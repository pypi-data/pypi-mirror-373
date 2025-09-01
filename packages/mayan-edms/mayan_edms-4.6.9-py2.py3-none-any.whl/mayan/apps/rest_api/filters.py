from rest_framework.filters import BaseFilterBackend, OrderingFilter

from mayan.apps.acls.models import AccessControlList


class MayanObjectPermissionsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        permission = self.get_mayan_object_permission(
            request=request, view=view
        )

        if permission:
            return AccessControlList.objects.restrict_queryset(
                queryset=queryset, permission=permission,
                user=request.user
            )
        else:
            return queryset

    def get_mayan_object_permission(self, request, view):
        try:
            method_get_mayan_object_permission = getattr(
                view, 'get_mayan_object_permission_map'
            )
        except AttributeError:
            mayan_object_permission_map = getattr(
                view, 'mayan_object_permission_map', {}
            )

            permission = mayan_object_permission_map.get(
                request.method, None
            )

            return permission
        else:
            return method_get_mayan_object_permission()


class MayanSortingFilter(OrderingFilter):
    ordering_param = '_ordering'

    def get_default_valid_fields(self, queryset, view, context=None):
        return ()
