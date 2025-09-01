from django.template import Library

from ..settings import setting_cluster

register = Library()


@register.simple_tag
def smart_setting(global_name):
    return setting_cluster.get_setting(global_name=global_name).value


@register.simple_tag
def smart_settings_check_changed():
    return setting_cluster.get_is_changed()
