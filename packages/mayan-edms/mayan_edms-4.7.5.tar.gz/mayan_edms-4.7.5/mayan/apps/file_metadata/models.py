from django.db import models
from django.utils.translation import gettext_lazy as _

from mayan.apps.common.utils import convert_to_internal_name
from mayan.apps.documents.models.document_file_models import DocumentFile
from mayan.apps.documents.models.document_type_models import DocumentType

from .managers import DocumentTypeSettingsManager, FileMetadataEntryManager
from .model_mixins import (
    DocumentFileDriverEntryBusinessLogicMixin, StoredDriverBusinessLogicMixin
)


class DocumentFileDriverEntry(
    DocumentFileDriverEntryBusinessLogicMixin, models.Model
):
    driver = models.ForeignKey(
        on_delete=models.CASCADE, related_name='driver_entries',
        to='StoredDriver', verbose_name=_(message='Driver')
    )
    document_file = models.ForeignKey(
        on_delete=models.CASCADE, related_name='file_metadata_drivers',
        to=DocumentFile, verbose_name=_(message='Document file')
    )

    class Meta:
        ordering = ('document_file', 'driver')
        unique_together = ('driver', 'document_file')
        verbose_name = _(message='Document file driver entry')
        verbose_name_plural = _(message='Document file driver entries')

    def __str__(self):
        return str(self.driver)


class DocumentTypeSettings(models.Model):
    """
    Model to store the file metadata settings for a document type.
    """
    document_type = models.OneToOneField(
        on_delete=models.CASCADE, related_name='file_metadata_settings',
        to=DocumentType, unique=True, verbose_name=_(message='Document type')
    )
    auto_process = models.BooleanField(
        default=True, help_text=_(
            message='Automatically queue newly created documents for '
            'processing.'
        ), verbose_name=_(message='Auto process')
    )

    objects = DocumentTypeSettingsManager()

    class Meta:
        verbose_name = _(message='Document type settings')
        verbose_name_plural = _(message='Document types settings')

    def natural_key(self):
        return self.document_type.natural_key()
    natural_key.dependencies = ['documents.DocumentType']


class FileMetadataEntry(models.Model):
    document_file_driver_entry = models.ForeignKey(
        on_delete=models.CASCADE, related_name='entries',
        to=DocumentFileDriverEntry,
        verbose_name=_(message='Document file driver entry')
    )
    internal_name = models.CharField(
        db_index=True, help_text=_(
            message='Normalized name of the file metadata entry.'
        ), max_length=255, verbose_name=_(message='Internal name')
    )
    key = models.CharField(
        help_text=_(
            message='Name of the file metadata entry as provided by the '
            'driver.'
        ), max_length=255, verbose_name=_(message='Key')
    )
    value = models.TextField(
        blank=True, help_text=_(message='Value of the file metadata entry.'),
        max_length=255, verbose_name=_(message='Value')
    )

    class Meta:
        ordering = ('internal_name', 'value')
        unique_together = ('document_file_driver_entry', 'internal_name')
        verbose_name = _(message='File metadata entry')
        verbose_name_plural = _(message='File metadata entries')

    objects = FileMetadataEntryManager()

    def __str__(self):
        return '{}: {}: {}'.format(
            self.document_file_driver_entry, self.key, self.value
        )

    def save(self, *args, **kwargs):
        internal_name = convert_to_internal_name(value=self.key)

        queryset_siblings = self.document_file_driver_entry.entries.exclude(
            pk=self.pk
        )

        queryset_duplicated = queryset_siblings.filter(
            internal_name=internal_name
        )

        if queryset_duplicated.exists():
            internal_name = '{}_{}'.format(
                internal_name, queryset_duplicated.count()
            )

        self.internal_name = internal_name

        super().save(*args, **kwargs)


class StoredDriver(StoredDriverBusinessLogicMixin, models.Model):
    driver_path = models.CharField(
        max_length=255, unique=True, verbose_name=_(message='Driver path')
    )
    internal_name = models.CharField(
        db_index=True, max_length=128, unique=True,
        verbose_name=_(message='Internal name')
    )

    class Meta:
        ordering = ('internal_name',)
        verbose_name = _(message='Driver')
        verbose_name_plural = _(message='Drivers')

    def __str__(self):
        return str(self.driver_label)
