import httpx
import logging
import os
import time

from types import MappingProxyType
from typing import (
    Annotated,
    Any,
    AsyncIterator,
    Dict,
    FrozenSet,
    List,
    Optional,
    Tuple,
    cast,
)

from fastapi import Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import ExpiredSignatureError, JOSEError, JWTError, JWSError, jwt
from jose.exceptions import JWTClaimsError

from .decorators import returns_errors


PublicKeys = Dict[str, List]
TokenPayload = Dict[str, Any]

logger = logging.getLogger(__file__)


# base URL of the OIDC provider
OIDC_BASE_URL = os.getenv(
    "OIDC_BASE_URL", "https://auth.delphai.com/auth/realms/delphai"
)

DEFAULT_AUDIENCE = "delphai-gateway"

OAuth2Token = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{OIDC_BASE_URL}/protocol/openid-connect/auth",
    tokenUrl=f"{OIDC_BASE_URL}/protocol/openid-connect/token",
    auto_error=False,
)


class TokenValidator:
    """
    Decodes tokens using public keys from trusted issuers
    """

    UPDATE_PUBLIC_KEYS_INTERVAL = 60

    def __init__(self) -> None:
        self._public_keys: Dict[str, PublicKeys] = {}
        self._public_keys_last_updated: Dict[str, float] = {}

        self.http_client = httpx.AsyncClient()

    async def decode_token(self, token: str, audience: Optional[str]) -> TokenPayload:
        """
        Updates public keys, validates token and decodes its content
        """
        unverified_data = self._decode_token(
            token=token,
            keys={},
            audience=audience,
            verify=False,
        )
        issuer = self._verify_issuer(unverified_data.get("iss"))

        issuer_public_keys = self._public_keys.get(issuer)
        if issuer_public_keys:
            # Try decode using cached keys
            try:
                return self._decode_token(
                    token=token,
                    keys=issuer_public_keys,
                    audience=audience,
                )
            except JWSError as error:
                if "Signature verification failed" in error.args[0]:
                    pass  # Update public keys and retry
                else:
                    raise

        issuer_public_keys = await self._update_keys(issuer)

        return self._decode_token(
            token=token,
            keys=issuer_public_keys,
            audience=audience,
        )

    def _decode_token(
        self, token: str, keys: PublicKeys, audience: Optional[str], verify: bool = True
    ) -> TokenPayload:
        """
        Decodes JWT and remaps `jose` errors
        """
        options = {"verify_signature": verify}

        if audience is None:
            options["verify_aud"] = False

        try:
            return jwt.decode(token, keys, audience=audience, options=options)
        except (ExpiredSignatureError, JWTClaimsError):
            raise
        except JWTError as error:
            if isinstance(error.args[0], Exception):
                # Unwrap low level error
                raise error.args[0]
            raise

    def _verify_issuer(self, issuer: Optional[str]) -> str:
        if not issuer:
            raise JWTClaimsError("Empty issuer")

        if issuer != OIDC_BASE_URL:
            raise JWTClaimsError("Invalid issuer")

        return issuer

    async def _update_keys(self, issuer: str) -> PublicKeys:
        """
        Updates public keys (not more often than `UPDATE_PUBLIC_KEYS_INTERVAL`)
        """
        last_updated = self._public_keys_last_updated.get(issuer)

        if not last_updated or self.UPDATE_PUBLIC_KEYS_INTERVAL < (
            time.monotonic() - last_updated
        ):
            response = await self.http_client.get(
                f"{issuer}/protocol/openid-connect/certs"
            )
            logger.debug(
                "Public keys for `%s` were fetched, status code: %s",
                issuer,
                response.status_code,
            )
            response.raise_for_status()
            public_keys = response.json()

            self._public_keys[issuer] = public_keys
            self._public_keys_last_updated[issuer] = time.monotonic()

        return self._public_keys[issuer]


