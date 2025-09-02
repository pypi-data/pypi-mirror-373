import yaml

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from mayan.apps.common.serialization import yaml_load


class SettingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setting = self.initial['setting']

        choices = self.setting.get_value_choices()

        if choices:
            self.fields['value'] = forms.ChoiceField(
                choices=list(
                    zip(choices, choices)
                ), required=True, widget=forms.widgets.Select(
                    attrs={'class': 'select2'}
                )
            )
        else:
            self.fields['value'] = forms.CharField(
                required=False, widget=forms.widgets.Textarea()
            )

        self.fields['value'].label = _(message='Value')
        self.fields['value'].help_text = self.setting.help_text or _(
            message='Enter the new setting value.'
        )
        self.fields['value'].initial = self.setting.get_value_current()

    def clean(self):
        try:
            yaml_load(
                stream=self.cleaned_data['value']
            )
        except yaml.YAMLError:
            raise ValidationError(
                message=_(
                    message='"%s" not a valid entry.'
                ) % self.cleaned_data['value']
            )
        else:
            self.setting.do_value_raw_validate(
                raw_value=self.cleaned_data['value']
            )
