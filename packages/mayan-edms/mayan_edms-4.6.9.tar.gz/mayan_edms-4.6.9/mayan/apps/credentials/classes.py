from django.utils.translation import gettext_lazy as _

from mayan.apps.backends.classes import DynamicFormModelBackend


class CredentialBackend(DynamicFormModelBackend):
    _backend_app_label = 'credentials'
    _backend_model_name = 'StoredCredential'
    _loader_module_name = 'credential_backends'

    form_fieldsets = (
        (
            _(message='General'), {
                'fields': ('label', 'internal_name')
            }
        ),
    )


# Null backend must be defined here to avoid automatic import.
class CredentialBackendNull(CredentialBackend):
    label = _(message='Null backend')
