from mayan.apps.common.tests.literals import TEST_ARCHIVE_MSG_STRANGE_DATE_PATH
from mayan.apps.documents.tests.base import GenericDocumentTestCase
from mayan.apps.documents.tests.literals import TEST_FILE_PDF_FILENAME

from ..drivers.exiftool import EXIFToolDriver
from ..drivers.extract_msg import ExtractMSGToolDriver

from .literals import (
    TEST_MSG_FILE_METADATA_DOTTED_NAME_SUBJECT,
    TEST_MSG_FILE_METADATA_DOTTED_NAME_TO,
    TEST_MSG_FILE_METADATA_VALUE_SUBJECT, TEST_MSG_FILE_METADATA_VALUE_TO,
    TEST_PDF_FILE_METADATA_DOTTED_NAME, TEST_PDF_FILE_METADATA_VALUE
)
from .mixins import DocumentFileMetadataTestMixin


class EXIFToolDriverTestCase(
    DocumentFileMetadataTestMixin, GenericDocumentTestCase
):
    _test_document_file_metadata_driver_path = EXIFToolDriver.dotted_path
    _test_document_filename = TEST_FILE_PDF_FILENAME

    def test_driver_entries(self):
        self._test_document.submit_for_file_metadata_processing()

        value = self._test_document_file.get_file_metadata(
            dotted_name=TEST_PDF_FILE_METADATA_DOTTED_NAME
        )
        self.assertEqual(value, TEST_PDF_FILE_METADATA_VALUE)


class ExtractMSGDriverTestCase(
    DocumentFileMetadataTestMixin, GenericDocumentTestCase
):
    _test_document_file_metadata_driver_path = ExtractMSGToolDriver.dotted_path
    _test_document_filename = TEST_ARCHIVE_MSG_STRANGE_DATE_PATH

    def test_driver_entries(self):
        self._test_document.submit_for_file_metadata_processing()

        value_subject = self._test_document_file.get_file_metadata(
            dotted_name=TEST_MSG_FILE_METADATA_DOTTED_NAME_SUBJECT
        )
        self.assertEqual(value_subject, TEST_MSG_FILE_METADATA_VALUE_SUBJECT)

        value_to = self._test_document.file_latest.get_file_metadata(
            dotted_name=TEST_MSG_FILE_METADATA_DOTTED_NAME_TO
        )
        self.assertEqual(value_to, TEST_MSG_FILE_METADATA_VALUE_TO)
