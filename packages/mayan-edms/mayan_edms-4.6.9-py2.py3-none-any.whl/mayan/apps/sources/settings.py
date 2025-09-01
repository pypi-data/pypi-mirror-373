from django.utils.translation import gettext_lazy as _

from mayan.apps.smart_settings.settings import setting_cluster

from .literals import (
    DEFAULT_SOURCES_BACKEND_ARGUMENTS, DEFAULT_SOURCES_CACHE_STORAGE_BACKEND,
    DEFAULT_SOURCES_CACHE_STORAGE_BACKEND_ARGUMENTS
)
from .setting_migrations import SourcesSettingMigration

setting_namespace = setting_cluster.do_namespace_add(
    label=_(message='Sources'), migration_class=SourcesSettingMigration,
    name='sources', version='0003'
)

setting_backend_arguments = setting_namespace.do_setting_add(
    default=DEFAULT_SOURCES_BACKEND_ARGUMENTS,
    global_name='SOURCES_BACKEND_ARGUMENTS', help_text=_(
        'Arguments to use when creating source backends.'
    )
)
setting_source_cache_storage_backend = setting_namespace.do_setting_add(
    global_name='SOURCES_CACHE_STORAGE_BACKEND',
    default=DEFAULT_SOURCES_CACHE_STORAGE_BACKEND, help_text=_(
        'Path to the Storage subclass used to store cached '
        'source image files.'
    )
)
setting_source_cache_storage_backend_arguments = setting_namespace.do_setting_add(
    global_name='SOURCES_CACHE_STORAGE_BACKEND_ARGUMENTS',
    default=DEFAULT_SOURCES_CACHE_STORAGE_BACKEND_ARGUMENTS,
    help_text=_(
        'Arguments to pass to the SOURCES_SOURCE_CACHE_STORAGE_BACKEND.'
    )
)
