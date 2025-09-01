from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.classes import Menu

menu_sources = Menu(
    label=_(message='Sources'), name='sources'
)
