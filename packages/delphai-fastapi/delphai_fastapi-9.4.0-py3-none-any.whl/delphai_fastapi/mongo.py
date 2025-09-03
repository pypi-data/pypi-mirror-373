OPERATORS_MAP = {
    "ne": "$ne",
    "lt": "$lt",
    "gt": "$gt",
    "lte": "$lte",
    "gte": "$gte",
    "": "$eq",
}


def make_mongo_query(**fields):
    """
    Receives an objects with fields and generates a mongo match query.
    """
    match_queries = {}

    for field_name, field_value in fields.items():
        if field_value is None:
            continue
        elif isinstance(field_value, dict):
            if not field_value:
                continue
            match_queries[field_name] = {
                OPERATORS_MAP[operator]: subvalue
                for operator, subvalue in field_value.items()
            }
        else:
            match_queries[field_name] = field_value

    return match_queries
