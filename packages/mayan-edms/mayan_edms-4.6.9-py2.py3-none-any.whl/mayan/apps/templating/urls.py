from django.urls import re_path

from .api_views import APITemplateDetailView, APITemplateListView

from .views import DocumentTemplateSandboxView

urlpatterns = [
    re_path(
        route=r'^documents/(?P<document_id>\d+)/sandbox/$',
        name='document_template_sandbox',
        view=DocumentTemplateSandboxView.as_view()
    )
]

api_urls = [
    re_path(
        route=r'^templates/$', view=APITemplateListView.as_view(),
        name='template-list'
    ),
    re_path(
        route=r'^templates/(?P<name>[-\w]+)/$',
        view=APITemplateDetailView.as_view(), name='template-detail'
    )
]
