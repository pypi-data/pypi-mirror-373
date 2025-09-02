from django.utils.translation import gettext_lazy as _

from mayan.apps.authentication.link_conditions import (
    condition_user_is_authenticated
)
from mayan.apps.navigation.classes import Link
from mayan.apps.navigation.utils import factory_condition_queryset_access

from .icons import (
    icon_ajax_refresh, icon_theme_create, icon_theme_delete, icon_theme_edit,
    icon_theme_list, icon_theme_setup, icon_user_theme_settings_detail,
    icon_user_theme_settings_edit
)
from .permissions import (
    permission_theme_create, permission_theme_delete, permission_theme_edit,
    permission_theme_view
)

link_ajax_refresh = Link(
    icon=icon_ajax_refresh, html_extra_classes='appearance-link-ajax-refresh'
)

link_user_theme_settings_detail = Link(
    args='object.pk',
    icon=icon_user_theme_settings_detail,
    text=_(message='Theme settings'),
    view='appearance:user_theme_settings_detail'
)
link_user_theme_settings_edit = Link(
    args='object.pk',
    condition=condition_user_is_authenticated,
    icon=icon_user_theme_settings_edit,
    text=_(message='Edit theme settings'),
    view='appearance:user_theme_settings_edit'
)

link_theme_create = Link(
    icon=icon_theme_create, permission=permission_theme_create,
    text=_(message='Create new theme'), view='appearance:theme_create'
)
link_theme_delete = Link(
    args='object.pk', icon=icon_theme_delete,
    permission=permission_theme_delete, tags='dangerous',
    text=_(message='Delete'), view='appearance:theme_delete'
)
link_theme_edit = Link(
    args='object.pk', icon=icon_theme_edit,
    permission=permission_theme_edit, text=_(message='Edit'),
    view='appearance:theme_edit'
)
link_theme_list = Link(
    icon=icon_theme_list, text=_(message='Themes'),
    view='appearance:theme_list'
)
link_theme_setup = Link(
    condition=factory_condition_queryset_access(
        app_label='appearance', model_name='Theme',
        object_permission=permission_theme_view,
        view_permission=permission_theme_create,
    ), icon=icon_theme_setup, text=_(message='Themes'),
    view='appearance:theme_list'
)
