from collections import deque
import functools

import elasticsearch
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search

from ...exceptions import (
    DynamicSearchBackendException, DynamicSearchValueTransformationError
)
from ...search_backends import SearchBackend
from ...search_fields import SearchFieldVirtualAllFields
from ...search_models import SearchModel

from .literals import (
    DEFAULT_ELASTICSEARCH_CLIENT_MAXSIZE,
    DEFAULT_ELASTICSEARCH_CLIENT_SNIFF_ON_CONNECTION_FAIL,
    DEFAULT_ELASTICSEARCH_CLIENT_SNIFF_ON_START,
    DEFAULT_ELASTICSEARCH_CLIENT_SNIFFER_TIMEOUT, DEFAULT_ELASTICSEARCH_HOST,
    DEFAULT_ELASTICSEARCH_CLIENT_VERIFY_CERTS,
    DEFAULT_ELASTICSEARCH_INDICES_NAMESPACE,
    DEFAULT_ELASTICSEARCH_SEARCH_PAGE_SIZE,
    DJANGO_TO_ELASTICSEARCH_FIELD_MAP, MAXIMUM_API_ATTEMPT_COUNT
)


class ElasticSearchBackend(SearchBackend):
    feature_reindex = True
    field_type_mapping = DJANGO_TO_ELASTICSEARCH_FIELD_MAP

    def __init__(
        self, client_http_auth=None, client_host=DEFAULT_ELASTICSEARCH_HOST,
        client_hosts=None,
        client_maxsize=DEFAULT_ELASTICSEARCH_CLIENT_MAXSIZE,
        client_port=None, client_scheme=None,
        client_sniff_on_connection_fail=DEFAULT_ELASTICSEARCH_CLIENT_SNIFF_ON_CONNECTION_FAIL,
        client_sniff_on_start=DEFAULT_ELASTICSEARCH_CLIENT_SNIFF_ON_START,
        client_sniffer_timeout=DEFAULT_ELASTICSEARCH_CLIENT_SNIFFER_TIMEOUT,
        client_verify_certs=DEFAULT_ELASTICSEARCH_CLIENT_VERIFY_CERTS,
        indices_namespace=DEFAULT_ELASTICSEARCH_INDICES_NAMESPACE,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.indices_namespace = indices_namespace

        self.client_kwargs = {
            'hosts': client_hosts or (client_host,),
            'http_auth': client_http_auth, 'maxsize': client_maxsize,
            'port': client_port, 'scheme': client_scheme,
            'sniff_on_start': client_sniff_on_start,
            'sniff_on_connection_fail': client_sniff_on_connection_fail,
            'sniffer_timeout': client_sniffer_timeout,
            'verify_certs': client_verify_certs
        }

        if self._test_mode:
            self.indices_namespace = 'mayan-test'

    def do_search_execute(self, index_name, search):
        point_in_time_keep_alive = '5m'

        client = self._get_client()

        point_in_time = client.open_point_in_time(
            index=index_name, keep_alive=point_in_time_keep_alive
        )

        search = search.extra(pit=point_in_time)
        search = search.extra(size=DEFAULT_ELASTICSEARCH_SEARCH_PAGE_SIZE)
        search = search.index()
        search = search.sort('_doc')
        search = search.source(False)

        search_after = 0

        try:
            while True:
                search = search.extra(
                    search_after=[search_after]
                )
                response = search.execute()

                if not len(response):
                    break

                for entry in response:
                    result_id = entry.meta.id
                    yield result_id

                search_after = response[-1].meta.sort[0]

            client.close_point_in_time(
                body={
                    'id': point_in_time['id']
                }
            )
        except elasticsearch.exceptions.NotFoundError as exception:
            raise DynamicSearchBackendException(
                'Index not found. Make sure the search engine '
                'was properly initialized or upgraded if '
                'it already existed.'
            ) from exception

    def _get_client(self):
        return Elasticsearch(**self.client_kwargs)

    def _get_index_name(self, search_model):
        return '{}-{}'.format(
            self.indices_namespace, search_model.model_name.lower()
        )

    @functools.cache
    def _get_search_model_index_mappings(self, search_model):
        mappings = {}

        field_map = self.get_resolved_field_type_map(
            search_model=search_model
        )
        for field_name, search_field_data in field_map.items():
            mappings[field_name] = {
                'type': search_field_data['field'].name
            }

            if 'analyzer' in search_field_data:
                mappings[field_name]['analyzer'] = search_field_data['analyzer']

        return mappings

    def _get_status(self):
        client = self._get_client()
        result = []

        title = 'Elastic Search search model indexing status'
        result.append(title)
        result.append(
            len(title) * '='
        )

        self.refresh()

        for search_model in SearchModel.all():
            index_name = self._get_index_name(search_model=search_model)
            try:
                index_stats = client.count(index=index_name)
            except elasticsearch.exceptions.NotFoundError:
                index_stats = {}

            count = index_stats.get('count', 'None')

            result.append(
                '{}: {}'.format(search_model.label, count)
            )

        return '\n'.join(result)

    def _initialize(self):
        self._update_mappings()

    def _search(
        self, search_field, query_type, value, is_quoted_value=False,
        is_raw_value=False
    ):
        self.do_query_type_verify(
            query_type=query_type, search_field=search_field
        )

        client = self._get_client()
        index_name = self._get_index_name(
            search_model=search_field.search_model
        )

        if isinstance(search_field, SearchFieldVirtualAllFields):
            for search_field in search_field.field_composition:
                try:
                    search_field_query = query_type.resolve_for_backend(
                        is_quoted_value=is_quoted_value,
                        is_raw_value=is_raw_value, search_backend=self,
                        search_field=search_field, value=value
                    )
                except DynamicSearchValueTransformationError:
                    """Skip the search field."""
                else:
                    if search_field_query is not None:

                        index_name = self._get_index_name(
                            search_model=search_field.search_model
                        )

                        search = Search(index=index_name, using=client)
                        search = search.filter(search_field_query)

                        result = self.do_search_execute(
                            index_name=index_name, search=search
                        )
                        yield from result
            else:
                return ()
        else:
            search = Search(index=index_name, using=client)

            try:
                search_field_query = query_type.resolve_for_backend(
                    is_quoted_value=is_quoted_value,
                    is_raw_value=is_raw_value, search_backend=self,
                    search_field=search_field, value=value
                )
            except DynamicSearchValueTransformationError:
                return ()
            else:
                if search_field_query is None:
                    return ()
                else:
                    search = search.filter(search_field_query)

                    yield from self.do_search_execute(
                        index_name=index_name, search=search
                    )

    def _update_mappings(self, search_model=None):
        client = self._get_client()

        if search_model:
            search_models = (search_model,)
        else:
            search_models = SearchModel.all()

        for search_model in search_models:
            index_name = self._get_index_name(search_model=search_model)

            mappings = self._get_search_model_index_mappings(
                search_model=search_model
            )

            try:
                client.indices.delete(index=index_name)
            except elasticsearch.exceptions.NotFoundError:
                """
                Non fatal, might be that this is the first time
                the method is executed. Proceed.
                """

            try:
                client.indices.create(
                    index=index_name,
                    body={
                        'mappings': {
                            'properties': mappings
                        }
                    }
                )
            except elasticsearch.exceptions.RequestError:
                try:
                    client.indices.put_mapping(
                        index=index_name,
                        body={
                            'properties': mappings
                        }
                    )
                except elasticsearch.exceptions.RequestError:
                    """
                    There are mapping changes that were not allowed.
                    Example: Text to Keyword.
                    Boot up regardless and allow user to reindex to delete
                    old indices.
                    """

    def deindex_instance(self, instance):
        search_model = SearchModel.get_for_model(instance=instance)
        client = self._get_client()
        client.delete(
            id=instance.pk,
            index=self._get_index_name(search_model=search_model)
        )

    def index_instance(
        self, instance, exclude_model=None, exclude_kwargs=None
    ):
        search_model = SearchModel.get_for_model(instance=instance)

        document = search_model.populate(
            exclude_kwargs=exclude_kwargs, exclude_model=exclude_model,
            instance=instance, search_backend=self
        )
        self._get_client().index(
            index=self._get_index_name(search_model=search_model),
            id=instance.pk, document=document
        )

    def index_instances(self, search_model, id_list):
        client = self._get_client()
        index_name = self._get_index_name(search_model=search_model)

        def generate_actions():
            queryset = search_model.get_queryset()

            queryset = queryset.filter(pk__in=id_list)

            for instance in queryset:
                kwargs = search_model.populate(
                    search_backend=self, instance=instance
                )
                kwargs['_id'] = kwargs['id']

                yield kwargs

        bulk_indexing_generator = helpers.streaming_bulk(
            actions=generate_actions(), client=client, index=index_name,
            yield_ok=False
        )

        deque(iterable=bulk_indexing_generator, maxlen=0)

    def refresh(self):
        attempt_count = 0
        client = self._get_client()
        search_model_index = 0
        search_models = SearchModel.all()

        while True:
            search_model = search_models[search_model_index]
            index_name = self._get_index_name(search_model=search_model)

            try:
                client.indices.refresh(index=index_name)
            except elasticsearch.exceptions.NotFoundError as exception:
                attempt_count += 1

                if attempt_count > MAXIMUM_API_ATTEMPT_COUNT:
                    raise DynamicSearchBackendException(
                        'Refresh attempt count exceeded the maximum'
                        ' of `{}`.'.format(
                            MAXIMUM_API_ATTEMPT_COUNT
                        )
                    ) from exception
            else:
                attempt_count = 0
                search_model_index += 1
                if search_model_index >= len(search_models):
                    break

    def reset(self, search_model=None):
        self.tear_down(search_model=search_model)
        self._update_mappings(search_model=search_model)

    def tear_down(self, search_model=None):
        client = self._get_client()

        if search_model:
            search_models = (search_model,)
        else:
            search_models = SearchModel.all()

        for search_model in search_models:
            try:
                client.indices.delete(
                    index=self._get_index_name(search_model=search_model)
                )
            except elasticsearch.exceptions.NotFoundError:
                """Ignore non existent indexes."""
