import io
import logging
import yaml
import json
import os
import zipfile
import cv2
import numpy as np
import datetime

from jsonschema import validate, ValidationError
from abc import ABC, abstractmethod
from typing import Union, IO, Any, Dict

from binaexperts.convertors import const
from binaexperts.common.loadhelpers import loadhelper_coco_data, loadhelper_yolo_from_zip, \
    loadhelper_yolo_from_directory, loadhelper_yolov8obb_from_zip, loadhelper_yolov8obb_from_directory, \
    loadhelper_binaexperts_data
from binaexperts.common.utils import get_image_dimensions, validate_data, load_json_from_source, \
    create_zip_writer, convert_bbox_yolo_to_coco, convert_bbox_to_yolo_format, process_segmentation_data, \
    generate_yaml_content, create_label_content, create_error_entry, save_images_to_zip, create_coco_dict, \
    save_image_to_zip, convert_yolo_obb_to_coco, convert_coco_to_yolo_obb
from binaexperts.convertors.const import *

logger = logging.getLogger(__name__)


class BaseConvertor(ABC):
    """
    Abstract base class for dataset convertors.
    Defines the interface for loading, normalizing, converting, and saving datasets.
    """

    def __init__(self):
        pass

    @abstractmethod
    def load(self, source: Union[str, IO[bytes]]) -> Any:
        """
        Loads dataset from the specified source into a raw, format-specific dictionary.
        :param source: Path to the dataset (zip file or directory) or an in-memory BytesIO object.
        :return: A dictionary representing the loaded dataset in its original format.
        """
        raise NotImplementedError(
            "The 'load' method must be overridden by subclasses.")

    @abstractmethod
    def normalize(self, data: Any) -> Dict:
        """
        Normalizes the loaded dataset into a common, standardized format.
        :param data: The raw dataset dictionary loaded by the 'load' method.
        :return: A dictionary representing the normalized dataset.
        """
        raise NotImplementedError(
            "The 'normalize' method must be overridden by subclasses.")

    @abstractmethod
    def convert(self, normalized_data: Dict, target_format_actual: str,
                destination: Union[str, IO[bytes], None] = None) -> Union[Any, None]:
        """
        Converts the normalized dataset into the target format.
        If a destination is provided, it saves the converted data to that destination and returns None.
        Otherwise, it returns the converted dataset dictionary.

        :param normalized_data: The dataset in normalized format.
        :param target_format_actual: The actual target format ('yolo', 'yolov8-obb', 'coco', 'binaexperts').
        :param destination: (Optional) The destination to save the converted dataset (file path or BytesIO object).
        :return: The converted dataset dictionary if no destination is provided, otherwise None.
        """
        raise NotImplementedError(
            "The 'convert' method must be overridden by subclasses.")

    @abstractmethod
    def save(self, data: Any, destination: Union[str, IO[bytes]]) -> None:
        """
        Saves the converted dataset to the specified destination.
        :param data: The dataset to be saved.
        :param destination: The destination to save the dataset (file path or BytesIO object).
        """
        raise NotImplementedError(
            "The 'save' method must be overridden by subclasses.")


