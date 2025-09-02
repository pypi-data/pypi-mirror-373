import elasticsearch_dsl
from elasticsearch_dsl import Q

from ...search_query_types import (
    BackendQueryType, QueryTypeExact, QueryTypeFuzzy, QueryTypeGreaterThan,
    QueryTypeGreaterThanOrEqual, QueryTypeLessThan, QueryTypeLessThanOrEqual,
    QueryTypePartial, QueryTypeRange, QueryTypeRangeExclusive,
    QueryTypeRegularExpression
)

from .backend import ElasticSearchBackend


class BackendQueryTypeExact(BackendQueryType):
    query_type = QueryTypeExact

    def do_resolve(self):
        if self.value is not None:
            if self.is_quoted_value:
                template = '"{}"'
            else:
                template = '{}'

            if not self.value:
                # Empty values cannot be quoted.
                template = '{}'

                if self.is_quoted_value:
                    if self.get_search_backend_field_type() == elasticsearch_dsl.field.Text:
                        return Q(
                            'bool', must_not=(
                                Q(
                                    'wildcard',
                                    **{self.search_field.field_name: '*'}
                                )
                            )
                        )

            if self.is_quoted_value:
                return Q(
                    name_or_query='match_phrase', _expand__to_dot=False,
                    **{
                        self.search_field.field_name: template.format(self.value)
                    }
                )
            else:
                return Q(
                    name_or_query='match', _expand__to_dot=False,
                    **{
                        self.search_field.field_name: template.format(self.value)
                    }
                )


class BackendQueryFuzzy(BackendQueryType):
    query_type = QueryTypeFuzzy

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='fuzzy', _expand__to_dot=False,
                **{self.search_field.field_name: self.value}
            )


class BackendQueryTypeGreaterThan(BackendQueryType):
    query_type = QueryTypeGreaterThan

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{
                    self.search_field.field_name: {'gt': self.value}
                }
            )


class BackendQueryTypeGreaterThanOrEqual(BackendQueryType):
    query_type = QueryTypeGreaterThanOrEqual

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{
                    self.search_field.field_name: {'gte': self.value}
                }
            )


class BackendQueryTypeLessThan(BackendQueryType):
    query_type = QueryTypeLessThan

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{
                    self.search_field.field_name: {'lt': self.value}
                }
            )


class BackendQueryTypeLessThanOrEqual(BackendQueryType):
    query_type = QueryTypeLessThanOrEqual

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{
                    self.search_field.field_name: {'lte': self.value}
                }
            )


class BackendQueryTypePartial(BackendQueryType):
    query_type = QueryTypePartial

    def do_resolve(self):
        if self.value is not None:
            if self.get_search_backend_field_type() != elasticsearch_dsl.field.Date:
                if self.is_quoted_value:
                    return Q(
                        name_or_query='match_phrase', _expand__to_dot=False,
                        **{
                            self.search_field.field_name: '{}'.format(self.value)
                        }
                    )
                else:
                    if self.get_search_backend_field_type() != elasticsearch_dsl.field.Integer:
                        return Q(
                            name_or_query='wildcard', _expand__to_dot=False,
                            **{
                                self.search_field.field_name: '*{}*'.format(self.value)
                            }
                        )


class BackendQueryTypeRange(BackendQueryType):
    query_type = QueryTypeRange

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{
                    self.search_field.field_name: {
                        'gte': self.value[0], 'lte': self.value[1]
                    }
                }
            )


class BackendQueryTypeRangeExclusive(BackendQueryType):
    query_type = QueryTypeRangeExclusive

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='range', _expand__to_dot=False,
                **{
                    self.search_field.field_name: {
                        'gt': self.value[0], 'lt': self.value[1]
                    }
                }
            )


class BackendQueryTypeRegularExpression(BackendQueryType):
    query_type = QueryTypeRegularExpression

    def do_resolve(self):
        if self.value is not None:
            return Q(
                name_or_query='regexp', _expand__to_dot=False,
                **{self.search_field.field_name: self.value}
            )


BackendQueryType.register(
    klass=BackendQueryTypeExact, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryFuzzy, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeGreaterThan, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeGreaterThanOrEqual,
    search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeLessThan, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeLessThanOrEqual,
    search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypePartial, search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeRange,
    search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeRangeExclusive,
    search_backend=ElasticSearchBackend
)
BackendQueryType.register(
    klass=BackendQueryTypeRegularExpression,
    search_backend=ElasticSearchBackend
)
