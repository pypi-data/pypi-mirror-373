from django.utils.translation import gettext_lazy as _

from mayan.apps.rest_api import serializers


class AJAXTemplateSerializer(serializers.Serializer):
    hex_hash = serializers.CharField(
        label=_(message='Hex hash'), read_only=True
    )
    name = serializers.CharField(
        label=_(message='Name'), read_only=True
    )
    html = serializers.CharField(
        label=_(message='HTML'), read_only=True
    )
    url = serializers.HyperlinkedIdentityField(
        label=_(message='URL'), lookup_field='name', lookup_url_kwarg='name',
        view_name='rest_api:template-detail'
    )
