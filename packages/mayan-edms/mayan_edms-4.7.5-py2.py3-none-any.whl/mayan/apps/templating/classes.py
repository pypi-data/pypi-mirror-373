import functools
import hashlib

from django.core.exceptions import ImproperlyConfigured
from django.template.response import TemplateResponse
from django.template.utils import EngineHandler
from django.urls import reverse


class AJAXTemplate:
    _registry = {}

    @classmethod
    def all(cls, rendered=False, request=None):
        if not rendered:
            return cls._registry.values()
        else:
            result = []
            for template in cls._registry.values():
                result.append(
                    template.render(request=request)
                )
            return result

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, name, template_name, context=None):
        self.context = context or None
        self.name = name
        self.template_name = template_name
        self.__class__._registry[name] = self

    def get_absolute_url(self):
        return reverse(
            kwargs={'name': self.name}, viewname='rest_api:template-detail'
        )

    def render(self, request):
        result = TemplateResponse(
            context=self.context, request=request,
            template=self.template_name
        ).render()

        # Calculate the hash of the bytes version but return the unicode
        # version.
        self.html = result.rendered_content.replace('\n', '')
        self.hex_hash = hashlib.sha256(string=result.content).hexdigest()
        return self


class Template:
    @classmethod
    @functools.cache
    def get_backend(cls):
        engine_handler = EngineHandler(
            templates=(
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'OPTIONS': {
                        'builtins': [
                            'mathfilters.templatetags.mathfilters',
                            'mayan.apps.templating.templatetags.templating_tags'
                        ]
                    }
                },
            )
        )
        return engine_handler['django']

    def __init__(self, template_string, context_entry_name_list=None):
        self._template_backend = Template.get_backend()
        self.context_entry_name_list = context_entry_name_list or ()

        self._template = self._template_backend.from_string(
            template_code=template_string
        )

    def render(self, context=None):
        final_context = {}

        entries_context = TemplateContextEntry.get_as_context(
            entry_name_list=self.context_entry_name_list
        )
        final_context.update(entries_context)

        if context:
            final_context.update(context)

        return self._template.render(context=final_context)


class TemplateContextEntry:
    _registry = {}
    _registry_always_available = []

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_as_context(cls, entry_name_list):
        result = {}

        for entry_name in cls._registry_always_available:
            entry = cls.get(name=entry_name)
            result[entry.name] = entry.get_value()

        for entry_name in entry_name_list:
            entry = cls.get(name=entry_name)
            result[entry.name] = entry.get_value()

        return result

    @classmethod
    def get_as_help_text(cls, entry_name_list):
        result = []

        for entry_name in cls._registry_always_available:
            entry = cls.get(name=entry_name)
            help_text = entry.get_help_text()
            result.append(help_text)

        for entry_name in entry_name_list:
            entry = cls.get(name=entry_name)
            help_text = entry.get_help_text()
            result.append(help_text)

        return ', '.join(result)

    def __init__(self, description, name, value, always_available=False):
        self.always_available = always_available
        self.description = description
        self.name = name
        self.value = value

        if name in self.__class__._registry:
            raise ImproperlyConfigured(
                '{} entry `{}` already registered. Check spelling or change '
                'the name'.format(self.__class__, self.name)
            )

        self.__class__._registry[self.name] = self

        if always_available:
            self.__class__._registry_always_available.append(self.name)

    def get_help_text(self):
        return '{{{{ {name} }}}} - {description}'.format(
            name=self.name, description=self.description
        )

    def get_value(self):
        try:
            return self.value()
        except TypeError:
            return self.value
