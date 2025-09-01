from mayan.apps.common.tests.literals import (
    TEST_ARCHIVE_MSG_STRANGE_DATE_FILENAME, TEST_ARCHIVE_MSG_STRANGE_DATE_PATH
)
from mayan.apps.documents.events import (
    event_document_created, event_document_file_created,
    event_document_file_edited, event_document_version_created,
    event_document_version_edited, event_document_version_page_created
)
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.tests.base import GenericDocumentTestCase
from mayan.apps.source_compressed.source_backends.literals import (
    SOURCE_UNCOMPRESS_CHOICE_ALWAYS, SOURCE_UNCOMPRESS_CHOICE_ASK,
    SOURCE_UNCOMPRESS_CHOICE_NEVER
)

from .mixins import CompressedSourceTestMixin


class CompressedSourceBackendActionDocumentUploadTestCase(
    CompressedSourceTestMixin, GenericDocumentTestCase
):
    _test_source_create_auto = False
    _test_source_file_path = TEST_ARCHIVE_MSG_STRANGE_DATE_PATH
    auto_upload_test_document = False

    def test_compressed_always(self):
        self._test_source_create(
            extra_data={'uncompress': SOURCE_UNCOMPRESS_CHOICE_ALWAYS}
        )

        document_count = Document.objects.count()

        self._test_object_track()

        self._clear_events()

        with open(file=self._test_source_file_path, mode='rb') as file_object:
            self._execute_test_source_action(
                action_name='document_upload',
                extra_data={'file_object': file_object}
            )

        self._test_object_set()

        self.assertEqual(
            Document.objects.count(), document_count + 1
        )

        self.assertEqual(self._test_document.label, 'message.txt')
        self.assertEqual(self._test_document.file_latest.size, 2711)

        events = self._get_test_events()
        self.assertEqual(events.count(), 6)

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, self._test_document)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, self._test_document)
        self.assertEqual(events[1].actor, self._test_document.file_latest)
        self.assertEqual(events[1].target, self._test_document.file_latest)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, self._test_document)
        self.assertEqual(events[2].actor, self._test_document.file_latest)
        self.assertEqual(events[2].target, self._test_document.file_latest)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, self._test_document)
        self.assertEqual(events[3].actor, self._test_document.version_active)
        self.assertEqual(events[3].target, self._test_document.version_active)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(
            events[4].action_object, self._test_document.version_active
        )
        self.assertEqual(
            events[4].actor, self._test_document.version_active.pages.first()
        )
        self.assertEqual(
            events[4].target, self._test_document.version_active.pages.first()
        )
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[5].action_object, self._test_document)
        self.assertEqual(events[5].actor, self._test_document.version_active)
        self.assertEqual(events[5].target, self._test_document.version_active)
        self.assertEqual(events[5].verb, event_document_version_edited.id)

    def test_compressed_ask_false(self):
        self._silence_logger(name='mayan.apps.converter.backends')

        self._test_source_create(
            extra_data={'uncompress': SOURCE_UNCOMPRESS_CHOICE_ASK}
        )

        document_count = Document.objects.count()

        self._test_object_track()

        self._clear_events()

        with open(file=self._test_source_file_path, mode='rb') as file_object:
            self._execute_test_source_action(
                action_name='document_upload',
                extra_data={
                    'expand': False,
                    'file_object': file_object
                }
            )

        self._test_object_set()

        self.assertEqual(
            Document.objects.count(), document_count + 1
        )

        self.assertEqual(
            self._test_document.label, TEST_ARCHIVE_MSG_STRANGE_DATE_FILENAME
        )
        self.assertEqual(self._test_document.file_latest.size, 31744)

        events = self._get_test_events()
        self.assertEqual(events.count(), 6)

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, self._test_document)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, self._test_document)
        self.assertEqual(events[1].actor, self._test_document.file_latest)
        self.assertEqual(events[1].target, self._test_document.file_latest)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, self._test_document)
        self.assertEqual(events[2].actor, self._test_document.file_latest)
        self.assertEqual(events[2].target, self._test_document.file_latest)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, self._test_document)
        self.assertEqual(events[3].actor, self._test_document.version_active)
        self.assertEqual(events[3].target, self._test_document.version_active)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(
            events[4].action_object, self._test_document.version_active
        )
        self.assertEqual(
            events[4].actor, self._test_document.version_active.pages.first()
        )
        self.assertEqual(
            events[4].target, self._test_document.version_active.pages.first()
        )
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[5].action_object, self._test_document)
        self.assertEqual(events[5].actor, self._test_document.version_active)
        self.assertEqual(events[5].target, self._test_document.version_active)
        self.assertEqual(events[5].verb, event_document_version_edited.id)

    def test_compressed_ask_true(self):
        self._test_source_create(
            extra_data={'uncompress': SOURCE_UNCOMPRESS_CHOICE_ASK}
        )

        document_count = Document.objects.count()

        self._test_object_track()

        self._clear_events()

        with open(file=self._test_source_file_path, mode='rb') as file_object:
            self._execute_test_source_action(
                action_name='document_upload',
                extra_data={
                    'expand': True,
                    'file_object': file_object
                }
            )

        self._test_object_set()

        self.assertEqual(
            Document.objects.count(), document_count + 1
        )

        self.assertEqual(self._test_document.label, 'message.txt')
        self.assertEqual(self._test_document.file_latest.size, 2711)

        events = self._get_test_events()
        self.assertEqual(events.count(), 6)

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, self._test_document)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, self._test_document)
        self.assertEqual(events[1].actor, self._test_document.file_latest)
        self.assertEqual(events[1].target, self._test_document.file_latest)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, self._test_document)
        self.assertEqual(events[2].actor, self._test_document.file_latest)
        self.assertEqual(events[2].target, self._test_document.file_latest)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, self._test_document)
        self.assertEqual(events[3].actor, self._test_document.version_active)
        self.assertEqual(events[3].target, self._test_document.version_active)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(
            events[4].action_object, self._test_document.version_active
        )
        self.assertEqual(
            events[4].actor, self._test_document.version_active.pages.first()
        )
        self.assertEqual(
            events[4].target, self._test_document.version_active.pages.first()
        )
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[5].action_object, self._test_document)
        self.assertEqual(events[5].actor, self._test_document.version_active)
        self.assertEqual(events[5].target, self._test_document.version_active)
        self.assertEqual(events[5].verb, event_document_version_edited.id)

    def test_compressed_never(self):
        self._silence_logger(name='mayan.apps.converter.backends')

        self._test_source_create(
            extra_data={'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER}
        )

        document_count = Document.objects.count()

        self._test_object_track()

        self._clear_events()

        with open(file=self._test_source_file_path, mode='rb') as file_object:
            self._execute_test_source_action(
                action_name='document_upload',
                extra_data={'file_object': file_object}
            )

        self._test_object_set()

        self.assertEqual(
            Document.objects.count(), document_count + 1
        )

        self.assertEqual(
            self._test_document.label, TEST_ARCHIVE_MSG_STRANGE_DATE_FILENAME
        )
        self.assertEqual(self._test_document.file_latest.size, 31744)

        events = self._get_test_events()
        self.assertEqual(events.count(), 6)

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, self._test_document)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, self._test_document)
        self.assertEqual(events[1].actor, self._test_document.file_latest)
        self.assertEqual(events[1].target, self._test_document.file_latest)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, self._test_document)
        self.assertEqual(events[2].actor, self._test_document.file_latest)
        self.assertEqual(events[2].target, self._test_document.file_latest)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, self._test_document)
        self.assertEqual(events[3].actor, self._test_document.version_active)
        self.assertEqual(events[3].target, self._test_document.version_active)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(
            events[4].action_object, self._test_document.version_active
        )
        self.assertEqual(
            events[4].actor, self._test_document.version_active.pages.first()
        )
        self.assertEqual(
            events[4].target, self._test_document.version_active.pages.first()
        )
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[5].action_object, self._test_document)
        self.assertEqual(events[5].actor, self._test_document.version_active)
        self.assertEqual(events[5].target, self._test_document.version_active)
        self.assertEqual(events[5].verb, event_document_version_edited.id)
