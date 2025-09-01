from django.utils.translation import gettext_lazy as _

from .classes import ErrorLog as ErrorLogProxy


class ErrorLogPartitionEntryBusinessLogicMixin:
    def get_object(self):
        return self.error_log_partition.content_object

    get_object.short_description = _(message='Object')


class StoredErrorLogBusinessLogicMixin:
    @property
    def app_label(self):
        return self.proxy.app_config

    app_label.fget.short_description = _(message='App label')

    @property
    def proxy(self):
        return ErrorLogProxy.get(name=self.name)
