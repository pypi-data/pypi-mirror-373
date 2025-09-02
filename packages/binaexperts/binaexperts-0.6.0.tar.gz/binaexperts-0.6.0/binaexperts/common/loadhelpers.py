import zipfile
import io
import yaml
import os
import base64

from binaexperts.common.utils import logger
from binaexperts.convertors.const import *


def loadhelper_coco_data(
        coco_data,
        dataset,
        subdir,
        source_zip=None
):

    # Load categories if not already present
    if not dataset[CATEGORIES_KEY]:
        for cat in coco_data.get(CATEGORIES_KEY, []):
            category = {
                ID_KEY: cat[ID_KEY],
                NAME_KEY: cat[NAME_KEY],
                SUPERCATEGORY_KEY: cat.get(
                    SUPERCATEGORY_KEY, DEFAULT_SUPERCATEGORY)
            }
            dataset[CATEGORIES_KEY].append(category)

    # Load images
    for img in coco_data.get(IMAGES_KEY, []):
        unique_image_id = f"{subdir}_{img[ID_KEY]}"  # Prefix with split
        image_file_name = img[FILE_NAME_KEY]
        image_path = f"{subdir}/{image_file_name}"

        image_content = None
        if source_zip and image_path in source_zip.namelist():
            with source_zip.open(image_path) as img_file:
                image_content = img_file.read()
        elif source_zip:
            continue

        image = {
            ID_KEY: unique_image_id,
            FILE_NAME_KEY: image_file_name,
            WIDTH_KEY: img.get(WIDTH_KEY, 0),
            HEIGHT_KEY: img.get(HEIGHT_KEY, 0),
            SPLIT_KEY: subdir,
            SOURCE_ZIP_KEY: source_zip,
            IMAGE_CONTENT_KEY: image_content
        }
        dataset[IMAGES_KEY].append(image)

    # Load annotations
    for ann in coco_data.get(ANNOTATIONS_KEY, []):
        unique_image_id = f"{subdir}_{ann[IMAGE_ID_KEY]}"
        annotation = {
            ID_KEY: ann[ID_KEY],
            IMAGE_ID_KEY: unique_image_id,
            CATEGORY_ID_KEY: ann[CATEGORY_ID_KEY],
            BBOX_KEY: ann[BBOX_KEY],
            SEGMENTATION_KEY: ann.get(SEGMENTATION_KEY, []),
            AREA_KEY: ann.get(AREA_KEY, 0.0),
            ISCROWD_KEY: ann.get(ISCROWD_KEY, 0)
        }
        if not isinstance(annotation[SEGMENTATION_KEY], list):
            continue
        dataset[ANNOTATIONS_KEY].append(annotation)