class COCOConvertor(BaseConvertor):
    """
    A convertor class for COCO dataset format.
    Handles loading, normalizing, converting to, and saving from COCO format.
    """

    def __init__(self):
        super().__init__()

        schema_path = os.path.join(os.path.dirname(__file__), '..', "convertors", const.SCHEMA_DIR,
                                   const.COCO_SCHEMA_FILE)
        schema_path = os.path.abspath(schema_path)
        try:
            with open(schema_path, 'r') as schema_file:
                self.coco_schema = json.load(schema_file)
        except Exception as e:
            logger.error(f"Failed to load COCO schema from {schema_path}: {e}")
            raise

        normalizer_schema_path = os.path.join(os.path.dirname(__file__), '..', "convertors", const.SCHEMA_DIR,
                                              const.NORMALIZER_SCHEMA_FILE)
        normalizer_schema_path = os.path.abspath(normalizer_schema_path)
        try:
            with open(normalizer_schema_path, 'r') as schema_file:
                self.normalizer_schema = json.load(schema_file)
        except Exception as e:
            logger.error(
                f"Failed to load Normalizer schema from {normalizer_schema_path}: {e}")
            raise

    def load(
            self,
            source: Union[str, IO[bytes]]
    ) -> Dict:
        """
        Loads a COCO-formatted dataset from a zip file, directory, or in-memory BytesIO object.

        This method supports loading COCO datasets where images and annotations are organized
        into 'train', 'test', and 'valid' subdirectories, each containing a `_annotations.coco.json` file.
        Image content is loaded into memory if the source is a zip file or BytesIO.

        :param source: The source of the COCO dataset, which can be:
                       - A string path to a zip file.
                       - A string path to a directory.
                       - An already open `zipfile.ZipFile` object.
                       - An in-memory `IO[bytes]` object (e.g., `BytesIO`) containing a zip file.
        :return: A dictionary representing the loaded COCO dataset, including image content.
                 The dictionary will have keys like 'images', 'annotations', 'categories', etc.,
                 and will include image content as `image_content` in image dictionaries.
        :raises ValueError: If the source type is unsupported or the path is invalid.
        :raises ValidationError: If loaded COCO data does not conform to the expected schema.
        """
        subdirs = [const.TRAIN_DIR, const.TEST_DIR, const.VALID_DIR]
        dataset = {key: [] for key in const.DATASET_KEYS}
        dataset[const.INFO_KEY] = {}

        if isinstance(source, str):
            if zipfile.is_zipfile(source):  # Handle zip file case
                with zipfile.ZipFile(source, 'r') as zip_file:
                    for subdir in subdirs:
                        annotation_path = f"{subdir}/{const.COCO_ANNOTATION_FILE}"
                        if annotation_path not in zip_file.namelist():
                            continue

                        coco_data = load_json_from_source(
                            zip_file, annotation_path)
                        if not validate_data(coco_data, self.coco_schema, context=subdir):
                            continue
                        loadhelper_coco_data(
                            coco_data, dataset, subdir, source_zip=zip_file)

            elif os.path.isdir(source):  # Handle directory case
                for subdir in subdirs:
                    annotation_file = os.path.join(
                        source, subdir, const.COCO_ANNOTATION_FILE)
                    if not os.path.isfile(annotation_file):
                        continue

                    coco_data = load_json_from_source(source, annotation_file)
                    if not validate_data(coco_data, self.coco_schema, context=subdir):
                        continue
                    loadhelper_coco_data(coco_data, dataset, subdir)

            else:
                raise ValueError(
                    f"Source '{source}' is not a valid zip file or directory path.")

        # Source is already an open ZipFile object
        elif isinstance(source, zipfile.ZipFile):
            for subdir in subdirs:
                annotation_path = f"{subdir}/{const.COCO_ANNOTATION_FILE}"
                if annotation_path not in source.namelist():
                    continue

                coco_data = load_json_from_source(source, annotation_path)
                if not validate_data(coco_data, self.coco_schema, context=subdir):
                    continue
                loadhelper_coco_data(coco_data, dataset,
                                     subdir, source_zip=source)

        elif hasattr(source, 'read'):  # Source is an in-memory BytesIO object
            source.seek(0)  # Ensure the pointer is at the beginning
            # FIX: Added 'with' statement for BytesIO
            with zipfile.ZipFile(source, 'r') as zip_file:
                for subdir in subdirs:
                    annotation_path = f"{subdir}/{const.COCO_ANNOTATION_FILE}"
                    if annotation_path not in zip_file.namelist():
                        continue

                    coco_data = load_json_from_source(
                        zip_file, annotation_path)
                    if not validate_data(coco_data, self.coco_schema, context=subdir):
                        continue
                    loadhelper_coco_data(
                        coco_data, dataset, subdir, source_zip=zip_file)

        else:
            raise ValueError("Unsupported source type for COCO load.")

        return dataset

    def normalize(
            self,
            data: dict
    ) -> dict:
        """
        Convert a COCO-formatted dataset dictionary into a normalized dataset dictionary.
        This version handles Roboflow-style COCO where category ID 0 might be a meta-category,
        but only skips it if its name indicates it's a placeholder.

        :param data: A dictionary representing the COCO dataset.
        :return: A dictionary representing the normalized dataset.
        :raises ValidationError: If the normalized dataset does not conform to the Normalizer schema.
        """
        # Check if category ID 0 exists and has a placeholder name, indicating it's a meta-category
        is_meta_category_0_placeholder = False
        # Find category with ID 0
        cat_id_0 = next((cat for cat in data.get(
            const.CATEGORIES_KEY, []) if cat.get(const.ID_KEY) == 0), None)
        if cat_id_0:
            # Common placeholder names for meta-category 0 in Roboflow exports
            # Added 'players-referee' as a potential unwanted placeholder name specific to the user's issue.
            if cat_id_0.get(const.NAME_KEY, '').strip().lower() in ['', '___', 'background', 'unlabeled',
                                                                    'players-referee']:
                is_meta_category_0_placeholder = True
                logger.info(
                    f"Detected meta-category ID 0 with name '{cat_id_0.get(const.NAME_KEY)}'. It will be skipped during normalization.")
            # Add more specific checks if needed, e.g., if there are no annotations for this category
            # For simplicity, we'll rely on name for now.

        actual_categories = []
        for cat in data.get(const.CATEGORIES_KEY, []):
            if is_meta_category_0_placeholder and cat.get(const.ID_KEY) == 0:
                continue  # Skip this category if it's the detected meta-category 0
            actual_categories.append(cat)

        # Create a new category_id_map for 0-indexed YOLO-like IDs based on the *filtered* actual_categories
        category_id_map = {cat[const.ID_KEY]: idx for idx,
                           cat in enumerate(actual_categories)}

        # Update names and nc based on actual categories
        normalized_names = [cat[const.NAME_KEY] for cat in actual_categories]
        normalized_nc = len(actual_categories)

        normalized_dataset = {
            const.INFO_KEY: {
                const.DESCRIPTION_KEY: const.NORMALIZED_DATASET_DESCRIPTION,
                const.DATASET_NAME_KEY: const.NORMALIZED_DATASET_NAME,
                const.DATASET_TYPE_KEY: const.NORMALIZED_DATASET_TYPE,
                const.SPLITS_KEY: {}
            },
            const.IMAGES_KEY: [],
            const.ANNOTATIONS_KEY: [],
            const.CATEGORIES_KEY: [],  # Will be populated with re-indexed categories
            const.LICENSES_KEY: data.get(const.LICENSES_KEY, []),
            const.NC_KEY: normalized_nc,
            const.NAMES_KEY: normalized_names
        }

        image_id_map = {image[const.ID_KEY]: idx for idx,
                        image in enumerate(data[const.IMAGES_KEY])}
        annotation_id = 1

        for image in data[const.IMAGES_KEY]:
            if const.WIDTH_KEY not in image or const.HEIGHT_KEY not in image:
                logger.warning(
                    f"Skipping image {image.get(const.FILE_NAME_KEY, 'Unknown')} due to missing width/height.")
                continue

            normalized_image = {
                const.ID_KEY: image_id_map[image[const.ID_KEY]],
                const.FILE_NAME_KEY: image[const.FILE_NAME_KEY],
                const.WIDTH_KEY: image[const.WIDTH_KEY],
                const.HEIGHT_KEY: image[const.HEIGHT_KEY],
                const.SPLIT_KEY: image.get(const.SPLIT_KEY, const.DEFAULT_TRAIN_SPLIT),
                const.SOURCE_ZIP_KEY: image.get(const.SOURCE_ZIP_KEY),
                const.IMAGE_CONTENT_KEY: image.get(const.IMAGE_CONTENT_KEY)
            }
            normalized_dataset[const.IMAGES_KEY].append(normalized_image)

        for ann in data[const.ANNOTATIONS_KEY]:
            # Skip annotations if their category_id is the meta-category (ID 0)
            # This check must align with the `is_meta_category_0_placeholder` logic
            if is_meta_category_0_placeholder and ann.get(const.CATEGORY_ID_KEY) == 0:
                logger.info(
                    f"Skipping annotation {ann.get(const.ID_KEY, 'Unknown')} with meta-category ID 0 because it's a placeholder.")
                continue

            # Ensure the category ID exists in our new re-indexed map.
            # This covers cases where category_id_map might not contain the ID (e.g., filtered out, or invalid ID).
            if ann.get(const.CATEGORY_ID_KEY) not in category_id_map or const.IMAGE_ID_KEY not in ann or ann[
                    const.IMAGE_ID_KEY] not in image_id_map:
                logger.warning(
                    f"Skipping annotation {ann.get(const.ID_KEY, 'Unknown')} due to missing category or image ID or invalid re-mapping.")
                continue

            normalized_annotation = {
                const.ID_KEY: annotation_id,
                const.IMAGE_ID_KEY: image_id_map[ann[const.IMAGE_ID_KEY]],
                # Use the new re-indexed ID
                const.CATEGORY_ID_KEY: category_id_map[ann[const.CATEGORY_ID_KEY]],
                const.BBOX_KEY: ann.get(const.BBOX_KEY, []),
                const.SEGMENTATION_KEY: ann.get(const.SEGMENTATION_KEY, []),
                const.AREA_KEY: ann.get(const.AREA_KEY, 0.0),
                const.ISCROWD_KEY: ann.get(const.ISCROWD_KEY, 0),
                const.BBOX_FORMAT_KEY: const.BBOX_FORMAT_VALUE
            }
            normalized_dataset[const.ANNOTATIONS_KEY].append(
                normalized_annotation)
            annotation_id += 1

        # Populate categories with the re-indexed ones
        for cat in actual_categories:  # Iterate over the filtered categories
            normalized_category = {
                # Use the new re-indexed ID
                const.ID_KEY: category_id_map[cat[const.ID_KEY]],
                const.NAME_KEY: cat[const.NAME_KEY],
                const.SUPERCATEGORY_KEY: cat.get(
                    const.SUPERCATEGORY_KEY, const.DEFAULT_SUPERCATEGORY)
            }
            normalized_dataset[const.CATEGORIES_KEY].append(
                normalized_category)

        if not validate_data(normalized_dataset, self.normalizer_schema, context=const.NORMALIZED_DATASET_CONTEXT):
            raise ValidationError(const.NORMALIZED_DATASET_VALIDATION_ERROR)

        return normalized_dataset

    def convert(
            self,
            normalized_data: dict,
            target_format_actual: str,
            destination: Union[str, IO[bytes], None] = None
    ) -> Union[Any, None]:
        """
        Converts the normalized dataset into COCO format.
        If a destination is provided, it saves the converted data to that destination and returns None.
        Otherwise, it returns the converted dataset dictionary.

        This method reconstructs the COCO dataset structure from the normalized data,
        including information, images, annotations, categories, and licenses.
        It prepares the data to be saved by the `save` method.

        :param normalized_data: The dataset in normalized format.
        :param target_format_actual: (Unused in this method, kept for signature compatibility).
        :param destination: (Optional) The destination to save the converted dataset (file path or BytesIO object).
        :return: The converted dataset dictionary if no destination is provided, otherwise None.
        :raises ValidationError: If the converted COCO dataset does not conform to the COCO schema.
        """
        coco_dataset = {
            const.INFO_KEY: {
                const.DESCRIPTION_KEY: normalized_data.get(const.INFO_KEY, {}).get(const.DESCRIPTION_KEY,
                                                                                   const.DEFAULT_DESCRIPTION),
                const.DATASET_NAME_KEY: normalized_data.get(const.INFO_KEY, {}).get(const.DATASET_NAME_KEY,
                                                                                    const.DEFAULT_DATASET_NAME),
                const.DATASET_TYPE_KEY: normalized_data.get(const.INFO_KEY, {}).get(const.DATASET_TYPE_KEY,
                                                                                    const.DEFAULT_DATASET_TYPE),
                const.DATE_CREATED_KEY: normalized_data.get(const.INFO_KEY, {}).get(
                    const.DATE_CREATED_KEY, datetime.datetime.now().strftime(const.DEFAULT_DATE_FORMAT))
            },
            const.IMAGES_KEY: [],
            const.ANNOTATIONS_KEY: [],
            const.CATEGORIES_KEY: [],
            const.LICENSES_KEY: normalized_data.get(
                const.LICENSES_KEY, [const.DEFAULT_LICENSE])
        }

        for normalized_image in normalized_data.get(const.IMAGES_KEY, []):
            coco_image = {
                const.ID_KEY: normalized_image.get(const.ID_KEY),
                const.FILE_NAME_KEY: normalized_image.get(const.FILE_NAME_KEY),
                const.WIDTH_KEY: normalized_image.get(const.WIDTH_KEY, 0),
                const.HEIGHT_KEY: normalized_image.get(const.HEIGHT_KEY, 0),
                const.SPLIT_KEY: normalized_image.get(const.SPLIT_KEY, ""),
                const.SOURCE_ZIP_KEY: normalized_image.get(const.SOURCE_ZIP_KEY, None),
                const.IMAGE_CONTENT_KEY: normalized_image.get(
                    const.IMAGE_CONTENT_KEY, None)
            }
            coco_dataset[const.IMAGES_KEY].append(coco_image)

        annotation_id = 1
        for normalized_annotation in normalized_data.get(const.ANNOTATIONS_KEY, []):
            segmentation = normalized_annotation.get(
                const.SEGMENTATION_KEY, [])
            if segmentation and (
                    not isinstance(segmentation, list) or not all(
                        isinstance(seg, list) for seg in segmentation)):
                logger.warning(
                    f"Skipping segmentation for annotation {normalized_annotation.get(const.ID_KEY, 'Unknown')} due to invalid format.")
                continue

            coco_annotation = {
                const.ID_KEY: annotation_id,
                const.IMAGE_ID_KEY: normalized_annotation.get(const.IMAGE_ID_KEY),
                const.CATEGORY_ID_KEY: normalized_annotation.get(const.CATEGORY_ID_KEY),
                const.BBOX_KEY: normalized_annotation.get(const.BBOX_KEY, []),
                const.SEGMENTATION_KEY: segmentation,
                const.AREA_KEY: normalized_annotation.get(const.AREA_KEY, 0.0),
                const.ISCROWD_KEY: normalized_annotation.get(
                    const.ISCROWD_KEY, 0)
                # Corrected from 'ann' to 'normalized_annotation'
            }
            coco_dataset[const.ANNOTATIONS_KEY].append(coco_annotation)
            annotation_id += 1

        for normalized_category in normalized_data.get(const.CATEGORIES_KEY, []):
            coco_category = {
                const.ID_KEY: normalized_category.get(const.ID_KEY),
                const.NAME_KEY: normalized_category.get(const.NAME_KEY),
                const.SUPERCATEGORY_KEY: normalized_category.get(
                    const.SUPERCATEGORY_KEY, const.DEFAULT_SUPERCATEGORY)
            }
            coco_dataset[const.CATEGORIES_KEY].append(coco_category)

        try:
            if not validate_data(coco_dataset, self.coco_schema, context=const.COCO_DATASET_CONTEXT):
                raise ValidationError(
                    f"COCO dataset validation failed after conversion.")

        except ValidationError as e:
            raise

        if destination:
            self.save(coco_dataset, destination)
            return None
        return coco_dataset

    def save(
            self,
            data: dict,
            destination: Union[str, IO[bytes], None] = None
    ):
        """
        Saves the COCO dataset to a zip file or an in-memory BytesIO object.

        The dataset is organized into 'train', 'test', and 'valid' subdirectories within the zip,
        each containing an `_annotations.coco.json` file and the corresponding images.

        :param data: The COCO dataset dictionary to be saved.
        :param destination: (Optional) The destination to save the converted dataset. Can be a file path
                            or an in-memory object (BytesIO). If None, an in-memory BytesIO object is returned.
        :return: An in-memory BytesIO object if `destination` was None, otherwise None.
        :raises ValidationError: If the COCO dataset does not conform to the expected schema before saving.
        """
        if destination == None:
            destination = io.BytesIO()

        try:
            if not validate_data(data, self.coco_schema, context=const.COCO_DATASET_CONTEXT):
                raise ValidationError(
                    f"COCO dataset validation failed before saving.")
        except ValidationError as e:
            raise

        with create_zip_writer(destination) as zip_file:
            for split in [const.TRAIN_SPLIT, const.VALID_SPLIT, const.TEST_SPLIT]:
                split_images = [
                    img for img in data.get(const.IMAGES_KEY, [])
                    if (img.get(const.SPLIT_KEY,
                                "").lower() in const.VALID_SPLIT_ALIASES if split == const.VALID_SPLIT else img.get(
                        const.SPLIT_KEY, "").lower() == split)
                ]

                split_annotations = [
                    ann for ann in data.get(const.ANNOTATIONS_KEY, [])
                    if ann.get(const.IMAGE_ID_KEY) in {img.get(const.ID_KEY) for img in split_images}
                ]

                if not split_images and not split_annotations:
                    logger.info(
                        f"{const.SKIPPING_SPLIT} '{split}': No images or annotations found.")
                    continue

                split_coco_json_data = create_coco_dict(
                    data, split_images, split_annotations, split)

                json_filename = const.ANNOTATION_JSON_PATH_TEMPLATE.format(
                    split)
                zip_file.writestr(json_filename, json.dumps(
                    split_coco_json_data, indent=4))

                images_dir_in_zip = f"{split}/"
                zip_file.writestr(images_dir_in_zip, b'')

                for image in split_images:
                    image_path_in_zip = os.path.join(
                        images_dir_in_zip, image.get(const.FILE_NAME_KEY))
                    save_image_to_zip(image, image_path_in_zip, zip_file)

        if isinstance(destination, io.BytesIO):
            destination.seek(0)
            return destination


