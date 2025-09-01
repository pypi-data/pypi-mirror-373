from django.db import models
from django.utils.translation import gettext_lazy as _

from mayan.apps.common.validators import YAMLValidator
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import (
    EventManagerMethodAfter, EventManagerSave
)
from mayan.apps.events.models import StoredEventType

from ..events import event_workflow_template_edited
from ..literals import FIELD_TYPE_CHOICES, WIDGET_CLASS_CHOICES

from .workflow_models import Workflow
from .workflow_state_models import WorkflowState
from .workflow_transition_model_mixins import (
    WorkflowTransitionBusinessLogicMixin,
    WorkflowTransitionFieldBusinessLogicMixin,
    WorkflowTransitionTriggerEventBusinessLogicMixin
)

__all__ = (
    'WorkflowTransition', 'WorkflowTransitionField',
    'WorkflowTransitionTriggerEvent'
)


class WorkflowTransition(
    ExtraDataModelMixin, WorkflowTransitionBusinessLogicMixin, models.Model
):
    workflow = models.ForeignKey(
        on_delete=models.CASCADE, related_name='transitions', to=Workflow,
        verbose_name=_(message='Workflow')
    )
    label = models.CharField(
        help_text=_(message='A short text to describe the transition.'),
        max_length=255, verbose_name=_(message='Label')
    )
    origin_state = models.ForeignKey(
        on_delete=models.CASCADE, related_name='origin_transitions',
        to=WorkflowState, verbose_name=_(message='Origin state')
    )
    destination_state = models.ForeignKey(
        on_delete=models.CASCADE, related_name='destination_transitions',
        to=WorkflowState, verbose_name=_(message='Destination state')
    )
    condition = models.TextField(
        blank=True, help_text=_(
            'The condition that will determine if this transition '
            'is enabled or not. The condition is evaluated against the '
            'workflow instance. Conditions that do not return any value, '
            'that return the Python logical None, or an empty string (\'\') '
            'are considered to be logical false, any other value is '
            'considered to be the logical true.'
        ), verbose_name=_(message='Condition')
    )

    class Meta:
        ordering = ('label',)
        unique_together = (
            'workflow', 'label', 'origin_state', 'destination_state'
        )
        verbose_name = _(message='Workflow transition')
        verbose_name_plural = _(message='Workflow transitions')

    def __str__(self):
        return self.label

    @method_event(
        action_object='self',
        event_manager_class=EventManagerMethodAfter,
        event=event_workflow_template_edited,
        target='workflow'
    )
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'self',
            'event': event_workflow_template_edited,
            'target': 'workflow'
        },
        edited={
            'action_object': 'self',
            'event': event_workflow_template_edited,
            'target': 'workflow'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class WorkflowTransitionField(
    ExtraDataModelMixin, WorkflowTransitionFieldBusinessLogicMixin,
    models.Model
):
    transition = models.ForeignKey(
        on_delete=models.CASCADE, related_name='fields',
        to=WorkflowTransition, verbose_name=_(message='Transition')
    )
    field_type = models.PositiveIntegerField(
        choices=FIELD_TYPE_CHOICES, verbose_name=_(message='Type')
    )
    name = models.CharField(
        help_text=_(
            'The name that will be used to identify this field in other '
            'parts of the workflow system.'
        ), max_length=128, verbose_name=_(message='Internal name')
    )
    label = models.CharField(
        help_text=_(
            'The field name that will be shown on the user interface.'
        ), max_length=128, verbose_name=_(message='Label')
    )
    help_text = models.TextField(
        blank=True, help_text=_(
            'An optional message that will help users better understand the '
            'purpose of the field and data to provide.'
        ), verbose_name=_(message='Help text')
    )
    required = models.BooleanField(
        default=False, help_text=_(
            'Whether this field needs to be filled out or not to proceed.'
        ), verbose_name=_('Required')
    )
    widget = models.PositiveIntegerField(
        blank=True, choices=WIDGET_CLASS_CHOICES, help_text=_(
            'An optional class to change the default presentation of the '
            'field.'
        ), null=True, verbose_name=_(message='Widget class')
    )
    widget_kwargs = models.TextField(
        blank=True, help_text=_(
            'A group of keyword arguments to customize the widget. '
            'Use YAML format.'
        ), validators=[
            YAMLValidator()
        ], verbose_name=_(message='Widget keyword arguments')
    )

    class Meta:
        unique_together = ('transition', 'name')
        verbose_name = _(message='Workflow transition field')
        verbose_name_plural = _(message='Workflow transition fields')

    def __str__(self):
        return self.label

    @method_event(
        action_object='self',
        event_manager_class=EventManagerMethodAfter,
        event=event_workflow_template_edited,
        target='transition.workflow'
    )
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'self',
            'event': event_workflow_template_edited,
            'target': 'transition.workflow'
        },
        edited={
            'action_object': 'self',
            'event': event_workflow_template_edited,
            'target': 'transition.workflow'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class WorkflowTransitionTriggerEvent(
    ExtraDataModelMixin, WorkflowTransitionTriggerEventBusinessLogicMixin,
    models.Model
):
    transition = models.ForeignKey(
        on_delete=models.CASCADE, related_name='trigger_events',
        to=WorkflowTransition, verbose_name=_(message='Transition')
    )
    event_type = models.ForeignKey(
        on_delete=models.CASCADE, to=StoredEventType,
        verbose_name=_(message='Event type')
    )

    class Meta:
        ordering = ('event_type__name',)
        unique_together = ('transition', 'event_type')
        verbose_name = _(message='Workflow transition trigger event')
        verbose_name_plural = _(
            message='Workflow transitions trigger events'
        )

    def __str__(self):
        return str(self.transition)

    @method_event(
        action_object='self',
        event_manager_class=EventManagerMethodAfter,
        event=event_workflow_template_edited,
        target='transition.workflow'
    )
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'self',
            'event': event_workflow_template_edited,
            'target': 'transition.workflow'
        },
        edited={
            'action_object': 'self',
            'event': event_workflow_template_edited,
            'target': 'transition.workflow'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
