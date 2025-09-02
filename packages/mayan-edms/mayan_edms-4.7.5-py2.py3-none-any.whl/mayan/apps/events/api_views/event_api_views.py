from django.http import Http404

from actstream.models import Action, any_stream

from mayan.apps.rest_api import generics
from mayan.apps.rest_api.api_view_mixins import (
    ExternalContentTypeObjectAPIViewMixin
)

from ..classes import EventType, EventTypeNamespace
from ..permissions import permission_events_view
from ..serializers import (
    EventSerializer, EventTypeNamespaceSerializer, EventTypeSerializer
)


class APIObjectEventListView(
    ExternalContentTypeObjectAPIViewMixin, generics.ListAPIView
):
    """
    get: Return a list of events for the specified object.
    """
    mayan_external_object_permission_map = {'GET': permission_events_view}
    serializer_class = EventSerializer

    def get_source_queryset(self):
        return any_stream(
            obj=self.get_external_object()
        )


class APIEventTypeNamespaceDetailView(generics.RetrieveAPIView):
    """
    get: Returns the details of an event type namespace.
    """
    serializer_class = EventTypeNamespaceSerializer

    def get_object(self):
        try:
            return EventTypeNamespace.get(
                name=self.kwargs['name']
            )
        except KeyError:
            raise Http404


class APIEventTypeNamespaceListView(generics.ListAPIView):
    """
    get: Returns a list of all the available event type namespaces.
    """
    serializer_class = EventTypeNamespaceSerializer
    source_queryset = EventTypeNamespace.all()

    def get_serializer_context(self):
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }


class APIEventTypeNamespaceEventTypeListView(generics.ListAPIView):
    """
    get: Returns a list of all the available event types from a namespaces.
    """
    serializer_class = EventTypeSerializer

    def get_serializer_context(self):
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }

    def get_source_queryset(self):
        try:
            return EventTypeNamespace.get(
                name=self.kwargs['name']
            ).get_event_types()
        except KeyError:
            raise Http404


class APIEventTypeListView(generics.ListAPIView):
    """
    get: Returns a list of all the available event types.
    """
    serializer_class = EventTypeSerializer
    source_queryset = EventType.all()

    def get_serializer_context(self):
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }


class APIEventListView(generics.ListAPIView):
    """
    get: Returns a list of all the available events.
    """
    mayan_view_permission_map = {'GET': permission_events_view}
    serializer_class = EventSerializer
    source_queryset = Action.objects.all()

    def get_serializer_context(self):
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }
