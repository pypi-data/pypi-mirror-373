from django.utils.translation import gettext_lazy as _

from mayan.apps.smart_settings.settings import setting_cluster

from .literals import DEFAULT_EVENTS_DISABLE_ASYNCHRONOUS_MODE

setting_namespace = setting_cluster.do_namespace_add(
    label=_(message='Events'), name='events'
)

setting_disable_asynchronous_mode = setting_namespace.do_setting_add(
    default=DEFAULT_EVENTS_DISABLE_ASYNCHRONOUS_MODE,
    global_name='EVENTS_DISABLE_ASYNCHRONOUS_MODE',
    help_text=_(
        message='Disables asynchronous events mode. All events will be committed '
        'in the same process that triggers them. This was the behavior '
        'prior to version 4.5.'
    )
)
