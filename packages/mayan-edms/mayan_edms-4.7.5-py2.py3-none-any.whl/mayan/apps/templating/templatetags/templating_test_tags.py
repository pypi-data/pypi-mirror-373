from django.conf import settings
from django.template import Library

register = Library()


@register.simple_tag
def templating_test_tag():
    if settings.TESTING:
        # Hidden import.
        # Required to allow production package to work when tests are
        # removed.
        from ..tests.literals import TEST_TEMPLATE_TAG_RESULT

        return TEST_TEMPLATE_TAG_RESULT
