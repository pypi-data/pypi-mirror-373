from django.utils.translation import gettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import (
    menu_facet, menu_list_facet, menu_object, menu_return, menu_secondary,
    menu_tools
)
from mayan.apps.common.signals import (
    signal_post_initial_setup, signal_post_upgrade
)
from mayan.apps.navigation.classes import SourceColumn

from .handlers import (
    handler_search_backend_initialize, handler_search_backend_upgrade
)
from .links import (
    link_saved_resultset_delete_single, link_saved_resultset_list,
    link_search, link_saved_resultset_result_list, link_search_advanced,
    link_search_again, link_search_backend_reindex
)
from .permissions import (
    permission_saved_resultset_delete, permission_saved_resultset_view
)
from .search_backends import SearchBackend
from .search_models import SearchModel


class DynamicSearchApp(MayanAppConfig):
    app_namespace = 'search'
    app_url = 'search'
    has_rest_api = True
    has_static_media = True
    has_tests = True
    name = 'mayan.apps.dynamic_search'
    verbose_name = _(message='Dynamic search')

    def ready(self):
        super().ready()

        SearchModel.load_modules()
        SearchBackend._enable()

        SavedResultset = self.get_model(model_name='SavedResultset')

        ModelPermission.register(
            model=SavedResultset,
            permissions=(
                permission_saved_resultset_delete,
                permission_saved_resultset_view,
            )
        )

        SourceColumn(
            attribute='timestamp', is_identifier=True, is_sortable=True,
            source=SavedResultset
        )
        SourceColumn(
            attribute='user', include_label=True, is_sortable=True,
            source=SavedResultset
        )
        SourceColumn(
            attribute='app_label', include_label=True, source=SavedResultset
        )
        SourceColumn(
            attribute='model_name', include_label=True, source=SavedResultset
        )
        SourceColumn(
            attribute='result_count', include_label=True,
            source=SavedResultset
        )
        SourceColumn(
            attribute='search_explainer_text', include_label=True,
            source=SavedResultset
        )

        SourceColumn(
            attribute='time_to_live', include_label=True, source=SavedResultset
        )

        menu_facet.bind_links(
            links=(link_search, link_search_advanced),
            sources=(
                'search:search_simple', 'search:search_advanced',
                'search:search_results'
            )
        )
        menu_object.bind_links(
            links=(link_saved_resultset_delete_single,),
            sources=(SavedResultset,)
        )
        menu_list_facet.bind_links(
            links=(link_saved_resultset_result_list,),
            sources=(SavedResultset,)
        )
        menu_secondary.bind_links(
            links=(link_search_again,), sources=('search:search_results',)
        )
        menu_return.bind_links(
            links=(link_saved_resultset_list,), sources=(SavedResultset,)
        )
        menu_tools.bind_links(
            links=(link_saved_resultset_list, link_search_backend_reindex,),
        )

        signal_post_initial_setup.connect(
            dispatch_uid='search_handler_search_backend_initialize',
            receiver=handler_search_backend_initialize
        )

        signal_post_upgrade.connect(
            dispatch_uid='search_handler_search_backend_upgrade',
            receiver=handler_search_backend_upgrade
        )
