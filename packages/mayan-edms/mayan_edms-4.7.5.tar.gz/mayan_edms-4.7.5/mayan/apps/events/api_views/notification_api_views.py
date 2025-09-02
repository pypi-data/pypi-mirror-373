from mayan.apps.rest_api import generics

from ..models import Notification
from ..serializers import NotificationSerializer


class APINotificationDetailView(generics.RetrieveUpdateAPIView):
    """
    get: Return the details of the selected notification.
    patch: Edit the selected notification.
    put: Edit the selected notification.
    """
    lookup_url_kwarg = 'notification_id'
    serializer_class = NotificationSerializer

    def get_source_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Notification.objects.filter(user=self.request.user)
        else:
            queryset = Notification.objects.none()

        return queryset


class APINotificationListView(generics.ListAPIView):
    """
    get: Return a list of notifications for the current user.
    """
    serializer_class = NotificationSerializer

    def get_source_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Notification.objects.filter(user=self.request.user)
        else:
            queryset = Notification.objects.none()

        return queryset
