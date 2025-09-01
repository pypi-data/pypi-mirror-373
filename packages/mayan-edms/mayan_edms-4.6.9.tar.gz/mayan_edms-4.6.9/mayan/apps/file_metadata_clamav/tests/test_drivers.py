from mayan.apps.documents.tests.base import GenericDocumentTestCase
from mayan.apps.file_metadata.tests.mixins import DocumentFileMetadataTestMixin

from ..drivers import ClamScanDriver

from .literals import (
    TEST_CLAMSCAN_FILE_METADATA_DOTTED_NAME,
    TEST_CLAMSCAN_FILE_METADATA_VALUE
)


class ClamScanDriverTestCase(
    DocumentFileMetadataTestMixin, GenericDocumentTestCase
):
    _test_document_file_metadata_driver_path = ClamScanDriver.dotted_path

    def test_driver_entries(self):
        self._test_document.submit_for_file_metadata_processing()

        value = self._test_document_file.get_file_metadata(
            dotted_name=TEST_CLAMSCAN_FILE_METADATA_DOTTED_NAME
        )
        self.assertEqual(value, TEST_CLAMSCAN_FILE_METADATA_VALUE)