def loadhelper_yolo_from_zip(
        zip_file: zipfile.ZipFile,
        dataset: dict,
        subdirs: list
):
    # ... (data.yaml loading remains the same)

    for subdir in subdirs:
        image_dir = YOLO_IMAGE_DIR_PATH_TEMPLATE.format(subdir)
        label_dir = YOLO_LABEL_DIR_PATH_TEMPLATE.format(subdir)

        has_images_in_subdir = any(
            path.startswith(image_dir) and (path.endswith('.jpg') or path.endswith('.png')) for path in
            zip_file.namelist())
        if not has_images_in_subdir:
            continue
        for img_path in zip_file.namelist():

            if img_path.startswith(image_dir) and (img_path.endswith('.jpg') or img_path.endswith('.png')):
                image_file_name = os.path.basename(img_path)
                image_path = f"{subdir}/{YOLO_IMAGES_SUBDIR}/{image_file_name}"
                label_file_name = image_file_name.replace(
                    '.jpg', TXT_EXT).replace('.png', TXT_EXT)
                label_path = f"{subdir}/{YOLO_LABELS_SUBDIR}/{label_file_name}"
                if image_path in zip_file.namelist():
                    with zip_file.open(image_path) as img_file:
                        image_content = img_file.read()

                    yolo_image = {
                        FILE_NAME_KEY: image_file_name,
                        ANNOTATIONS_KEY: [],
                        SPLIT_KEY: subdir,
                        SOURCE_ZIP_KEY: zip_file,
                        IMAGE_CONTENT_KEY: image_content
                    }

                    if label_path in zip_file.namelist():
                        with zip_file.open(label_path) as label_file:
                            for line in io.TextIOWrapper(label_file, encoding='utf-8'):
                                line = line.strip()
                                if not line:
                                    continue
                                values = list(map(float, line.split()))

                                if len(values) == 5:  # Standard YOLO bbox: class_id cx cy w h
                                    class_id = int(values[0])
                                    cx, cy, w, h = values[1:]
                                    yolo_annotation = {
                                        CLASS_ID_KEY: class_id,
                                        # <--- STORE AS LIST UNDER BBOX_KEY
                                        BBOX_KEY: [cx, cy, w, h]
                                    }
                                    yolo_image[ANNOTATIONS_KEY].append(
                                        yolo_annotation)
                                elif len(values) > 5 and len(values) % 2 != 0:  # Segmentation
                                    class_id = int(values[0])
                                    # Flat list of segmentation points
                                    segmentation_coords = values[1:]
                                    yolo_annotation = {
                                        CLASS_ID_KEY: class_id,
                                        # <--- STORE AS LIST OF LISTS
                                        SEGMENTATION_KEY: [segmentation_coords]
                                    }
                                    yolo_image[ANNOTATIONS_KEY].append(
                                        yolo_annotation)
                                else:
                                    print(
                                        f"Warning: Skipping malformed or unsupported line in label file {label_path}: {line}")
                    dataset[IMAGES_KEY].append(yolo_image)


def loadhelper_yolo_from_directory(
        source: str,
        dataset: dict,
        subdirs: list
):
    # ... (data.yaml loading remains the same)

    for subdir in subdirs:
        image_dir = os.path.join(source, subdir, YOLO_IMAGES_SUBDIR)
        label_dir = os.path.join(source, subdir, YOLO_LABELS_SUBDIR)

        if not os.path.isdir(image_dir) or not os.path.isdir(label_dir):
            continue

        for image_file_name in os.listdir(image_dir):
            if image_file_name.endswith('.jpg') or image_file_name.endswith('.png'):
                image_path = os.path.join(image_dir, image_file_name)
                label_file_name = image_file_name.replace(
                    '.jpg', TXT_EXT).replace('.png', TXT_EXT)
                label_path = os.path.join(label_dir, label_file_name)

                with open(image_path, 'rb') as img_file:
                    image_content = img_file.read()

                yolo_image = {
                    FILE_NAME_KEY: image_file_name,
                    ANNOTATIONS_KEY: [],
                    SPLIT_KEY: subdir,
                    IMAGE_CONTENT_KEY: image_content
                }

                if os.path.isfile(label_path):
                    with open(label_path, 'r') as label_file:
                        for line in label_file:
                            line = line.strip()
                            if not line:
                                continue
                            values = list(map(float, line.split()))

                            if len(values) == 5:
                                class_id = int(values[0])
                                cx, cy, w, h = values[1:]
                                yolo_annotation = {
                                    CLASS_ID_KEY: int(class_id),
                                    # <--- STORE AS LIST UNDER BBOX_KEY
                                    BBOX_KEY: [cx, cy, w, h]
                                }
                                yolo_image[ANNOTATIONS_KEY].append(
                                    yolo_annotation)
                            elif len(values) > 5:
                                class_id = int(values[0])
                                segmentation_coords = values[1:]
                                yolo_annotation = {
                                    CLASS_ID_KEY: class_id,
                                    # <--- STORE AS LIST OF LISTS
                                    SEGMENTATION_KEY: [segmentation_coords]
                                }
                                yolo_image[ANNOTATIONS_KEY].append(
                                    yolo_annotation)

                dataset[IMAGES_KEY].append(yolo_image)


