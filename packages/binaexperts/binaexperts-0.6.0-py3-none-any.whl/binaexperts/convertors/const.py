CONVERTOR_FORMAT_COCO = 'coco'
CONVERTOR_FORMAT_YOLO = 'yolo'
CONVERTOR_FORMAT_BINAEXPERTS = 'binaexperts'
CONVERTOR_FORMAT_YOLOv8_obb = 'yolov8-obb'

YOLO_YAML_FILENAME = 'data.yaml'
YOLO_IMAGES_SUBDIR = 'images'
YOLO_LABELS_SUBDIR = 'labels'
YOLO_IMAGE_DIR_PATH_TEMPLATE = "{}/images"
YOLO_LABEL_DIR_PATH_TEMPLATE = "{}/labels"

NORMALIZED_DATASET_DESCRIPTION = "Converted from COCO"
NORMALIZED_DATASET_NAME = "COCO Dataset"
NORMALIZED_DATASET_TYPE = "Object Detection and Segmentation"
NORMALIZER_SCHEMA_FILE = 'normalizer.json'

SCHEMA_DIR = 'schema'
COCO_SCHEMA_FILE = 'coco.json'
YOLOv8obb_SCHEMA_FILE = 'yolov8_obb.json'

INFO_KEY = 'info'
IMAGES_KEY = 'images'
ANNOTATIONS_KEY = 'annotations'
CATEGORIES_KEY = 'categories'
LICENSES_KEY = 'licenses'
DATASET_KEYS = [INFO_KEY, IMAGES_KEY, ANNOTATIONS_KEY, CATEGORIES_KEY, LICENSES_KEY]
VALID_SPLIT = 'valid'
TRAIN_SPLIT = 'train'
TEST_SPLIT = 'test'
VALID_SPLIT_ALIASES = ['valid', 'val', 'validation']
DESCRIPTION_KEY = 'description'
DATASET_NAME_KEY = 'dataset_name'
DATASET_TYPE_KEY = 'dataset_type'
DATE_CREATED_KEY = 'date_created'
DATE_FORMAT = '%Y-%m-%d'
BBOX_KEY = 'bbox'
SEGMENTATION_KEY = 'segmentation'
AREA_KEY = 'area'
ISCROWD_KEY = 'iscrowd'
BBOX_FORMAT_KEY = 'bbox_format'
COCO_BBOX_FORMAT = 'xywh'
DEFAULT_TRAIN_SPLIT = 'train'
DEFAULT_SUPERCATEGORY = 'none'
DEFAULT_DESCRIPTION = 'Converted dataset to COCO'
DEFAULT_DATASET_NAME = 'COCO Dataset'
DEFAULT_DATASET_TYPE = 'Object Detection'
DEFAULT_LICENSE = {"id": 1, "name": "Unknown License", "url": "unknown"}
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
COCO_ANNOTATION_FILE = '_annotations.coco.json'

UNKNOWN_ANNOTATION_ID = 'Unknown'
COCO_DATASET_CONTEXT = 'COCO dataset'

ANNOTATION_JSON_PATH_TEMPLATE = "{}/_annotations.coco.json"
IMAGES_KEY = 'images'
ANNOTATIONS_KEY = 'annotations'
CATEGORIES_KEY = 'categories'
INFO_KEY = 'info'
LICENSES_KEY = 'licenses'
SPLIT_KEY = 'split'
ID_KEY = 'id'
FILE_NAME_KEY = 'file_name'
WIDTH_KEY = 'width'
HEIGHT_KEY = 'height'
IMAGE_ID_KEY = 'image_id'
IMAGE_CONTENT_KEY = 'image_content'
CX_KEY = 'cx'
CY_KEY = 'cy'
WIDTH_BOX_KEY = 'width'
HEIGHT_BOX_KEY = 'height'

X1 = "x1"
Y1 = "y1"

X2 = "x2"
Y2 = "y2"

X3 = "x3"
Y3 = "y3"

X4 = "x4"
Y4 = "y4"

YOLO_SCHEMA_FILE = 'yolo.json'

TRAIN_DIR = 'train'
VALID_DIR = 'valid'
TEST_DIR = 'test'
DATASET_IMAGES_KEY = 'images'
DATASET_CLASS_NAMES_KEY = 'class_names'
DATASET_LICENSES_KEY = 'licenses'
OBJECT_DETECTION_TYPE = 'Object Detection'
SEGMENTATION_TYPE = 'Segmentation'

CONVERTED_FROM_YOLO = 'Converted from YOLO Dataset'
CONVERTED_FROM_YOLOv8_obb = 'Converted from YOLOv8-obb Dataset'

YOLO_DATASET_NAME = 'YOLO Dataset'
YOLOv8_obb_DATASET_NAME = 'YOLOv8-obb Dataset'
DATE_FORMAT_YOLO = '%Y-%m-%d %H:%M:%S'
SPLITS_KEY = 'splits'
NC_KEY = 'nc'
NAMES_KEY = 'names'
SOURCE_ZIP_KEY = 'source_zip'
CATEGORY_ID_KEY = 'category_id'
CLASS_ID_KEY = 'class_id'
BBOX_FORMAT_VALUE = 'xywh'
NAME_KEY = 'name'
SUPERCATEGORY_KEY = 'supercategory'
SUPERCATEGORY_DEFAULT = 'none'
NORMALIZED_DATASET_CONTEXT = 'Normalized YOLO Dataset'
NORMALIZED_DATASET_VALIDATION_ERROR = 'Validation error in normalized YOLO dataset.'
ERROR_MESSAGE_TEMPLATE = "Expected bbox height to be <= 1.0, got {height}"
YOLO_DATASET_CONTEXT = 'YOLO dataset'
YOLO_DATASET_VALIDATION_FAILED = 'YOLO dataset validation failed.'
DATA_YAML_FILE = 'data.yaml'
SAVED_DATA_YAML_MESSAGE = 'Saved data.yaml'
VALIDATION_SPLIT = 'validation'
TXT_EXT = '.txt'

BINAEXPERTS_SCHEMA_FILE = 'binaexperts.json'
TRAIN_IMAGES_DIR = 'train_images'
TEST_IMAGES_DIR = 'test_images'
VALIDATION_IMAGES_DIR = 'validation_images'
TRAIN_COCO_FILE = 'train_coco.json'
TEST_COCO_FILE = 'test_coco.json'
VALID_COCO_FILE = 'val_coco.json'
COCOS_DIR = 'cocos'
DATASET_KEY = 'dataset'
ORGANIZATION_KEY = 'organization'
ERRORS_KEY = 'errors'
LABELS_KEY = 'labels'
CLASSIFICATIONS_KEY = 'classifications'
AUGMENTATION_SETTINGS_KEY = 'augmentation_settings'
TILE_SETTINGS_KEY = 'tile_settings'
FALSE_POSITIVE_KEY = 'False_positive'
VALIDATION_PREFIX = 'val'
SKIPPING_SPLIT = 'Skipping split'
WARNING_NO_IMAGES_OR_ANNOTATIONS = 'Warning: No images or annotations found for split'
DEFAULT_TILE_SETTINGS = {"type": None, "enabled": False, "tile_width": None, "tile_height": None}
DEFAULT_FALSE_POSITIVE = {"False_positive": False}
CONVERTED_FROM_BINAEXPERTS = 'Converted from BinaExperts'
BINAEXPERTS_DATASET_NAME = 'BinaExperts Dataset'
SKIPPING_IMAGE = 'Skipping image'
SKIPPING_SUBDIR = 'Skipping this subdir'
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480

