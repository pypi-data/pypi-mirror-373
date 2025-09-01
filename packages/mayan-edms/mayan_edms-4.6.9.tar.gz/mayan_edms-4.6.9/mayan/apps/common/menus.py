from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.classes import Menu

from .icons import icon_menu_about, icon_menu_user

menu_about = Menu(
    icon=icon_menu_about, label=_(message='System'), name='about'
)
menu_facet = Menu(label=_(message='Facet'), name='facet')
menu_list_facet = Menu(label=_(message='Facet'), name='list facet')
menu_main = Menu(name='main')
menu_multi_item = Menu(name='multi item')
menu_object = Menu(label=_(message='Actions'), name='object')
menu_related = Menu(label=_(message='Related'), name='related')
menu_secondary = Menu(label=_(message='Secondary'), name='secondary')
menu_setup = Menu(name='setup')
menu_return = Menu(label=_(message='Return'), name='return')
menu_tools = Menu(name='tools')
menu_topbar = Menu(name='topbar')
menu_user = Menu(
    icon=icon_menu_user, name='user', label=_(message='User')
)