class _Authorization:
    """
    Holds decoded JWT payload
    """

    token_validator = TokenValidator()

    @classmethod
    @returns_errors(
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )
    async def fastapi_dependency(
        cls, request: Request, token: Annotated[Optional[str], Depends(OAuth2Token)]
    ) -> AsyncIterator["_Authorization"]:
        """
        Decodes and validates authorization token
        """
        if token:
            pre_authorization = cls(request=request)
            if pre_authorization.is_direct_request:
                # We should not check `audience` for service-to-service calls
                # to allow all valid tokens to be used.
                audience = None
            else:
                # `audience` is only checked in first ("entrypoint") service
                audience = request.app.extra.get("oidc_audience", DEFAULT_AUDIENCE)

            try:
                token_payload = await cls.token_validator.decode_token(
                    token=token, audience=audience
                )
            except ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is expired",
                )
            except JOSEError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token verification failed",
                )

        else:
            token_payload = None

        authorization = cls(request=request, token=token, token_payload=token_payload)

        raise_unchecked = True
        try:
            yield authorization

        except (HTTPException, RequestValidationError):
            raise_unchecked = False
            raise

        finally:
            if os.getenv("ENFORCE_PERMISSIONS_CHECKED"):
                # Because of the `fastapi` issue the following check causes
                # unwanted behaviour now when input data validation is failed.
                # Now it could be useful to verify authentication during developing
                # but breaks other flows

                # Must not be enabled on production

                # Remove this if-block when/if `fastapi` will be fixed

                if raise_unchecked and not authorization.were_permissions_checked:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Token was not validated",
                    )

    def __init__(
        self,
        request: Request,
        token: Optional[str] = None,
        token_payload: Optional[TokenPayload] = None,
    ):
        self._were_permissions_checked = False

        self._request = request

        self._token = token
        self._token_payload = token_payload

        self._client_id = self._scopes = None
        self._user_id = self._user_email = self._user_name = None
        self._groups_chains = self._roles = None

        if token_payload:
            self._client_id = token_payload["azp"]
            self._scopes = frozenset(token_payload.get("scope", "").split())

            self._user_id = token_payload["sub"]
            self._user_email = token_payload.get("email")
            self._user_name = token_payload.get("name")
            self._mongo_user_id = token_payload.get("mongo_user_id")
            self._mongo_client_id = token_payload.get("mongo_client_id")
            self._preferred_currency = token_payload.get("preferred_currency")

            self._groups_chains = tuple(
                tuple(
                    MappingProxyType(cast(Dict[str, Any], group))
                    for group in groups_chain
                )
                for groups_chain in token_payload.get("groups", [])
            )

            self._roles = frozenset(
                token_payload.get("realm_access", {}).get("roles", [])
            )

    @property
    def were_permissions_checked(self) -> bool:
        return self._were_permissions_checked

    def require(self, value: bool) -> None:
        self._were_permissions_checked = True

        if not value:
            if self._token:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    @property
    def is_direct_request(self) -> bool:
        # If it does not come from an ingress reverse-proxy
        # then it's a direct (cluster local) request
        return not bool(self._request.headers.get("x-forwarded-for"))

    @property
    def is_authenticated(self) -> bool:
        return bool(self._token_payload)

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def token_payload(self) -> Optional[TokenPayload]:
        return self._token_payload

    @property
    def client_id(self) -> Optional[str]:
        return self._client_id

    @property
    def mongo_client_id(self) -> Optional[str]:
        return self._mongo_client_id

    @property
    def preferred_currency(self) -> Optional[str]:
        return self._preferred_currency

    @property
    def scopes(self) -> Optional[FrozenSet[str]]:
        return self._scopes

    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    @property
    def mongo_user_id(self) -> Optional[str]:
        return self._mongo_user_id

    @property
    def user_email(self) -> Optional[str]:
        return self._user_email

    @property
    def user_name(self) -> Optional[str]:
        return self._user_name

    @property
    def groups_chain(self) -> Optional[Tuple[MappingProxyType[str, Any], ...]]:
        if not self._groups_chains:
            return None

        # We usally have only one group per user
        # If that's not true, that's most likely a misconfiguration
        if len(self._groups_chains) != 1:
            logger.warning(
                "User %s has %d groups assigned, expected 1",
                self.user_id,
                len(self._groups_chains),
            )

        return self._groups_chains[0]

    @property
    def customer(self) -> Optional[MappingProxyType[str, Any]]:
        groups_chain = self.groups_chain
        if not groups_chain:
            return None

        # First (root) group in the chain represents customer
        return groups_chain[0]

    @property
    def customer_id(self) -> Optional[str]:
        customer = self.customer
        return customer["id"] if customer else None

    @property
    def customer_name(self) -> Optional[str]:
        customer = self.customer
        return customer["name"] if customer else None

    @property
    def department(self) -> Optional[MappingProxyType[str, Any]]:
        groups_chain = self.groups_chain
        if not groups_chain or len(groups_chain or []) < 2:
            return None

        # Last (leaf) non-root group in the chain represents department
        return groups_chain[-1]

    @property
    def department_id(self) -> Optional[str]:
        department = self.department
        return department["id"] if department else None

    @property
    def department_name(self) -> Optional[str]:
        department = self.department
        return department["name"] if department else None

    @property
    def roles(self) -> Optional[FrozenSet[str]]:
        return self._roles


Authorization = Annotated[_Authorization, Depends(_Authorization.fastapi_dependency)]
