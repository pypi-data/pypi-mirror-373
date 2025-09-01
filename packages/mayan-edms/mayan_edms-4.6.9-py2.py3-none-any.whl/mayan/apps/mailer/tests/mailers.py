from ..classes import MailerBackend


class MailingProfileTest(MailerBackend):
    """
    Mailing profile backend to use with tests.
    """
    class_path = 'django.core.mail.backends.locmem.EmailBackend'
    label = 'Django local memory backend'
