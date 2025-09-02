from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import gettext_lazy as _


class WorkflowTransitionTriggerEventRelationshipForm(forms.Form):
    namespace = forms.CharField(
        label=_(message='Namespace'), required=False,
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        )
    )
    label = forms.CharField(
        label=_(message='Label'), required=False,
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        )
    )
    relationship = forms.ChoiceField(
        choices=(
            ('no', _(message='No')),
            ('yes', _(message='Yes')),
        ), label=_(message='Enabled'), widget=forms.RadioSelect()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['namespace'].initial = self.initial['event_type'].namespace
        self.fields['label'].initial = self.initial['event_type'].label

        relationship = self.initial['transition'].trigger_events.filter(
            event_type=self.initial['event_type']
        )

        if relationship.exists():
            self.fields['relationship'].initial = 'yes'
        else:
            self.fields['relationship'].initial = 'no'

    def save(self):
        relationship = self.initial['transition'].trigger_events.filter(
            event_type=self.initial['event_type']
        )

        if self.cleaned_data['relationship'] == 'no':
            relationship.delete()
        elif self.cleaned_data['relationship'] == 'yes':
            if not relationship.exists():
                self.initial['transition'].trigger_events.create(
                    event_type=self.initial['event_type']
                )


WorkflowTransitionTriggerEventRelationshipFormSet = formset_factory(
    form=WorkflowTransitionTriggerEventRelationshipForm, extra=0
)
