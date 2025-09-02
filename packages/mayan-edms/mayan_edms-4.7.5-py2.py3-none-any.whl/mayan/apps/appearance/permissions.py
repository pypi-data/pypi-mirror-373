from django.utils.translation import gettext_lazy as _

from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_(message='Appearance'), name='appearance'
)

permission_theme_create = namespace.add_permission(
    label=_(message='Create new themes'), name='theme_create'
)
permission_theme_delete = namespace.add_permission(
    label=_(message='Delete themes'), name='theme_delete'
)
permission_theme_edit = namespace.add_permission(
    label=_(message='Edit themes'), name='theme_edit'
)
permission_theme_view = namespace.add_permission(
    label=_(message='View existing themes'), name='theme_view'
)
