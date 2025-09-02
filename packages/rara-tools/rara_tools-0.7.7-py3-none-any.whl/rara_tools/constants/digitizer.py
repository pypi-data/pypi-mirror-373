COMPONENT_KEY = "digitizer"
ES_INDEX_DEFAULT = "digitizer_output"


class ModelTypes:
    IMAGE_PROCESSOR = "image_processor"


class StatusKeys:
    DOWNLOAD_MODELS = "digitizer_download_models"
    CLEAN_UP = "digitizer_clean_up"
    ELASTICSEARCH_UPLOAD = "digitizer_elasticsearch_upload"
    UPLOAD = "s3_upload"
    DOWNLOAD = "digitizer_s3_download"
    OCR = "digitizer_ocr"


class Queue:
    IO = "io"
    DOWNLOAD = "download"
    FINISH = "finish"
    OCR = "ocr"
    UTILITY = "digitizer-utility"


class Tasks:
    START_DIGITIZER_PIPELINE = "start_digitizer_pipeline"
    PURGE_MODELS = "purge_unused_digitizer_models"


class Error:
    NO_SPACE = "Disk out of space!"
    COULDNT_DOWNLOAD = "Unknown error when downloading model!"
    UNKNOWN = "Unknown system error!"
    S3_CONNECTION = "Failed to connect to S3!"
    UNSUPPORTED_FILETYPE = "Unsupported file type!"
    COULDNT_UPLOAD = "Could not upload documents to Elasticsearch!"
    FILE_IS_PROTECTED = "File is password protected or encrypted!"
    UNKNOWN_OCR = "Unknown error when applying ocr!"
    CUSTOM_MODEL_ERROR = "Couldn't download custom image classification model!"
