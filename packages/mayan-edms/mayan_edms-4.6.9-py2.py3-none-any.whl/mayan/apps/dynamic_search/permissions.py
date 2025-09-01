from django.utils.translation import gettext_lazy as _

from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_(message='Search'), name='search'
)

permission_search_tools = namespace.add_permission(
    label=_(message='Execute search tools'), name='search_tools'
)
