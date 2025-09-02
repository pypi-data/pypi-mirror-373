import hashlib

from django.apps import apps
from django.conf import settings
from django.core import serializers
from django.db.models import F, Max, Q
from django.utils.translation import gettext_lazy as _

from mayan.apps.documents.models.document_models import Document

from ..literals import (
    ERROR_LOG_DOMAIN_NAME, GRAPHVIZ_COLOR_STATE_FILL, GRAPHVIZ_ID_STATE,
    GRAPHVIZ_SHAPE_CIRCLE, GRAPHVIZ_SHAPE_DOUBLECIRCLE, GRAPHVIZ_STYLE_FILLED,
    WORKFLOW_ACTION_ON_ENTRY, WORKFLOW_ACTION_ON_EXIT
)


class WorkflowStateBusinessLogicMixin:
    def do_active_set(self, workflow_instance):
        queryset = self.entry_actions.filter(enabled=True)
        self.do_queryset_actions_execute(
            queryset=queryset, workflow_instance=workflow_instance
        )

    def do_active_unset(self, workflow_instance):
        queryset = self.exit_actions.filter(enabled=True)
        self.do_queryset_actions_execute(
            queryset=queryset, workflow_instance=workflow_instance
        )

    def do_queryset_actions_execute(self, queryset, workflow_instance):
        for action in queryset:
            context = workflow_instance.get_context()
            context.update(
                {'action': action}
            )

            try:
                action.execute(
                    context=context, workflow_instance=workflow_instance
                )
            except Exception as exception:
                queryset_error_logs = workflow_instance.document.error_log
                queryset_error_logs.create(
                    domain_name=ERROR_LOG_DOMAIN_NAME,
                    text='{}; {}'.format(
                        exception.__class__.__name__, exception
                    )
                )

                if settings.DEBUG or settings.TESTING:
                    raise

                break
            else:
                queryset_error_logs = workflow_instance.document.error_log.filter(
                    domain_name=ERROR_LOG_DOMAIN_NAME
                )
                queryset_error_logs.delete()

    def do_diagram_generate(self, diagram):
        is_edge_state = self.initial or not self.destination_transitions.exists() or not self.origin_transitions.exists()

        if is_edge_state:
            shape = GRAPHVIZ_SHAPE_DOUBLECIRCLE
        else:
            shape = GRAPHVIZ_SHAPE_CIRCLE

        if self.initial:
            style = GRAPHVIZ_STYLE_FILLED
        else:
            style = ''

        node_kwargs = {
            'fillcolor': GRAPHVIZ_COLOR_STATE_FILL,
            'label': self.label,
            'name': self.get_graph_id(),
            'shape': shape,
            'style': style
        }
        diagram.node(**node_kwargs)

        for action in self.actions.all():
            action.do_diagram_generate(diagram=diagram)

        for escalation in self.escalations.all():
            escalation.do_diagram_generate(diagram=diagram)

    @property
    def entry_actions(self):
        return self.actions.filter(when=WORKFLOW_ACTION_ON_ENTRY)

    @property
    def exit_actions(self):
        return self.actions.filter(when=WORKFLOW_ACTION_ON_EXIT)

    def get_actions_display(self):
        field_list = [
            str(field) for field in self.actions.all()
        ]
        field_list.sort()

        return ', '.join(field_list)

    get_actions_display.short_description = _(message='Actions')

    def get_documents(self):
        WorkflowInstanceLogEntry = apps.get_model(
            app_label='document_states',
            model_name='WorkflowInstanceLogEntry'
        )

        latest_entries = WorkflowInstanceLogEntry.objects.annotate(
            max_datetime=Max(
                'workflow_instance__log_entries__datetime'
            )
        ).filter(
            datetime=F('max_datetime')
        )

        state_latest_entries = latest_entries.filter(
            transition__destination_state=self
        )

        return Document.valid.filter(
            Q(
                workflows__pk__in=state_latest_entries.values_list(
                    'workflow_instance', flat=True
                )
            ) | Q(
                workflows__log_entries__isnull=True,
                workflows__workflow__states=self,
                workflows__workflow__states__initial=True
            )
        ).distinct()

    def get_escalations_display(self):
        field_list = [
            str(field) for field in self.escalations.all()
        ]
        field_list.sort()

        return ', '.join(field_list)

    get_escalations_display.short_description = _(message='Escalations')

    def get_graph_id(self):
        return '{}{}'.format(GRAPHVIZ_ID_STATE, self.pk)

    def get_hash(self):
        result = hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        )

        for action in self.actions.all():
            result.update(
                action.get_hash().encode()
            )

        for escalation in self.escalations.all():
            result.update(
                escalation.get_hash().encode()
            )

        return result.hexdigest()
