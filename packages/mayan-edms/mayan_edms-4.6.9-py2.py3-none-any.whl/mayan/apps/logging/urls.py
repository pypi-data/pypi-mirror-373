from django.urls import re_path

from .api_views import (
    APIErrorLogPartitionEntryDetailView, APIErrorLogPartitionEntryListView
)
from .views import (
    GlobalErrorLogEntryList, ObjectErrorLogEntryDeleteView,
    ObjectErrorLogEntryListClearView, ObjectErrorLogEntryListView
)

urlpatterns = [
    re_path(
        route=r'^object/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<object_id>\d+)/errors/$',
        name='object_error_log_entry_list', view=ObjectErrorLogEntryListView.as_view()
    ),
    re_path(
        route=r'^object/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<object_id>\d+)/errors/clear/$',
        name='object_error_log_entry_list_clear',
        view=ObjectErrorLogEntryListClearView.as_view()
    ),
    re_path(
        route=r'^object/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<object_id>\d+)/errors/(?P<error_log_partition_entry_id>\d+)/delete/$',
        name='object_error_log_entry_delete',
        view=ObjectErrorLogEntryDeleteView.as_view()
    ),
    re_path(
        route=r'^error_logs/partitions/entries/$',
        name='global_error_log_partition_entry_list',
        view=GlobalErrorLogEntryList.as_view()
    )
]

api_urls = [
    re_path(
        route=r'^objects/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<object_id>\d+)/errors/$',
        name='errorlogpartitionentry-list',
        view=APIErrorLogPartitionEntryListView.as_view()
    ),
    re_path(
        route=r'^objects/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<object_id>\d+)/errors/(?P<error_log_partition_entry_id>\d+)/$',
        name='errorlogpartitionentry-detail',
        view=APIErrorLogPartitionEntryDetailView.as_view()
    )
]