class YOLOConvertor(BaseConvertor):
    """
    A convertor class for YOLO dataset format, supporting both standard YOLO and YOLOv8-obb formats.
    Handles loading, normalizing, converting to, and saving from YOLO format.
    """

    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(__file__)
        yolo_schema_path = os.path.join(
            current_dir, '..', 'convertors', 'schema', YOLO_SCHEMA_FILE)
        normalizer_schema_path = os.path.join(
            current_dir, '..', 'convertors', 'schema', NORMALIZER_SCHEMA_FILE)
        yolo_obb_schema_path = os.path.join(
            current_dir, '..', 'convertors', 'schema', YOLOv8obb_SCHEMA_FILE)

        yolo_schema_path = os.path.abspath(yolo_schema_path)
        normalizer_schema_path = os.path.abspath(normalizer_schema_path)
        yolo_obb_schema_path = os.path.abspath(yolo_obb_schema_path)

        try:  # FIX: Added try-except for yolo_schema
            with open(yolo_schema_path, 'r') as schema_file:
                self.yolo_schema = json.load(schema_file)
        except Exception as e:
            logger.error(
                f"Failed to load YOLO schema from {yolo_schema_path}: {e}")
            raise

        try:  # FIX: Added try-except for normalizer_schema
            with open(normalizer_schema_path, 'r') as schema_file:
                self.normalizer_schema = json.load(schema_file)
        except Exception as e:
            logger.error(
                f"Failed to load Normalizer schema from {normalizer_schema_path}: {e}")
            raise

        try:  # FIX: Added try-except for yolo_obb_schema
            with open(yolo_obb_schema_path, 'r') as schema_file:
                self.yolo_obb_schema = json.load(schema_file)
        except Exception as e:
            logger.error(
                f"Failed to load YOLOv8-obb schema from {yolo_obb_schema_path}: {e}")
            raise

    def load(
            self,
            source: Union[str, IO[bytes]]
    ) -> dict:
        """
        Loads a YOLO-formatted dataset (standard or YOLOv8-obb) from a zip file, directory,
        or in-memory BytesIO object.

        This method detects the YOLO subtype (standard or OBB) based on the structure of the
        'names' key in the `data.yaml` file.

        :param source: The source of the YOLO dataset, which can be:
                       - A string path to a zip file.
                       - A string path to a directory.
                       - An already open `zipfile.ZipFile` object.
                       - An in-memory `IO[bytes]` object (e.g., `BytesIO`) containing a zip file.
        :return: A dictionary representing the loaded YOLO dataset, including image content
                 and a 'format_subtype' key indicating if it's 'yolo' or 'yolov8-obb'.
        :raises ValueError: If the source type is unsupported or the path is invalid,
                            or if the YOLO subtype cannot be determined.
        :raises ValidationError: If loaded YOLO data does not conform to the expected schema
                                 (standard YOLO or YOLOv8-obb schema based on detected subtype).
        """
        subdirs = [TRAIN_DIR, VALID_DIR, TEST_DIR]
        dataset = {
            DATASET_IMAGES_KEY: [],
            DATASET_CLASS_NAMES_KEY: [],
            DATASET_LICENSES_KEY: [],
            'format_subtype': None  # Add this key to store the detected subtype
        }

        # Determine if it's a zip or directory and load data.yaml first
        data_yaml = {}
        if isinstance(source, str):
            if zipfile.is_zipfile(source):
                with zipfile.ZipFile(source, 'r') as zip_file:
                    if YOLO_YAML_FILENAME in zip_file.namelist():
                        with zip_file.open(YOLO_YAML_FILENAME) as file:
                            data_yaml = yaml.safe_load(file)
            elif os.path.isdir(source):
                data_yaml_path = os.path.join(source, YOLO_YAML_FILENAME)
                if os.path.exists(data_yaml_path):
                    with open(data_yaml_path, 'r') as file:
                        data_yaml = yaml.safe_load(file)
        elif isinstance(source, zipfile.ZipFile):  # If source is already an open ZipFile
            if YOLO_YAML_FILENAME in source.namelist():
                with source.open(YOLO_YAML_FILENAME) as file:
                    data_yaml = yaml.safe_load(file)
        elif hasattr(source, 'read'):  # If source is BytesIO
            source.seek(0)
            # FIX: Added 'with' statement for BytesIO
            with zipfile.ZipFile(source, 'r') as temp_zip_file:
                if YOLO_YAML_FILENAME in temp_zip_file.namelist():
                    with temp_zip_file.open(YOLO_YAML_FILENAME) as file:
                        data_yaml = yaml.safe_load(file)

        names_data = data_yaml.get('names')
        schema_to_validate = None

        # Refine format detection based on 'names' type
        if isinstance(names_data, list):
            # This is a standard YOLO format
            logger.info("Detected standard YOLO format (names as list).")
            dataset['format_subtype'] = CONVERTOR_FORMAT_YOLO
            if isinstance(source, str) and zipfile.is_zipfile(source):
                with zipfile.ZipFile(source, 'r') as zip_file:
                    loadhelper_yolo_from_zip(zip_file, dataset, subdirs)
            elif isinstance(source, str) and os.path.isdir(source):
                loadhelper_yolo_from_directory(source, dataset, subdirs)
            elif isinstance(source, zipfile.ZipFile):
                loadhelper_yolo_from_zip(source, dataset, subdirs)
            elif hasattr(source, 'read'):
                source.seek(0)
                with zipfile.ZipFile(source) as zip_file:
                    loadhelper_yolo_from_zip(zip_file, dataset, subdirs)
            else:
                raise ValueError("Unsupported source type for YOLO load.")

            # Set class names after loading
            dataset[DATASET_CLASS_NAMES_KEY] = [
                str(name) for name in names_data]
            dataset[LICENSES_KEY] = [{ID_KEY: 1, NAME_KEY: data_yaml.get('license', 'Unknown License'),
                                      "url": data_yaml.get('license_url', '')}]
            schema_to_validate = self.yolo_schema

        elif isinstance(names_data, dict):
            # This indicates a YOLOv8-obb format (or similar YOLO variant with dict names)
            logger.info(
                "Detected YOLO format with dictionary names. Loading as YOLOv8-obb.")
            dataset['format_subtype'] = CONVERTOR_FORMAT_YOLOv8_obb
            if isinstance(source, str) and zipfile.is_zipfile(source):
                with zipfile.ZipFile(source, 'r') as zip_file:
                    loadhelper_yolov8obb_from_zip(zip_file, dataset, subdirs)
            elif isinstance(source, str) and os.path.isdir(source):
                loadhelper_yolov8obb_from_directory(source, dataset, subdirs)
            elif isinstance(source, zipfile.ZipFile):
                loadhelper_yolov8obb_from_zip(source, dataset, subdirs)
            elif hasattr(source, 'read'):
                source.seek(0)
                with zipfile.ZipFile(source) as zip_file:
                    loadhelper_yolov8obb_from_zip(zip_file, dataset, subdirs)
            else:
                raise ValueError(
                    "Unsupported source type for YOLOv8-obb load initiated from YOLOConvertor.")
            schema_to_validate = self.yolo_obb_schema

        else:
            raise ValueError(
                f"Could not determine YOLO subtype: 'names' key in data.yaml is missing or not a list/dict (got {type(names_data)}).")

        try:
            if schema_to_validate:
                validate(instance=dataset, schema=schema_to_validate)
            else:
                logger.warning(
                    "No specific schema found for validation after loading YOLO data.")
        except ValidationError as e:
            raise
        return dataset

    def normalize(
            self,
            data: dict
    ) -> dict:
        """
        Normalize the YOLO dataset into a standardized format, supporting both object detection and segmentation datasets.

        This method processes the input YOLO dataset and converts it into a normalized format that is compatible
        with downstream applications, such as COCO-like object detection or segmentation tasks.

        :param data:
            A dictionary representing the YOLO dataset (standard or YOLOv8-obb). The YOLO dataset should include:
            - `images`: A list of dictionaries, each containing image metadata (file names, content, etc.) and
              annotations (bounding boxes or segmentation data).
            - `class_names`: A list of class names used in the dataset.
            - `format_subtype`: Indicates if the original format was 'yolo' or 'yolov8-obb'.
            - Optionally, `licenses`: A list of license dictionaries associated with the dataset.

        :return:
            A dictionary representing the normalized dataset. The normalized dataset includes:
            - `info`: General metadata about the dataset (e.g., description, dataset name, type, creation date).
            - `images`: A list of image dictionaries with normalized metadata (file names, dimensions, split, etc.).
            - `annotations`: A list of annotation dictionaries for each image, including bounding boxes or segmentation data.
            - `categories`: A list of object categories from the dataset.
            - `licenses`: A list of licenses from the dataset (if provided).
            - `nc`: The number of categories in the dataset.
            - `names`: A list of category names.
            - `format_subtype`: Carries the detected format subtype.

        Raises:
            ValidationError: If the normalized dataset does not conform to the Normalizer schema.

        Notes:
            - The method automatically detects whether the dataset includes object detection or segmentation data by
              inspecting annotations. It sets the `dataset_type` field to "Object Detection" or "Segmentation" accordingly.
            - Bounding boxes (in YOLO format) are converted to COCO's "xywh" format (x, y, width, height), and segmentation
              data is transformed into a compatible format if present.
            - For segmentation data, the method calculates the bounding box and area from the segmentation points using
              OpenCV functions.
            - If an image's dimensions (width, height) are missing or invalid, the image and its annotations are skipped.

        Processing Steps:
            1. The method first checks if any segmentation data is present in the annotations. If found, the dataset type is set to "Segmentation".
            2. Each image in the dataset is processed: its metadata is extracted, and dimensions are calculated from the content if provided.
            3. Annotations are converted from YOLO's format to a normalized format. Bounding boxes are translated from YOLO's center format (cx, cy, width, height) to COCO's "xywh" format. Segmentation data is processed if present.
            4. Categories are added to the dataset, and a mapping between class IDs and category names is created.
            5. The resulting dataset is validated against the Normalizer schema to ensure its correctness.
        """

        # Determine the dataset type (Object Detection or Segmentation)
        dataset_type = OBJECT_DETECTION_TYPE
        for image in data.get(DATASET_IMAGES_KEY, []):
            for ann in image.get(ANNOTATIONS_KEY, []):
                if SEGMENTATION_KEY in ann and ann[SEGMENTATION_KEY]:
                    dataset_type = SEGMENTATION_TYPE
                    break

        # Determine description based on format subtype
        description_prefix = CONVERTED_FROM_YOLO
        dataset_name = YOLO_DATASET_NAME
        if data.get('format_subtype') == CONVERTOR_FORMAT_YOLOv8_obb:
            description_prefix = CONVERTED_FROM_YOLOv8_obb
            dataset_name = YOLOv8_obb_DATASET_NAME

        normalized_dataset = {
            INFO_KEY: {
                DESCRIPTION_KEY: f"{description_prefix} ({dataset_type})",
                DATASET_NAME_KEY: dataset_name,
                DATASET_TYPE_KEY: dataset_type,
                DATE_CREATED_KEY: datetime.datetime.now().strftime(DATE_FORMAT_YOLO),
                SPLITS_KEY: {}
            },
            DATASET_IMAGES_KEY: [],
            ANNOTATIONS_KEY: [],
            CATEGORIES_KEY: [],
            DATASET_LICENSES_KEY: data.get(DATASET_LICENSES_KEY, []),
            NC_KEY: len(data.get(DATASET_CLASS_NAMES_KEY, [])),
            NAMES_KEY: data.get(DATASET_CLASS_NAMES_KEY, []),
            # Pass the subtype through
            'format_subtype': data.get('format_subtype')
        }

        image_id_map = {}
        annotation_id = 1

        for idx, yolo_image in enumerate(data.get(DATASET_IMAGES_KEY, [])):
            image_content = yolo_image.get(IMAGE_CONTENT_KEY)
            file_name = yolo_image[FILE_NAME_KEY]
            split = yolo_image[SPLIT_KEY]

            width, height = 0, 0
            if image_content:
                width, height = get_image_dimensions(image_content)

            if width == 0 or height == 0:
                logger.warning(
                    f"Skipping image {file_name} due to invalid dimensions (width={width}, height={height}).")
                continue

            normalized_image = {
                ID_KEY: idx,
                FILE_NAME_KEY: file_name,
                WIDTH_KEY: width,
                HEIGHT_KEY: height,
                SPLIT_KEY: split,
                SOURCE_ZIP_KEY: yolo_image.get(SOURCE_ZIP_KEY),
                IMAGE_CONTENT_KEY: image_content
            }
            image_id_map[file_name] = idx
            normalized_dataset[DATASET_IMAGES_KEY].append(normalized_image)

        for yolo_image in data.get(DATASET_IMAGES_KEY, []):
            image_id = image_id_map.get(yolo_image[FILE_NAME_KEY])
            if image_id is None:
                continue

            width = normalized_dataset[DATASET_IMAGES_KEY][image_id][WIDTH_KEY]
            height = normalized_dataset[DATASET_IMAGES_KEY][image_id][HEIGHT_KEY]

            for ann in yolo_image.get(ANNOTATIONS_KEY, []):
                area = 0
                segmentation = []
                bbox = []
                is_valid_annotation_for_processing = False

                if SEGMENTATION_KEY in ann and ann[SEGMENTATION_KEY]:
                    segmentation_data = ann[SEGMENTATION_KEY]
                    if segmentation_data and isinstance(segmentation_data, list) and len(segmentation_data) > 0:
                        # Segmentation data from loadhelper is a list containing a single flat list of normalized points
                        # Denormalize them to pixel coordinates
                        denormalized_segmentation_points = [
                            coord * width if i % 2 == 0 else coord * height
                            # Access the inner flat list
                            for i, coord in enumerate(segmentation_data[0])
                        ]

                        # Reshape for OpenCV contour functions (expects Nx2 array)
                        flat_seg_np = np.array(
                            denormalized_segmentation_points).reshape(-1, 2).astype(np.float32)

                        # Need at least 3 points for a valid contour
                        if flat_seg_np.shape[0] >= 3:
                            area = cv2.contourArea(flat_seg_np)
                            x, y, w, h = cv2.boundingRect(flat_seg_np)
                            # Ensure float output
                            bbox = [float(x), float(y), float(w), float(h)]
                            segmentation = [
                                # Keep as list of list for consistency in normalized data
                                denormalized_segmentation_points]
                            is_valid_annotation_for_processing = True
                        else:
                            logger.warning(
                                f"Skipping segmentation for annotation {ann.get(CLASS_ID_KEY, 'Unknown')} due to insufficient points after denormalization. Points: {flat_seg_np.shape[0]}")
                    else:
                        logger.warning(
                            f"Skipping annotation {ann.get(CLASS_ID_KEY, 'Unknown')} because segmentation data is malformed: {segmentation_data}")

                elif BBOX_KEY in ann and ann[BBOX_KEY]:
                    current_bbox_data = ann[BBOX_KEY]
                    if data.get('format_subtype') == CONVERTOR_FORMAT_YOLOv8_obb and isinstance(current_bbox_data,
                                                                                                list) and len(
                            current_bbox_data) == 8:  # YOLOv8 OBB
                        bbox = convert_yolo_obb_to_coco(
                            current_bbox_data, width, height)
                        # Area of axis-aligned bbox for OBB
                        area = bbox[2] * bbox[3]
                        is_valid_annotation_for_processing = True
                    # Handle standard YOLO bounding boxes (list of 4 floats)
                    elif data.get('format_subtype') == CONVERTOR_FORMAT_YOLO and isinstance(current_bbox_data,
                                                                                            list) and len(
                            current_bbox_data) == 4:
                        # FIX: For standard YOLO, the bbox is already in normalized cxcywh format from loadhelpers.
                        # It needs to be converted to COCO xywh pixel format for the normalized dataset.
                        # convert_bbox_yolo_to_coco expects normalized values and image dimensions to convert to pixels.
                        bbox = convert_bbox_yolo_to_coco({const.BBOX_KEY: current_bbox_data}, width,
                                                         height)  # Pass as dict to match function signature
                        area = bbox[2] * bbox[3]
                        is_valid_annotation_for_processing = True
                    else:
                        logger.warning(
                            f"Skipping bbox for annotation {ann.get(CLASS_ID_KEY, 'Unknown')} due to unexpected bbox format: {current_bbox_data}. Expected 8-element list (OBB) or 4-element list (standard YOLO).")
                else:
                    logger.warning(
                        f"Skipping annotation {ann.get(CLASS_ID_KEY, 'Unknown')} as it has no valid bbox or segmentation data.")

                if is_valid_annotation_for_processing:
                    normalized_annotation = {
                        ID_KEY: annotation_id,
                        IMAGE_ID_KEY: image_id,
                        CATEGORY_ID_KEY: ann[CLASS_ID_KEY],
                        BBOX_KEY: bbox,
                        SEGMENTATION_KEY: segmentation,
                        AREA_KEY: area,
                        ISCROWD_KEY: 0,
                        BBOX_FORMAT_KEY: BBOX_FORMAT_VALUE
                    }
                    normalized_dataset[ANNOTATIONS_KEY].append(
                        normalized_annotation)
                    annotation_id += 1
                else:
                    logger.warning(
                        f"Annotation {ann.get(CLASS_ID_KEY, 'Unknown')} on image {yolo_image.get(FILE_NAME_KEY, 'Unknown')} skipped entirely as no valid data could be parsed.")

        for idx, class_name in enumerate(data.get(DATASET_CLASS_NAMES_KEY, [])):
            normalized_category = {
                ID_KEY: idx,
                NAME_KEY: class_name,
                SUPERCATEGORY_KEY: SUPERCATEGORY_DEFAULT
            }
            normalized_dataset[CATEGORIES_KEY].append(normalized_category)

        if not validate_data(normalized_dataset, self.normalizer_schema, context=NORMALIZED_DATASET_CONTEXT):
            raise ValidationError(NORMALIZED_DATASET_VALIDATION_ERROR)
        return normalized_dataset

    def convert(
            self,
            normalized_data: dict,
            target_format_actual: str,
            destination: Union[str, IO[bytes], None] = None
    ) -> Union[Any, None]:
        """
        Converts the normalized dataset into the appropriate YOLO format (standard or YOLOv8-obb).
        If a destination is provided, it saves the converted data to that destination and returns None.
        Otherwise, it returns the converted dataset dictionary.

        This method determines the target YOLO subtype based on the 'target_format_actual' parameter.
        It then converts bounding box annotations accordingly.

        :param normalized_data: The dataset in normalized format, including 'format_subtype'.
        :param target_format_actual: The actual target YOLO format ('yolo' or 'yolov8-obb').
        :param destination: (Optional) The destination to save the converted dataset (file path or BytesIO object).
        :return: The converted dataset dictionary if no destination is provided, otherwise None.
        """
        yolo_images = []
        image_to_annotations = {ann[const.IMAGE_ID_KEY]: []
                                for ann in normalized_data.get(const.ANNOTATIONS_KEY, [])}

        for annotation in normalized_data.get(const.ANNOTATIONS_KEY, []):
            image_to_annotations[annotation[const.IMAGE_ID_KEY]].append(
                annotation)

        target_yolo_output_subtype = target_format_actual  # Use the actual target format

        for normalized_image in normalized_data.get(const.DATASET_IMAGES_KEY, []):
            annotations = image_to_annotations.get(
                normalized_image[const.ID_KEY], [])
            yolo_annotations = []
            logger.debug(
                f"Processing image: {normalized_image.get(const.FILE_NAME_KEY)}")
            logger.debug(
                f"Number of annotations for this image: {len(annotations)}")

            img_width, img_height = normalized_image[const.WIDTH_KEY], normalized_image[const.HEIGHT_KEY]

            for normalized_annotation in annotations:
                yolo_annotation_entry = None  # Initialize to None for each annotation
                class_id = normalized_annotation[const.CATEGORY_ID_KEY]
                logger.debug(
                    f"  Normalized annotation before YOLO conversion: {normalized_annotation}")

                # --- Attempt to process SEGMENTATION first ---
                if const.SEGMENTATION_KEY in normalized_annotation and normalized_annotation[const.SEGMENTATION_KEY]:
                    # process_segmentation_data here is used to normalize pixel coords to 0-1 range
                    segmentation_result = process_segmentation_data(
                        normalized_annotation[const.SEGMENTATION_KEY], img_width, img_height
                    )
                    # segmentation_result from process_segmentation_data is list[list[float]] (normalized)
                    # Flatten it to a single list for YOLO format if it contains one polygon
                    flattened_segmentation = []
                    if segmentation_result and isinstance(segmentation_result, list) and len(segmentation_result) > 0:
                        # Assuming single polygon segmentation for YOLO .txt format
                        flattened_segmentation = segmentation_result[0]

                    if flattened_segmentation:
                        yolo_annotation_entry = {
                            const.CLASS_ID_KEY: class_id,
                            const.SEGMENTATION_KEY: flattened_segmentation,  # Pass the flattened list
                            const.BBOX_KEY: []  # Explicitly empty bbox if segmentation is used
                        }
                        logger.debug(
                            f"  Converted segmentation for class {class_id}: {yolo_annotation_entry}")
                    else:
                        logger.warning(
                            f"Skipping segmentation for annotation {normalized_annotation.get(const.ID_KEY, 'Unknown')} due to empty or invalid processed segmentation.")

                # --- If no valid segmentation entry was created, or segmentation was not present, try BOUNDING BOX ---
                if yolo_annotation_entry is None and const.BBOX_KEY in normalized_annotation and normalized_annotation[
                        const.BBOX_KEY]:
                    bbox_coco_pixels = normalized_annotation[const.BBOX_KEY]
                    logger.debug(
                        f"  Processing bbox for class {class_id}. COCO pixels: {bbox_coco_pixels}")

                    if normalized_annotation.get(const.BBOX_FORMAT_KEY) == const.BBOX_FORMAT_VALUE:
                        converted_bbox = []
                        # Correctly use target_yolo_output_subtype which will be 'yolo' or 'yolov8-obb'
                        if target_yolo_output_subtype == const.CONVERTOR_FORMAT_YOLOv8_obb:
                            converted_bbox = convert_coco_to_yolo_obb(
                                bbox_coco_pixels, img_width, img_height)
                        elif target_yolo_output_subtype == const.CONVERTOR_FORMAT_YOLO:  # Explicitly check for standard YOLO
                            converted_bbox = convert_bbox_to_yolo_format(
                                bbox_coco_pixels, img_width, img_height)
                        else:
                            logger.warning(
                                f"Unsupported target YOLO subtype for bbox conversion: {target_yolo_output_subtype}")

                        if converted_bbox:  # Only create entry if bbox conversion was successful
                            yolo_annotation_entry = {
                                const.CLASS_ID_KEY: class_id,
                                const.BBOX_KEY: converted_bbox,
                                const.SEGMENTATION_KEY: []  # Explicitly empty segmentation if bbox is used
                            }
                            logger.debug(
                                f"  Converted bbox for class {class_id} to {target_yolo_output_subtype}: {yolo_annotation_entry}")
                        else:
                            logger.warning(
                                f"Skipping bbox for annotation {normalized_annotation.get(const.ID_KEY, 'Unknown')} due to failed bbox conversion to target format {target_yolo_output_subtype}. Converted bbox was empty.")
                    else:
                        logger.warning(
                            f"Skipping bbox for annotation {normalized_annotation.get(const.ID_KEY, 'Unknown')} due to unsupported bbox format: {normalized_annotation.get(const.BBOX_FORMAT_KEY)}.")

                # --- Add the successfully created entry to yolo_annotations ---
                if yolo_annotation_entry:
                    yolo_annotations.append(yolo_annotation_entry)
                else:
                    logger.warning(
                        f"Annotation {normalized_annotation.get(const.ID_KEY, 'Unknown')} on image {normalized_image.get(const.FILE_NAME_KEY, 'Unknown')} could not be converted to a valid YOLO entry (no valid bbox or segmentation).")

            yolo_image = {
                const.FILE_NAME_KEY: normalized_image[const.FILE_NAME_KEY],
                const.ANNOTATIONS_KEY: yolo_annotations,
                const.SPLIT_KEY: normalized_image[const.SPLIT_KEY],
                const.SOURCE_ZIP_KEY: normalized_image.get(const.SOURCE_ZIP_KEY),
                const.IMAGE_CONTENT_KEY: normalized_image.get(const.IMAGE_CONTENT_KEY),
                const.WIDTH_KEY: normalized_image[const.WIDTH_KEY],
                const.HEIGHT_KEY: normalized_image[const.HEIGHT_KEY]
            }
            yolo_images.append(yolo_image)

        yolo_dataset = {
            const.DATASET_IMAGES_KEY: yolo_images,
            const.DATASET_CLASS_NAMES_KEY: normalized_data.get(const.NAMES_KEY, []),
            'format_subtype': target_yolo_output_subtype  # Set the output subtype here
        }

        if destination:
            self.save(yolo_dataset, destination)
            return None
        return yolo_dataset

    def save(
            self,
            data: dict,
            destination: Union[str, IO[bytes], None] = None
    ):
        """
        Saves the YOLO dataset (standard or YOLOv8-obb) to a zip file or an in-memory BytesIO object.

        The dataset is organized into 'train', 'valid', and 'test' subdirectories,
        each containing an 'images' folder and a 'labels' folder.
        A `data.yaml` file is also created at the root.

        :param data: The YOLO dataset dictionary to be saved.
                     Should include a 'format_subtype' key to determine the validation schema.
        :param destination: (Optional) The destination to save the converted dataset. Can be a file path
                            or an in-memory object (BytesIO). If None, an in-memory BytesIO object is returned.
        :return: An in-memory BytesIO object if `destination` was None, otherwise None.
        :raises ValidationError: If the YOLO dataset does not conform to the expected schema
                                 (standard YOLO or YOLOv8-obb schema based on subtype).
        """
        schema_to_validate = self.yolo_schema
        if data.get('format_subtype') == CONVERTOR_FORMAT_YOLOv8_obb:
            schema_to_validate = self.yolo_obb_schema

        if not validate_data(data, schema_to_validate, context=YOLO_DATASET_CONTEXT):
            raise ValidationError(YOLO_DATASET_VALIDATION_FAILED)

        if destination is None:
            destination = io.BytesIO()

        with create_zip_writer(destination) as zip_file:
            # Pass the target_format_actual from the data dictionary to generate_yaml_content
            yaml_content = generate_yaml_content(
                data[DATASET_CLASS_NAMES_KEY], data['format_subtype'])
            zip_file.writestr(DATA_YAML_FILE, yaml_content)

            created_dirs = set()

            for image in data[DATASET_IMAGES_KEY]:
                split = VALID_DIR if image[SPLIT_KEY] == VALIDATION_SPLIT else image[SPLIT_KEY]
                split_dir = f"{split}/images"
                labels_dir = f"{split}/labels"

                if split_dir not in created_dirs:
                    zip_file.writestr(f"{split_dir}/", b'')
                    created_dirs.add(split_dir)

                if labels_dir not in created_dirs:
                    zip_file.writestr(f"{labels_dir}/", b'')
                    created_dirs.add(labels_dir)

                if image.get(IMAGE_CONTENT_KEY):
                    zip_file.writestr(os.path.join(
                        split_dir, image[FILE_NAME_KEY]), image[IMAGE_CONTENT_KEY])
                else:
                    logger.warning(
                        f"{SKIPPING_IMAGE} {image.get(FILE_NAME_KEY, 'Unknown')} for split {split} due to missing content.")

                label_file_name = os.path.splitext(
                    image[FILE_NAME_KEY])[0] + TXT_EXT
                label_zip_path = os.path.join(labels_dir, label_file_name)
                width, height = image.get(WIDTH_KEY), image.get(HEIGHT_KEY)

                if width is not None and height is not None and width > 0 and height > 0:
                    label_content = create_label_content(
                        image[ANNOTATIONS_KEY], width, height)
                    if label_content.strip():
                        zip_file.writestr(label_zip_path, label_content)
                    else:
                        logger.info(
                            f"Skipping empty label file for {image.get(FILE_NAME_KEY, 'Unknown')}.")
                else:
                    logger.warning(
                        f"Skipping label file for {image.get(FILE_NAME_KEY, 'Unknown')} due to invalid image dimensions ({width}x{height}).")

        if isinstance(destination, io.BytesIO):
            destination.seek(0)
            return destination