def loadhelper_binaexperts_data(
    bina_data,
    dataset,
    image_folder,
    source_zip=None
):

    if not dataset[CATEGORIES_KEY]:
        for cat in bina_data.get(CATEGORIES_KEY, []):
            category = {
                ID_KEY: cat[ID_KEY],
                NAME_KEY: cat[NAME_KEY],
                SUPERCATEGORY_KEY: cat.get(
                    SUPERCATEGORY_KEY, DEFAULT_SUPERCATEGORY)
            }
            dataset[CATEGORIES_KEY].append(category)

    for img in bina_data.get(IMAGES_KEY, []):
        image_id = img[ID_KEY]
        image_file_name = img[FILE_NAME_KEY]
        image_path = f"{image_folder}/{image_file_name}"

        image_content = None
        if source_zip and image_path in source_zip.namelist():
            with source_zip.open(image_path) as img_file:
                image_content = img_file.read()

        image = {
            ID_KEY: image_id,
            FILE_NAME_KEY: image_file_name,
            WIDTH_KEY: img.get(WIDTH_KEY, 0),
            HEIGHT_KEY: img.get(HEIGHT_KEY, 0),
            SPLIT_KEY: image_folder.replace('_images', ''),
            SOURCE_ZIP_KEY: source_zip,
            IMAGE_CONTENT_KEY: image_content
        }
        dataset[IMAGES_KEY].append(image)

    image_ids = set(img[ID_KEY] for img in dataset[IMAGES_KEY])
    for ann in bina_data.get(ANNOTATIONS_KEY, []):
        image_id = ann[IMAGE_ID_KEY]
        if image_id not in image_ids:
            continue
        annotation = {
            ID_KEY: ann[ID_KEY],
            IMAGE_ID_KEY: image_id,
            CATEGORY_ID_KEY: ann[CATEGORY_ID_KEY],
            BBOX_KEY: ann[BBOX_KEY],
            SEGMENTATION_KEY: ann.get(SEGMENTATION_KEY, []),
            AREA_KEY: ann.get(AREA_KEY, 0.0),
            ISCROWD_KEY: ann.get(ISCROWD_KEY, 0),
            BBOX_FORMAT_KEY: COCO_BBOX_FORMAT
        }
        dataset[ANNOTATIONS_KEY].append(annotation)

    dataset[LABELS_KEY] = bina_data.get(LABELS_KEY, [])
    dataset[CLASSIFICATIONS_KEY] = bina_data.get(CLASSIFICATIONS_KEY, [])
    dataset[AUGMENTATION_SETTINGS_KEY] = bina_data.get(
        AUGMENTATION_SETTINGS_KEY, {})
    dataset[TILE_SETTINGS_KEY] = bina_data.get(
        TILE_SETTINGS_KEY, DEFAULT_TILE_SETTINGS)
    dataset[FALSE_POSITIVE_KEY] = bina_data.get(
        FALSE_POSITIVE_KEY, DEFAULT_FALSE_POSITIVE)

    if ERRORS_KEY not in dataset:
        dataset[ERRORS_KEY] = []
    dataset[ERRORS_KEY].extend(bina_data.get(ERRORS_KEY, []))


