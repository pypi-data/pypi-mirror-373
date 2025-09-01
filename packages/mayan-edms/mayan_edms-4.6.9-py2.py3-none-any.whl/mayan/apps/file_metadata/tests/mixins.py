from django.utils.module_loading import import_string

from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin

from ..classes import FileMetadataDriver

from .literals import (
    TEST_DRIVER_CLASS_PATH, TEST_FILE_METADATA_KEY, TEST_FILE_METADATA_VALUE
)


class FileMetadataTestMixin:
    _test_document_file_metadata_driver_path = TEST_DRIVER_CLASS_PATH

    def setUp(self):
        super().setUp()
        FileMetadataDriver.load_modules()

        FileMetadataDriver.collection.do_driver_disable_all()

        if self._test_document_file_metadata_driver_path:
            self._test_document_file_metadata_driver = import_string(
                dotted_path=self._test_document_file_metadata_driver_path
            )
            self._test_document_file_metadata_driver.do_model_instance_populate()
            FileMetadataDriver.collection.do_driver_enable(
                driver=self._test_document_file_metadata_driver
            )


class DocumentFileMetadataTestMixin(
    DocumentTestMixin, FileMetadataTestMixin
):
    _test_document_file_metadata_create_auto = False

    def setUp(self):
        super().setUp()

        if self._test_document_file_metadata_create_auto:
            self._test_document_file_metadata_create()

    def _test_document_file_metadata_create(self):
        self._test_document_file_driver_entry, created = self._test_document_file.file_metadata_drivers.get_or_create(
            driver=self._test_document_file_metadata_driver.model_instance
        )

        self._test_document_file_metadata = self._test_document_file_driver_entry.entries.create(
            key=TEST_FILE_METADATA_KEY,
            value=TEST_FILE_METADATA_VALUE
        )

        self._test_document_file_metadata_path = '{}__{}'.format(
            self._test_document_file_driver_entry.driver.internal_name,
            self._test_document_file_metadata.key
        )


class DocumentFileMetadataViewTestMixin(DocumentFileMetadataTestMixin):
    def _request_document_file_metadata_driver_list_view(self):
        return self.get(
            viewname='file_metadata:document_file_metadata_driver_list',
            kwargs={'document_file_id': self._test_document_file.pk}
        )

    def _request_document_file_metadata_list_view(self):
        return self.get(
            viewname='file_metadata:document_file_metadata_driver_attribute_list',
            kwargs={
                'document_file_driver_id': self._test_document_file_driver_entry.pk
            }
        )

    def _request_document_file_metadata_single_submit_view(self):
        return self.post(
            viewname='file_metadata:document_file_metadata_single_submit',
            kwargs={'document_file_id': self._test_document_file.pk}
        )

    def _request_document_file_multiple_submit_view(self):
        return self.post(
            viewname='file_metadata:document_file_metadata_multiple_submit',
            data={
                'id_list': self._test_document_file.pk
            }
        )


class DocumentTypeViewTestMixin(FileMetadataTestMixin):
    def _request_document_type_file_metadata_settings_view(self):
        return self.get(
            viewname='file_metadata:document_type_file_metadata_settings',
            kwargs={'document_type_id': self._test_document.document_type.pk}
        )

    def _request_document_type_file_metadata_submit_view(self):
        return self.post(
            viewname='file_metadata:document_type_file_metadata_submit', data={
                'document_type': self._test_document_type.pk,
            }
        )


class FileMetadataDriverTestMixin(FileMetadataTestMixin):
    def _request_file_metadata_driver_list_view(self):
        return self.get(viewname='file_metadata:file_metadata_driver_list')
