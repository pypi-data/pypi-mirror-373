from .literals import URL_QUERY_POSITIVE_VALUES


def is_url_query_positive(value):
    if value is not None:
        return value.lower() in URL_QUERY_POSITIVE_VALUES