def encode_file_to_base64(file_path):
    """Encode a file to Base64 format."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "rb") as file:
        return "data:@file/zip;base64," + base64.b64encode(file.read()).decode("utf-8")


def loadhelper_yolov8obb_from_zip(
    zip_file: zipfile.ZipFile,
    dataset: dict,
    subdirs: list
):
    data_yaml = {}
    if YOLO_YAML_FILENAME in zip_file.namelist():
        try:
            with zip_file.open(YOLO_YAML_FILENAME) as file:
                data_yaml = yaml.safe_load(file)
                if not isinstance(data_yaml, dict):  # Ensure loaded YAML is a dict

                    data_yaml = {}  # Reset to empty dict if malformed
        except yaml.YAMLError as e:

            data_yaml = {}  # Ensure it's empty if parsing fails
    else:
        logger.warning(
            f"{YOLO_YAML_FILENAME} not found in zip file. Class names might be missing.")

    names_data_raw = data_yaml.get('names')  # Get raw value of 'names' key

    if isinstance(names_data_raw, dict):
        dataset[DATASET_CLASS_NAMES_KEY] = [
            str(key) for key in names_data_raw.keys()]
    elif isinstance(names_data_raw, list):
        dataset[DATASET_CLASS_NAMES_KEY] = [
            str(name) for name in names_data_raw]
    else:
        dataset[DATASET_CLASS_NAMES_KEY] = []  # Default to empty list on error

    dataset[LICENSES_KEY] = [{ID_KEY: 1, NAME_KEY: data_yaml.get('license', 'Unknown License'),
                              "url": data_yaml.get('license_url', '')}]
    # ... (data.yaml loading and class names parsing remain the same)

    for subdir in subdirs:
        image_dir = YOLO_IMAGE_DIR_PATH_TEMPLATE.format(subdir)
        label_dir = YOLO_LABEL_DIR_PATH_TEMPLATE.format(subdir)

        has_images_in_subdir = any(
            path.startswith(image_dir) and (path.endswith('.jpg') or path.endswith('.png')) for path in
            zip_file.namelist())
        if not has_images_in_subdir:
            continue

        for img_path in zip_file.namelist():
            if img_path.startswith(image_dir) and (img_path.endswith('.jpg') or img_path.endswith('.png')):
                image_file_name = os.path.basename(img_path)
                image_path_in_zip = f"{image_dir}/{image_file_name}"
                label_file_name = image_file_name.replace(
                    '.jpg', TXT_EXT).replace('.png', TXT_EXT)
                label_path_in_zip = f"{label_dir}/{label_file_name}"

                image_content = None
                if image_path_in_zip in zip_file.namelist():
                    with zip_file.open(image_path_in_zip) as img_file:
                        image_content = img_file.read()

                yolo_image = {
                    FILE_NAME_KEY: image_file_name,
                    ANNOTATIONS_KEY: [],  # Initialize empty list for this image's annotations
                    SPLIT_KEY: subdir,
                    SOURCE_ZIP_KEY: zip_file,
                    IMAGE_CONTENT_KEY: image_content
                }

                if label_path_in_zip in zip_file.namelist():
                    with zip_file.open(label_path_in_zip) as label_file:
                        for line in io.TextIOWrapper(label_file, encoding='utf-8'):
                            line = line.strip()
                            if not line:  # Skip empty lines
                                continue

                            values = list(map(float, line.split()))

                            if len(values) == 9:  # OBB format: class_id x1 y1 x2 y2 x3 y3 x4 y4
                                class_index = int(values[0])
                                # Get the 8 OBB coordinates
                                obb_coords = values[1:]
                                yolo_annotation = {
                                    CLASS_ID_KEY: class_index,
                                    BBOX_KEY: obb_coords  # Store the list of 8 floats
                                }
                                yolo_image[ANNOTATIONS_KEY].append(
                                    yolo_annotation)
                            elif len(values) == 5:  # Standard YOLO bbox: class_id cx cy w h
                                class_id = int(values[0])
                                cx, cy, w, h = values[1:]
                                yolo_annotation = {
                                    CLASS_ID_KEY: class_id,
                                    # Store as list for consistency
                                    BBOX_KEY: [cx, cy, w, h]
                                }
                                yolo_image[ANNOTATIONS_KEY].append(
                                    yolo_annotation)
                            # Segmentation: class_id x1 y1 x2 y2 ...
                            elif len(values) > 5 and len(values) % 2 != 0:
                                class_id = int(values[0])
                                segmentation = values[1:]
                                yolo_annotation = {
                                    CLASS_ID_KEY: class_id,
                                    # Store as list of list
                                    SEGMENTATION_KEY: [segmentation]
                                }
                                yolo_image[ANNOTATIONS_KEY].append(
                                    yolo_annotation)
                            else:
                                print(
                                    f"Warning: Skipping malformed or unsupported line in label file {label_path_in_zip}: {line}")

                dataset[IMAGES_KEY].append(yolo_image)


def loadhelper_yolov8obb_from_directory(
        source: str,
        dataset: dict,
        subdirs: list
):
    # ... (data.yaml loading remains the same)
    data_yaml_path = os.path.join(source, YOLO_YAML_FILENAME)
    data_yaml = {}
    if os.path.exists(data_yaml_path):
        with open(data_yaml_path, 'r') as file:
            data_yaml = yaml.safe_load(file)

    names_data = data_yaml.get('names', [])
    if isinstance(names_data, dict):
        dataset[DATASET_CLASS_NAMES_KEY] = [
            str(key) for key in names_data.keys()]
    elif isinstance(names_data, list):
        dataset[DATASET_CLASS_NAMES_KEY] = [str(name) for name in names_data]
    else:
        print("Error: 'names' is not in the expected format.")
        dataset[DATASET_CLASS_NAMES_KEY] = []

    dataset[LICENSES_KEY] = [{ID_KEY: 1, NAME_KEY: data_yaml.get('license', 'Unknown License'),
                              "url": data_yaml.get('license_url', '')}]

    for subdir in subdirs:
        image_dir = os.path.join(source, subdir, YOLO_IMAGES_SUBDIR)
        label_dir = os.path.join(source, subdir, YOLO_LABELS_SUBDIR)
        if not os.path.isdir(image_dir) or not os.path.isdir(label_dir):
            continue

        for image_file_name in os.listdir(image_dir):
            if image_file_name.endswith('.jpg') or image_file_name.endswith('.png'):
                image_path = os.path.join(image_dir, image_file_name)
                label_file_name = image_file_name.replace(
                    '.jpg', TXT_EXT).replace('.png', TXT_EXT)
                label_path = os.path.join(label_dir, label_file_name)

                image_content = None
                with open(image_path, 'rb') as img_file:
                    image_content = img_file.read()

                yolo_image = {
                    FILE_NAME_KEY: image_file_name,
                    ANNOTATIONS_KEY: [],
                    SPLIT_KEY: subdir,
                    IMAGE_CONTENT_KEY: image_content
                }

                if os.path.isfile(label_path):
                    with open(label_path, 'r') as label_file:
                        for line in label_file:
                            line = line.strip()
                            if not line:  # Skip empty lines
                                continue

                            values = list(map(float, line.split()))

                            if len(values) == 9:  # OBB format
                                class_index = int(values[0])
                                obb_coords = values[1:]
                                yolo_annotation = {
                                    CLASS_ID_KEY: int(class_index),
                                    BBOX_KEY: obb_coords
                                }
                                yolo_image[ANNOTATIONS_KEY].append(
                                    yolo_annotation)
                            elif len(values) == 5:  # Standard YOLO bbox
                                class_id = int(values[0])
                                cx, cy, w, h = values[1:]
                                yolo_annotation = {
                                    CLASS_ID_KEY: class_id,
                                    # Store as list for consistency
                                    BBOX_KEY: [cx, cy, w, h]
                                }
                                yolo_image[ANNOTATIONS_KEY].append(
                                    yolo_annotation)
                            elif len(values) > 5 and len(values) % 2 != 0:  # Segmentation
                                class_id = int(values[0])
                                segmentation = values[1:]
                                yolo_annotation = {
                                    CLASS_ID_KEY: class_id,
                                    SEGMENTATION_KEY: [segmentation]
                                }
                                yolo_image[ANNOTATIONS_KEY].append(
                                    yolo_annotation)
                            else:
                                print(
                                    f"Warning: Skipping malformed or unsupported line in label file {label_path}: {line}")

                dataset[IMAGES_KEY].append(yolo_image)
