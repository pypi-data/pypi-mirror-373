from .models import HTTPExceptionModel


def returns_errors(*error_codes):
    responses = {
        str(error_code): {"model": HTTPExceptionModel} for error_code in error_codes
    }

    def decorator(func):
        original_responses = getattr(func, "responses", {})
        func.responses = dict(original_responses, **responses)
        return func

    return decorator