class BinaExpertsConvertor(BaseConvertor):
    """
    A convertor class for BinaExperts dataset format.
    Handles loading, normalizing, converting to, and saving from BinaExperts format.
    """

    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(__file__)
        binaexperts_schema_path = os.path.join(
            current_dir, '..', 'convertors', 'schema', BINAEXPERTS_SCHEMA_FILE)
        normalizer_schema_path = os.path.join(
            current_dir, '..', 'convertors', 'schema', NORMALIZER_SCHEMA_FILE)
        binaexperts_schema_path = os.path.abspath(binaexperts_schema_path)
        normalizer_schema_path = os.path.abspath(normalizer_schema_path)
        try:  # FIX: Added try-except for binaexperts_schema
            with open(binaexperts_schema_path, 'r') as schema_file:
                self.binaexperts_schema = json.load(schema_file)
        except Exception as e:
            logger.error(
                f"Failed to load BinaExperts schema from {binaexperts_schema_path}: {e}")
            raise
        try:  # FIX: Added try-except for normalizer_schema
            with open(normalizer_schema_path, 'r') as schema_file:
                self.normalizer_schema = json.load(schema_file)
        except Exception as e:
            logger.error(
                f"Failed to load Normalizer schema from {normalizer_schema_path}: {e}")
            raise

    def load(self, source: Union[str, IO[bytes]]) -> Dict:
        """
        Loads a BinaExperts-formatted dataset from a zip file, directory, or in-memory BytesIO object.

        This method supports loading BinaExperts datasets where COCO-style annotation
        files (`train_coco.json`, `val_coco.json`, `test_coco.json`) are located in a 'cocos'
        subdirectory, and images are in split-specific directories (e.g., 'train_images').

        :param source: The source of the BinaExperts dataset, which can be:
                       - A string path to a zip file.
                       - A string path to a directory.
                       - An already open `zipfile.ZipFile` object.
                       - An in-memory `IO[bytes]` object (e.g., `BytesIO`) containing a zip file.
        :return: A dictionary representing the loaded BinaExperts dataset.
        :raises ValueError: If the source type is unsupported or the path is invalid.
        :raises ValidationError: If loaded BinaExperts data does not conform to the expected schema.
        """
        subdir_mapping = {
            TRAIN_SPLIT: TRAIN_IMAGES_DIR,
            TEST_SPLIT: TEST_IMAGES_DIR,
            VALID_SPLIT: VALIDATION_IMAGES_DIR
        }
        annotation_files = {
            TRAIN_SPLIT: TRAIN_COCO_FILE,
            TEST_SPLIT: TEST_COCO_FILE,
            VALID_SPLIT: VALID_COCO_FILE
        }

        dataset = {
            INFO_KEY: {},
            IMAGES_KEY: [],
            ANNOTATIONS_KEY: [],
            CATEGORIES_KEY: [],
            LICENSES_KEY: []
        }

        if isinstance(source, str):
            if zipfile.is_zipfile(source):
                with zipfile.ZipFile(source, 'r') as zip_file:
                    for split, subdir in subdir_mapping.items():
                        annotation_path = f"{COCOS_DIR}/{annotation_files[split]}"
                        if annotation_path not in zip_file.namelist():
                            logger.info(
                                f"{SKIPPING_SUBDIR} {annotation_path} in zip. No annotation file found.")
                            continue
                        with zip_file.open(annotation_path) as file:
                            coco_data = json.load(file)
                            if not validate_data(coco_data, self.binaexperts_schema, context=subdir):
                                continue
                        loadhelper_binaexperts_data(
                            coco_data, dataset, subdir, source_zip=zip_file)
            elif os.path.isdir(source):
                for split, subdir in subdir_mapping.items():
                    annotation_file = os.path.join(
                        source, COCOS_DIR, annotation_files[split])
                    if not os.path.isfile(annotation_file):
                        logger.info(
                            f"{SKIPPING_SUBDIR} {annotation_file} in directory. No annotation file found.")
                        continue
                    with open(annotation_file, 'r') as file:
                        coco_data = json.load(file)
                        if not validate_data(coco_data, self.binaexperts_schema, context=subdir):
                            continue
                    loadhelper_binaexperts_data(coco_data, dataset, subdir)
            else:
                raise ValueError(
                    f"Source '{source}' is not a valid zip file or directory path.")

        elif isinstance(source, zipfile.ZipFile):
            for split, subdir in subdir_mapping.items():
                annotation_path = f"{COCOS_DIR}/{annotation_files[split]}"
                if annotation_path not in source.namelist():
                    continue
                with source.open(annotation_path) as file:
                    coco_data = json.load(file)
                    if not validate_data(coco_data, self.binaexperts_schema, context=subdir):
                        continue
                loadhelper_binaexperts_data(
                    coco_data, dataset, subdir, source_zip=source)
        elif hasattr(source, 'read'):
            source.seek(0)
            with zipfile.ZipFile(source, 'r') as zip_file:
                for split, subdir in subdir_mapping.items():
                    annotation_path = f"{COCOS_DIR}/{annotation_files[split]}"
                    if annotation_path not in zip_file.namelist():
                        logger.info(
                            f"{SKIPPING_SUBDIR} {annotation_path} in zip. No annotation file found.")
                        continue
                    with zip_file.open(annotation_path) as file:
                        coco_data = json.load(file)
                        if not validate_data(coco_data, self.binaexperts_schema, context=subdir):
                            continue
                    loadhelper_binaexperts_data(
                        coco_data, dataset, subdir, source_zip=zip_file)
        else:
            raise ValueError("Unsupported source type for BinaExperts load.")

        return dataset

    def normalize(
            self,
            data: dict
    ) -> dict:
        """
        Normalizes a BinaExperts-formatted dataset dictionary into a standardized format.

        This method extracts key information from the BinaExperts dataset,
        including images, annotations, categories, and other metadata,
        and transforms it into a common, consistent structure.

        :param data: A dictionary representing the BinaExperts dataset.
        :return: A dictionary representing the normalized dataset.
        :raises ValidationError: If the normalized dataset does not conform to the Normalizer schema.
        """
        normalized_dataset = {
            INFO_KEY: {
                DESCRIPTION_KEY: CONVERTED_FROM_BINAEXPERTS,
                DATASET_NAME_KEY: data[INFO_KEY].get(DATASET_KEY, BINAEXPERTS_DATASET_NAME),
                DATASET_TYPE_KEY: data[INFO_KEY].get(DATASET_TYPE_KEY, DEFAULT_DATASET_TYPE),
                SPLITS_KEY: {}
            },
            IMAGES_KEY: [],
            ANNOTATIONS_KEY: [],
            CATEGORIES_KEY: [],
            LICENSES_KEY: data.get(LICENSES_KEY, []),
            NC_KEY: len(data[CATEGORIES_KEY]),
            NAMES_KEY: [cat[NAME_KEY] for cat in data[CATEGORIES_KEY]],
            ERRORS_KEY: data.get(ERRORS_KEY, []),
            LABELS_KEY: data.get(LABELS_KEY, []),
            CLASSIFICATIONS_KEY: data.get(CLASSIFICATIONS_KEY, []),
            AUGMENTATION_SETTINGS_KEY: data.get(AUGMENTATION_SETTINGS_KEY, {}),
            TILE_SETTINGS_KEY: data.get(TILE_SETTINGS_KEY, DEFAULT_TILE_SETTINGS),
            FALSE_POSITIVE_KEY: data.get(
                FALSE_POSITIVE_KEY, DEFAULT_FALSE_POSITIVE)
        }

        category_id_map = {cat[ID_KEY]: idx for idx,
                           cat in enumerate(data[CATEGORIES_KEY])}
        image_id_map = {image[ID_KEY]: idx for idx,
                        image in enumerate(data[IMAGES_KEY])}
        annotation_id = 1

        for image in data[IMAGES_KEY]:
            if WIDTH_KEY not in image or HEIGHT_KEY not in image:
                logger.warning(
                    f"Skipping image {image.get(FILE_NAME_KEY, 'Unknown')} due to missing width/height.")
                continue

            normalized_image = {
                ID_KEY: image_id_map[image[ID_KEY]],
                FILE_NAME_KEY: image[FILE_NAME_KEY],
                WIDTH_KEY: image[WIDTH_KEY],
                HEIGHT_KEY: image[HEIGHT_KEY],
                SPLIT_KEY: image.get(SPLIT_KEY, TRAIN_SPLIT),
                SOURCE_ZIP_KEY: image.get(SOURCE_ZIP_KEY),
                IMAGE_CONTENT_KEY: image.get(IMAGE_CONTENT_KEY)
            }
            normalized_dataset[IMAGES_KEY].append(normalized_image)

        for ann in data[ANNOTATIONS_KEY]:
            if ann[CATEGORY_ID_KEY] not in category_id_map or IMAGE_ID_KEY not in ann or ann[
                    IMAGE_ID_KEY] not in image_id_map:
                logger.warning(
                    f"Skipping annotation {ann.get(ID_KEY, 'Unknown')} due to missing category or image ID.")
                continue

            normalized_annotation = {
                ID_KEY: annotation_id,
                IMAGE_ID_KEY: image_id_map[ann[IMAGE_ID_KEY]],
                CATEGORY_ID_KEY: category_id_map[ann[CATEGORY_ID_KEY]],
                BBOX_KEY: ann.get(BBOX_KEY, []),
                SEGMENTATION_KEY: ann.get(SEGMENTATION_KEY, []),
                AREA_KEY: ann.get(AREA_KEY, 0.0),
                ISCROWD_KEY: ann.get(ISCROWD_KEY, 0),
                BBOX_FORMAT_KEY: BBOX_FORMAT_VALUE
            }
            normalized_dataset[ANNOTATIONS_KEY].append(normalized_annotation)
            annotation_id += 1

        for cat in data[CATEGORIES_KEY]:
            normalized_category = {
                ID_KEY: category_id_map[cat[ID_KEY]],
                NAME_KEY: cat[NAME_KEY],
                SUPERCATEGORY_KEY: SUPERCATEGORY_DEFAULT
            }
            normalized_dataset[CATEGORIES_KEY].append(normalized_category)

        if not validate_data(normalized_dataset, self.normalizer_schema, context=NORMALIZED_DATASET_CONTEXT):
            raise ValidationError(NORMALIZED_DATASET_VALIDATION_ERROR)

        return normalized_dataset

    def convert(
            self,
            normalized_data: dict,
            target_format_actual: str,
            destination: Union[str, IO[bytes], None] = None
    ) -> Union[Any, None]:
        """
        Converts the normalized dataset into BinaExperts format.
        If a destination is provided, it saves the converted data to that destination and returns None.
        Otherwise, it returns the converted dataset dictionary.

        This method reconstructs the BinaExperts dataset structure from the normalized data,
        including all relevant keys such as info, images, annotations, categories,
        and additional BinaExperts-specific metadata. It also identifies and logs
        any bounding box errors.

        :param normalized_data: The dataset in normalized format.
        :param target_format_actual: (Unused in this method, kept for signature compatibility).
        :param destination: (Optional) The destination to save the converted dataset (file path or BytesIO object).
        :return: The converted dataset dictionary if no destination is provided, otherwise None.
        """
        binaexperts_dataset = {
            INFO_KEY: {
                DESCRIPTION_KEY: normalized_data.get(INFO_KEY, {}).get(DESCRIPTION_KEY, ""),
                ORGANIZATION_KEY: normalized_data.get(INFO_KEY, {}).get(ORGANIZATION_KEY, ""),
                DATASET_KEY: normalized_data.get(INFO_KEY, {}).get(DATASET_NAME_KEY, ""),
                DATASET_TYPE_KEY: normalized_data.get(INFO_KEY, {}).get(DATASET_TYPE_KEY, ""),
                DATE_CREATED_KEY: normalized_data.get(INFO_KEY, {}).get(DATE_CREATED_KEY,
                                                                        datetime.datetime.now().strftime(DATE_FORMAT))
            },
            LICENSES_KEY: normalized_data.get(LICENSES_KEY, []),
            IMAGES_KEY: normalized_data.get(IMAGES_KEY, []),
            ANNOTATIONS_KEY: normalized_data.get(ANNOTATIONS_KEY, []),
            CATEGORIES_KEY: normalized_data.get(CATEGORIES_KEY, []),
            ERRORS_KEY: [],
            LABELS_KEY: normalized_data.get(LABELS_KEY, []),
            CLASSIFICATIONS_KEY: normalized_data.get(CLASSIFICATIONS_KEY, []),
            AUGMENTATION_SETTINGS_KEY: normalized_data.get(AUGMENTATION_SETTINGS_KEY, {}),
            TILE_SETTINGS_KEY: normalized_data.get(TILE_SETTINGS_KEY, DEFAULT_TILE_SETTINGS),
            FALSE_POSITIVE_KEY: normalized_data.get(
                FALSE_POSITIVE_KEY, DEFAULT_FALSE_POSITIVE)
        }

        for annotation in normalized_data.get(ANNOTATIONS_KEY, []):
            if len(annotation.get(BBOX_KEY, [])) == 4 and annotation[BBOX_KEY][3] > 1.0:
                error = create_error_entry(
                    annotation, normalized_data[IMAGES_KEY])
                binaexperts_dataset[ERRORS_KEY].append(error)

        if destination:
            self.save(binaexperts_dataset, destination)
            return None
        return binaexperts_dataset

    def save(
            self,
            data: dict,
            destination: Union[str, IO[bytes]] = None
    ):
        """
        Saves the BinaExperts dataset to a zip file or an in-memory BytesIO object.

        The dataset is organized into split-specific image directories (e.g., 'train_images')
        and COCO-style annotation files in a 'cocos' subdirectory.
        Additional metadata files (labels.json, classifications.json, etc.) are also included.

        :param data: The BinaExperts dataset dictionary to be saved.
        :param destination: (Optional) The destination to save the converted dataset. Can be a file path
                            or an in-memory object (BytesIO). If None, an in-memory BytesIO object is returned.
        :return: An in-memory BytesIO object if `destination` was None, otherwise None.
        """
        if destination is None:
            destination = io.BytesIO()

        with create_zip_writer(destination) as zip_file:
            zip_file.writestr(f"{COCOS_DIR}/", b'')

            created_img_dirs = set()
            for image in data.get(IMAGES_KEY, []):
                split_key = image.get(SPLIT_KEY, TRAIN_SPLIT)
                img_dir_name = VALIDATION_IMAGES_DIR if split_key in VALID_SPLIT_ALIASES else f"{split_key}_images"

                if img_dir_name not in created_img_dirs:
                    zip_file.writestr(f"{img_dir_name}/", b'')
                    created_img_dirs.add(img_dir_name)

                image_path_in_zip = os.path.join(
                    img_dir_name, image.get(FILE_NAME_KEY))
                save_image_to_zip(image, image_path_in_zip, zip_file)

            for split in [TRAIN_SPLIT, TEST_SPLIT, VALID_SPLIT]:
                split_images = [
                    img for img in data.get(IMAGES_KEY, [])
                    if img.get(SPLIT_KEY, '').lower() == split or
                    (split == VALID_SPLIT and img.get(
                        SPLIT_KEY, '').lower() in VALID_SPLIT_ALIASES)
                ]
                split_annotations = [
                    ann for ann in data.get(ANNOTATIONS_KEY, [])
                    if ann.get(IMAGE_ID_KEY) in {img.get(ID_KEY) for img in split_images}
                ]

                if not split_images and not split_annotations:
                    logger.info(
                        f"{SKIPPING_SPLIT} '{split}': No images or annotations found for BinaExperts.")
                    continue

                coco_dict = create_coco_dict(
                    data, split_images, split_annotations, split)

                json_filename_map = {
                    TRAIN_SPLIT: TRAIN_COCO_FILE,
                    TEST_SPLIT: TEST_COCO_FILE,
                    VALID_SPLIT: VALID_COCO_FILE
                }
                json_file_in_zip = os.path.join(
                    COCOS_DIR, json_filename_map[split])
                zip_file.writestr(json_file_in_zip,
                                  json.dumps(coco_dict, indent=4))

            if LABELS_KEY in data and data[LABELS_KEY]:
                zip_file.writestr("labels.json", json.dumps(
                    data[LABELS_KEY], indent=4))
            if CLASSIFICATIONS_KEY in data and data[CLASSIFICATIONS_KEY]:
                zip_file.writestr("classifications.json", json.dumps(
                    data[CLASSIFICATIONS_KEY], indent=4))
            if AUGMENTATION_SETTINGS_KEY in data and data[AUGMENTATION_SETTINGS_KEY]:
                zip_file.writestr("augmentation_settings.json", json.dumps(
                    data[AUGMENTATION_SETTINGS_KEY], indent=4))
            if TILE_SETTINGS_KEY in data and data[TILE_SETTINGS_KEY]:
                zip_file.writestr("tile_settings.json", json.dumps(
                    data[TILE_SETTINGS_KEY], indent=4))
            if ERRORS_KEY in data and data[ERRORS_KEY]:
                zip_file.writestr("errors.json", json.dumps(
                    data[ERRORS_KEY], indent=4))
            if FALSE_POSITIVE_KEY in data and data[FALSE_POSITIVE_KEY]:
                zip_file.writestr("false_positive.json", json.dumps(
                    data[FALSE_POSITIVE_KEY], indent=4))

        if isinstance(destination, io.BytesIO):
            destination.seek(0)
            return destination
