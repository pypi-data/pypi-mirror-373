import logging

import extract_msg

from django.utils.translation import gettext_lazy as _

from mayan.apps.storage.literals import MSG_MIME_TYPES

from ..classes import FileMetadataDriver

logger = logging.getLogger(__name__)


class ExtractMSGToolDriver(FileMetadataDriver):
    description = _(
        'Extracts information from emails saved in Microsoft Outlook\'s '
        '.msg files.'
    )
    label = _(message='Extract msg')
    internal_name = 'extract_msg'
    mime_type_list = list(MSG_MIME_TYPES)

    def _process(self, document_file):
        message = extract_msg.Message(
            path=document_file.open()
        )
        result = {}

        if message.cc:
            result['cc'] = message.cc

        if message.sender:
            result['sender'] = message.sender

        if message.subject:
            result['subject'] = message.subject

        if message.to:
            result['to'] = message.to

        logger.debug('message file metadata: %s', result)

        return result
