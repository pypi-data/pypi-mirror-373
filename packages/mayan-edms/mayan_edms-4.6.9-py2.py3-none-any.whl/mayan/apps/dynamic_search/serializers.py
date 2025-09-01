from django.utils.translation import gettext_lazy as _

from mayan.apps.rest_api import serializers


class DummySearchResultModelSerializer(serializers.Serializer):
    """
    Empty serializer for Swagger views.
    """


class SearchFieldSerializer(serializers.Serializer):
    field_name = serializers.CharField(
        label=_(message='Field name'), read_only=True
    )
    label = serializers.CharField(
        label=_(message='Label'), read_only=True
    )


class SearchModelSerializer(serializers.Serializer):
    app_label = serializers.CharField(
        label=_(message='App label'), read_only=True
    )
    model_name = serializers.CharField(
        label=_(message='Model name'), read_only=True
    )
    pk = serializers.CharField(
        label=_(message='Primary key'), read_only=True
    )
    search_fields = SearchFieldSerializer(
        label=_(message='Search fields'), many=True, read_only=True
    )
