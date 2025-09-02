import logging

from django.apps import apps
from django.db import models

from mayan.apps.databases.manager_mixins import ManagerMinixCreateBulk

logger = logging.getLogger(name=__name__)


class FileMetadataEntryManager(ManagerMinixCreateBulk, models.Manager):
    """
    Leave empty as no other methods are necessary at the moment. This is just
    to allow the mixin into the manager class.
    """


class DocumentTypeSettingsManager(models.Manager):
    def get_by_natural_key(self, document_type_natural_key):
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )
        try:
            document_type = DocumentType.objects.get_by_natural_key(
                document_type_natural_key
            )
        except DocumentType.DoesNotExist:
            raise self.model.DoesNotExist

        return self.get(document_type__pk=document_type.pk)
