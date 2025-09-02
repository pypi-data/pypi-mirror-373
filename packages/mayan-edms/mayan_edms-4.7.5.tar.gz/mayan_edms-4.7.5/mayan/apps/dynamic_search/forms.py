from django import forms
from django.utils.translation import gettext_lazy as _

from mayan.apps.views.forms import Form

from .literals import MATCH_ALL_FIELD_CHOICES, MATCH_ALL_FIELD_NAME
from .settings import setting_store_results_default_value


class SearchFormBase(Form):
    _save_results = forms.BooleanField(
        help_text=_(
            message='Store the search results to speed up paging and for '
            'later browsing.'
        ), initial=setting_store_results_default_value.value, required=False,
        label=_(message='Save results')
    )

    def get_fieldsets(self):
        return (
            (
                _(message='Persistency'), {
                    'fields': ('_save_results',)
                },
            ),
        )


class AdvancedSearchForm(SearchFormBase):
    def __init__(self, *args, **kwargs):
        kwargs['data'] = kwargs['data'].copy()
        self.search_model = kwargs.pop('search_model')
        super().__init__(*args, **kwargs)

        fieldsets_dict = {}

        self.fields[MATCH_ALL_FIELD_NAME] = forms.ChoiceField(
            choices=MATCH_ALL_FIELD_CHOICES, label=_(message='Match all'),
            help_text=_(message='Return only results that match all fields.'),
            required=False, widget=forms.RadioSelect,
        )

        for search_field in self.search_model.search_fields_label_sorted:
            if search_field.concrete and not search_field.field_name == 'id':
                self.fields[search_field.field_name] = forms.CharField(
                    help_text=search_field.get_help_text(),
                    label=search_field.label, required=False,
                    widget=forms.widgets.TextInput(
                        attrs={'type': 'search'}
                    )
                )

                # Build the fieldset dictionary.
                model = search_field.field_name_model_list[0]

                model_verbose_name_plural = model._meta.verbose_name_plural

                fieldsets_dict.setdefault(
                    model_verbose_name_plural, {
                        'fields': []
                    }
                )
                fieldsets_dict[model_verbose_name_plural]['fields'].append(
                    search_field.field_name
                )

        # Convert the fieldset dictionary to the standard fieldset tuple.
        fieldsets = ()

        fieldsets += (
            (
                _(message='Search logic'), {
                    'fields': (MATCH_ALL_FIELD_NAME,)
                }
            ),
        )

        keys = list(
            fieldsets_dict.keys()
        )
        keys.sort()

        for key in keys:
            fieldsets += (
                key, fieldsets_dict[key]
            ),

        self._fieldsets = fieldsets

    def get_fieldsets(self):
        fieldsets = super().get_fieldsets()

        fieldsets += self._fieldsets

        return fieldsets


class SearchForm(SearchFormBase):
    q = forms.CharField(
        max_length=128, label=_(message='Search terms'), required=False,
        widget=forms.widgets.TextInput(
            attrs={'type': 'search'}
        )
    )

    def get_fieldsets(self):
        fieldsets_super = super().get_fieldsets()

        fieldsets = (
            (
                _(message='Criteria'), {
                    'fields': ('q',)
                },
            ),
        )

        fieldsets += fieldsets_super

        return fieldsets
