from django.utils.translation import gettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.backends.class_mixins import DynamicFormBackendMixin
from mayan.apps.backends.classes import ModelBaseBackend
from mayan.apps.credentials.class_mixins import BackendMixinCredentials
from mayan.apps.events.classes import EventModelRegistry

from .exceptions import MailerError


class MailerBackend(DynamicFormBackendMixin, ModelBaseBackend):
    """
    Base class for the mailing backends. This class is mainly a wrapper
    for other Django backends that adds a few metadata to specify the
    fields it needs to be instantiated at runtime.
    """
    _backend_app_label = 'mailer'
    _backend_model_name = 'UserMailer'
    _loader_module_name = 'mailers'
    class_path = ''  # Dot path to the actual class that will handle the mail.

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = (
            (
                _(message='General'), {
                    'fields': ('label', 'enabled', 'default')
                }
            ),
        )

        return fieldsets

    def get_connection_kwargs(self):
        result = {}

        return result


class MailerBackendBaseEmail(MailerBackend):
    class_path = None
    form_fields = {
        'from': {
            'label': _(message='From'),
            'class': 'django.forms.CharField', 'default': '',
            'help_text': _(
                message='The sender\'s address. Some system will refuse '
                'to send messages if this value is not set.'
            ), 'kwargs': {
                'max_length': 48
            }, 'required': False
        }
    }
    label = None

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _(message='Compatibility'), {
                    'fields': ('from',)
                }
            ),
        )

        return fieldsets

    def get_connection_kwargs(self):
        result = super().get_connection_kwargs()

        result['from'] = self.kwargs.get('from')

        return result


class MailerBackendCredentials(
    BackendMixinCredentials, MailerBackendBaseEmail
):
    label = _('Null backend')

    def get_connection_kwargs(self):
        result = super().get_connection_kwargs()

        credential = self.get_credential()

        password = credential.get('password')
        username = credential['username']

        result.update(
            {
                'password': password, 'username': username
            }
        )

        return result


class MailerBackendNull(MailerBackend):
    label = _(message='Null backend')


class ModelMailingAction:
    _registry = {}
    arguments = ('manager_name', 'permission',)
    as_attachment = False
    name = None

    @classmethod
    def get_action_for_model(cls, model, action_name):
        try:
            model_actions = cls._registry[model]
        except KeyError:
            raise MailerError(
                'Model `{}` is not registered for emailing.'.format(model)
            )
        else:
            try:
                return model_actions[action_name]
            except KeyError:
                raise MailerError(
                    'Model `{}` is not registered for emailing action '
                    '`{}`.'.format(model, action_name)
                )

    def __init__(self, model, **kwargs):
        self.kwargs = {}

        arguments = self.get_arguments()

        for argument in arguments:
            try:
                value = kwargs.pop(argument)
            except KeyError:
                raise MailerError(
                    'Error registering mailer action `{}` for model `{}`. '
                    'Missing argument `{}`.'.format(
                        self.name, model, argument
                    )
                )

            self.kwargs[argument] = value

        if kwargs:
            raise MailerError(
                'Error registering mailer action `{}` for model `{}`. '
                'Too many keyword arguments `{}`.'.format(
                    self.name, model, kwargs
                )
            )

        self.__class__._registry.setdefault(
            model, {}
        )

        self.__class__._registry[model][self.name] = self

        EventModelRegistry.register(model=model)

        ModelPermission.register(
            model=model, permissions=(
                self.kwargs['permission'],
            )
        )

    def get_arguments(self):
        return self.arguments


class ModelMailingActionAttachment(ModelMailingAction):
    as_attachment = True
    name = 'attachment'

    def get_arguments(self):
        arguments = super().get_arguments()

        arguments += (
            (
                'content_function_dotted_path',
                'mime_type_function_dotted_path'
            )
        )

        return arguments


class ModelMailingActionLink(ModelMailingAction):
    name = 'link'
