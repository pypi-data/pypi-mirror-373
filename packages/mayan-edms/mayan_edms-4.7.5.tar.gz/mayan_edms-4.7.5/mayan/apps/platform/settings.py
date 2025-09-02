from django.utils.translation import gettext_lazy as _

from mayan.apps.smart_settings.settings import setting_cluster

from .literals import (
    DEFAULT_PLATFORM_CLIENT_BACKEND_ARGUMENTS,
    DEFAULT_PLATFORM_CLIENT_BACKEND_ENABLED
)

setting_namespace = setting_cluster.do_namespace_add(
    label=_(message='Platform'), name='platform'
)

setting_client_backend_enabled = setting_namespace.do_setting_add(
    default=DEFAULT_PLATFORM_CLIENT_BACKEND_ENABLED,
    global_name='PLATFORM_CLIENT_BACKEND_ENABLED', help_text=_(
        message='List of client backends to launch after startup. Use full dotted '
        'path to the client backend classes.'
    )
)
setting_client_backend_arguments = setting_namespace.do_setting_add(
    default=DEFAULT_PLATFORM_CLIENT_BACKEND_ARGUMENTS,
    global_name='PLATFORM_CLIENT_BACKEND_ARGUMENTS', help_text=_(
        message='Arguments for the client backends. Use the client backend dotted '
        'path as the dictionary key for the arguments in dictionary format.'
    )
)
