TEST_DRIVER_CLASS_PATH = 'mayan.apps.file_metadata.tests.drivers.FileMetadataDriverTest'
TEST_DRIVER_INTERNAL_NAME = 'test_driver'
TEST_DRIVER_LABEL = 'test label'

TEST_FILE_METADATA_KEY = 'test_key'
TEST_FILE_METADATA_VALUE = 'test_value'

TEST_FILE_METADATA_INDEX_NODE_TEMPLATE = "{{{{ document.file_metadata_value_of.{}__{} }}}}".format(
    TEST_DRIVER_INTERNAL_NAME, TEST_FILE_METADATA_KEY
)

# MSG

TEST_MSG_FILE_METADATA_DOTTED_NAME_SUBJECT = 'extract_msg__subject'
TEST_MSG_FILE_METADATA_DOTTED_NAME_TO = 'extract_msg__to'

TEST_MSG_FILE_METADATA_VALUE_SUBJECT = 'MSG Test File'
TEST_MSG_FILE_METADATA_VALUE_TO = 'time2talk@online-convert.com <time2talk@online-convert.com>'

# PDF

TEST_PDF_FILE_METADATA_DOTTED_NAME = 'exiftool__producer'
TEST_PDF_FILE_METADATA_VALUE = 'pdfTeX-1.40.10'
