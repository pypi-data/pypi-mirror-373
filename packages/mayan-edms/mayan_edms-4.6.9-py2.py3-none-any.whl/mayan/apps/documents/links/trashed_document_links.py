from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.classes import Link

from ..icons import (
    icon_document_trash_send, icon_trash_can_empty,
    icon_trashed_document_delete, icon_trashed_document_list,
    icon_trashed_document_restore
)
from ..permissions import (
    permission_document_trash, permission_trash_empty,
    permission_trashed_document_delete, permission_trashed_document_restore
)

link_document_delete = Link(
    args='resolved_object.id', icon=icon_trashed_document_delete,
    permission=permission_trashed_document_delete,
    tags='dangerous', text=_(message='Delete'), view='documents:document_delete'
)
link_document_trash = Link(
    args='resolved_object.id', icon=icon_document_trash_send,
    permission=permission_document_trash, tags='dangerous',
    text=_(message='Move to trash'), view='documents:document_trash'
)
link_document_list_deleted = Link(
    icon=icon_trashed_document_list, text=_(message='Trash can'),
    view='documents:document_list_deleted'
)
link_document_restore = Link(
    args='object.pk', icon=icon_trashed_document_restore,
    permission=permission_trashed_document_restore, text=_(message='Restore'),
    view='documents:document_restore'
)
link_document_multiple_trash = Link(
    icon=icon_document_trash_send, tags='dangerous',
    text=_(message='Move to trash'), view='documents:document_multiple_trash'
)
link_document_multiple_delete = Link(
    icon=icon_trashed_document_delete, tags='dangerous',
    text=_(message='Delete'), view='documents:document_multiple_delete'
)
link_document_multiple_restore = Link(
    icon=icon_trashed_document_restore, text=_(message='Restore'),
    view='documents:document_multiple_restore'
)
link_trash_can_empty = Link(
    icon=icon_trash_can_empty, permission=permission_trash_empty,
    text=_(message='Empty trash'), view='documents:trash_can_empty'
)
