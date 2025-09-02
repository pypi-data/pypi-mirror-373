import bleach

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave

from .events import (
    event_theme_created, event_theme_edited, event_user_theme_settings_edited
)


class Theme(models.Model):
    label = models.CharField(
        db_index=True, help_text=_(
            message='A short text describing the theme.'
        ), max_length=128, unique=True, verbose_name=_(message='Label')
    )
    stylesheet = models.TextField(
        blank=True, help_text=_(
            message='The CSS stylesheet to change the appearance of the '
            'different user interface elements.'
        ), verbose_name=_(message='Stylesheet')
    )

    class Meta:
        ordering = ('label',)
        verbose_name = _(message='Theme')
        verbose_name_plural = _(message='Themes')

    def __str__(self):
        return force_str(s=self.label)

    def get_absolute_url(self):
        return reverse(
            kwargs={'theme_id': self.pk},
            viewname='appearance:theme_edit'
        )

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_theme_created,
            'target': 'self'
        },
        edited={
            'event': event_theme_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        self.stylesheet = bleach.clean(
            text=self.stylesheet, tags=('style',)
        )
        super().save(*args, **kwargs)


class UserThemeSetting(models.Model):
    user = models.OneToOneField(
        on_delete=models.CASCADE, related_name='theme_settings',
        to=settings.AUTH_USER_MODEL, verbose_name=_(message='User')
    )
    theme = models.ForeignKey(
        blank=True, null=True, on_delete=models.CASCADE,
        related_name='user_setting', to=Theme, verbose_name=_(message='Theme')
    )

    class Meta:
        verbose_name = _(message='User theme setting')
        verbose_name_plural = _(message='User theme settings')

    def __str__(self):
        return force_str(s=self.user)

    @method_event(
        event_manager_class=EventManagerSave,
        edited={
            'event': event_user_theme_settings_edited,
            'target': 'user'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
