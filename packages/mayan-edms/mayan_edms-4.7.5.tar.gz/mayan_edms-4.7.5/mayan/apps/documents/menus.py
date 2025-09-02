from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.classes import Menu

from .icons import icon_menu_documents

menu_documents = Menu(
    icon=icon_menu_documents, label=_(message='Documents'),
    name='documents'
)
