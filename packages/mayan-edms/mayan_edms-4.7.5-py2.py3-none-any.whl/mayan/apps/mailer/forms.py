from django import forms
from django.utils.translation import gettext_lazy as _

import mayan
from mayan.apps.acls.models import AccessControlList
from mayan.apps.backends.forms import FormDynamicModelBackend

from .classes import MailerBackend
from .models import UserMailer
from .permissions import permission_mailing_profile_use
from .settings import (
    setting_attachment_body_template, setting_attachment_subject_template,
    setting_document_link_body_template,
    setting_document_link_subject_template
)
from .validators import validate_email_multiple


class ObjectMailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        as_attachment = kwargs.pop('as_attachment', False)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if as_attachment:
            self.fields[
                'subject'
            ].initial = setting_attachment_subject_template.value

            self.fields[
                'body'
            ].initial = setting_attachment_body_template.value % {
                'project_title': mayan.__title__,
                'project_website': mayan.__website__
            }
        else:
            self.fields[
                'subject'
            ].initial = setting_document_link_subject_template.value
            self.fields['body'].initial = setting_document_link_body_template.value % {
                'project_title': mayan.__title__,
                'project_website': mayan.__website__
            }

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_mailing_profile_use,
            queryset=UserMailer.objects.filter(enabled=True), user=user
        )

        self.fields['mailing_profile'].queryset = queryset
        try:
            self.fields['mailing_profile'].initial = queryset.get(
                default=True
            )
        except UserMailer.DoesNotExist:
            pass

    email = forms.CharField(
        help_text=_(
            message='Email address of the recipient. Can be multiple '
            'addresses separated by comma or semicolon.'
        ), label=_(message='Email address'), validators=[
            validate_email_multiple
        ]
    )
    subject = forms.CharField(
        label=_(message='Subject'), required=False
    )
    body = forms.CharField(
        label=_(message='Body'), widget=forms.widgets.Textarea(),
        required=False
    )
    mailing_profile = forms.ModelChoiceField(
        help_text=_(
            message='The email profile that will be used to send this email.'
        ), label=_(message='Mailing profile'),
        queryset=UserMailer.objects.none()
    )


class UserMailerBackendSelectionForm(forms.Form):
    backend = forms.ChoiceField(
        choices=(), help_text=_(
            message='The driver to use when sending emails.'
        ), label=_(message='Backend')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['backend'].choices = MailerBackend.get_choices()


class UserMailerSetupDynamicForm(FormDynamicModelBackend):
    class Meta:
        fields = ('label', 'enabled', 'default')
        model = UserMailer


class UserMailerTestForm(forms.Form):
    email = forms.CharField(
        help_text=_(
            message='Email address of the recipient. Can be multiple '
            'addresses separated by comma or semicolon.'
        ), label=_(message='Email address'), validators=[
            validate_email_multiple
        ]
    )
