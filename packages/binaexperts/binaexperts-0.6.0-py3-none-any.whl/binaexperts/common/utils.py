import io
import os
import zipfile
import json
import yaml
import datetime
from struct import unpack
from typing import Tuple, Union, IO
from jsonschema import validate, ValidationError
from binaexperts.convertors import const
import logging

logger = logging.getLogger(__name__)


def _get_data_yaml_content(source: Union[str, IO[bytes]]) -> Union[dict, None]:
    """
    Helper function to safely extract and load data.yaml content from a source.
    Returns the loaded YAML content or None if not found/parsable.
    """
    data_yaml_content = None
    if isinstance(source, str):
        if zipfile.is_zipfile(source):
            with zipfile.ZipFile(source, 'r') as zip_ref:
                if const.YOLO_YAML_FILENAME in zip_ref.namelist():
                    with zip_ref.open(const.YOLO_YAML_FILENAME) as file:
                        data_yaml_content = yaml.safe_load(file)
        elif os.path.isdir(source):
            data_yaml_path = os.path.join(source, const.YOLO_YAML_FILENAME)
            if os.path.exists(data_yaml_path):
                with open(data_yaml_path, 'r') as file:
                    data_yaml_content = yaml.safe_load(file)
    elif isinstance(source, zipfile.ZipFile):
        if const.YOLO_YAML_FILENAME in source.namelist():
            with source.open(const.YOLO_YAML_FILENAME) as file:
                data_yaml_content = yaml.safe_load(file)
    elif hasattr(source, 'read'):  # For BytesIO
        # Create a temporary ZipFile object from BytesIO to read data.yaml
        current_pos = source.tell()  # Store current position
        source.seek(0)
        try:
            with zipfile.ZipFile(source, 'r') as temp_zip_file:
                if const.YOLO_YAML_FILENAME in temp_zip_file.namelist():
                    with temp_zip_file.open(const.YOLO_YAML_FILENAME) as file:
                        data_yaml_content = yaml.safe_load(file)
        except yaml.YAMLError as e:  # Catch YAML parsing errors
            logger.error(f"Error parsing data.yaml from source: {e}")
            data_yaml_content = None
        except zipfile.BadZipFile:
            logger.debug("Source is not a valid zip file, cannot extract data.yaml.")
            data_yaml_content = None
        finally:
            source.seek(current_pos)  # Restore original position

    return data_yaml_content


def detect_format(source: Union[str, IO[bytes]]) -> str:
    """
    Detects the format of the dataset from the given source.
    It can detect YOLO (standard and OBB), COCO, and BinaExperts formats.

    :param source: The dataset source, which can be a path to a zip file or directory,
                   or an in-memory BytesIO object.
    :return: A string representing the detected format (e.g., 'yolo', 'yolov8-obb', 'coco', 'binaexperts').
    :raises ValueError: If the source is invalid or the format cannot be determined.
    """
    file_list = []
    is_zip = False
    is_dir = False

    if isinstance(source, str):
        if zipfile.is_zipfile(source):
            is_zip = True
            with zipfile.ZipFile(source, 'r') as zip_ref:
                file_list = zip_ref.namelist()
        elif os.path.isdir(source):
            is_dir = True
            for root, _, files in os.walk(source):
                for f in files:
                    file_list.append(os.path.relpath(os.path.join(root, f), start=source))
        else:
            raise ValueError(f"Source '{source}' is not a valid zip file or directory.")
    elif isinstance(source, zipfile.ZipFile):
        is_zip = True
        file_list = source.namelist()
    elif hasattr(source, 'read'):  # Source is a generic IO object (like BytesIO)
        is_zip = True  # Assume it's a zip contained in BytesIO
        current_pos = source.tell()
        source.seek(0)
        try:
            with zipfile.ZipFile(source, 'r') as zip_ref:
                file_list = zip_ref.namelist()
        except zipfile.BadZipFile:
            logger.debug("IO source is not a valid zip file.")
            file_list = []
            is_zip = False
        finally:
            source.seek(current_pos)
    else:
        raise ValueError("Unsupported source type for format detection.")

    # 1. Check for YOLO formats (standard and OBB) via data.yaml
    data_yaml_content = _get_data_yaml_content(source)
    if data_yaml_content:
        names_data = data_yaml_content.get('names')
        if isinstance(names_data, list):
            logger.info("Detected YOLO format (names as list in data.yaml).")
            return const.CONVERTOR_FORMAT_YOLO
        elif isinstance(names_data, dict):
            logger.info("Detected YOLOv8-obb format (names as dict in data.yaml).")
            return const.CONVERTOR_FORMAT_YOLOv8_obb
        else:
            logger.warning(f"data.yaml found but 'names' key is not a list or dict. Type: {type(names_data)}")

    # 2. Check for BinaExperts format
    if any("cocos/" in filename for filename in file_list):
        logger.info("Detected BinaExperts format ('cocos/' directory found).")
        return const.CONVERTOR_FORMAT_BINAEXPERTS

    # 3. Check for COCO format
    if any("_annotations.coco.json" in filename for filename in file_list):
        logger.info("Detected COCO format ('_annotations.coco.json' found).")
        return const.CONVERTOR_FORMAT_COCO

    raise ValueError("Could not determine dataset format from source contents.")


def extract_zip(zip_path: str, extract_to: str) -> None:
    """
    Extracts the contents of a zip file to a specified directory.

    :param zip_path: The path to the zip file.
    :param extract_to: The directory where the contents will be extracted.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    """
    Infers the width and height of an image from its bytes.
    Supports JPEG images by reading SOF markers.

    :param image_bytes: The byte content of the image.
    :return: A tuple containing (width, height) of the image.
             Returns (DEFAULT_WIDTH, DEFAULT_HEIGHT) if dimensions cannot be determined.
    """
    if len(image_bytes) < 10:
        return const.DEFAULT_WIDTH, const.DEFAULT_HEIGHT

    with io.BytesIO(image_bytes) as img_file:
        img_file.seek(0)
        img_file.read(2)  # Skip the first two bytes (FF D8)
        b = img_file.read(1)
        try:
            max_iterations, iteration_count = 100, 0
            while b and b != b'\xDA':  # Loop until Start Of Scan (SOS, FF DA) marker
                iteration_count += 1
                if iteration_count > max_iterations:
                    logger.warning("Max iterations reached while parsing image dimensions.")
                    return const.DEFAULT_WIDTH, const.DEFAULT_HEIGHT

                while b != b'\xFF':  # Find the next marker start (FF)
                    b = img_file.read(1)
                while b == b'\xFF':  # Skip any extra FF bytes
                    b = img_file.read(1)
                if b >= b'\xC0' and b <= b'\xC3':  # SOF0, SOF1, SOF2, SOF3 markers (Start Of Frame)
                    img_file.read(3)  # Skip 3 bytes (precision, height high, height low)
                    h, w = unpack('>HH', img_file.read(4))  # Read height and width
                    return w, h
                else:
                    segment_length = unpack('>H', img_file.read(2))[0]  # Read segment length
                    if segment_length <= 2:  # Prevent infinite loop if segment length is too small
                        logger.warning("Invalid segment length encountered during image dimension parsing.")
                        return const.DEFAULT_WIDTH, const.DEFAULT_HEIGHT
                    img_file.read(segment_length - 2)  # Skip segment data
                b = img_file.read(1)  # Read next byte for marker check
        except Exception as e:
            logger.error(f"Error reading image dimensions: {e}")
            return const.DEFAULT_WIDTH, const.DEFAULT_HEIGHT
    return const.DEFAULT_WIDTH, const.DEFAULT_HEIGHT


def validate_data(instance: dict, schema: dict, context: str = "") -> bool:
    """
    Validates a data instance against a given JSON schema.

    :param instance: The data dictionary to validate.
    :param schema: The JSON schema to validate against.
    :param context: An optional string to provide context in error messages.
    :return: True if validation passes, False otherwise.
    """
    try:
        validate(instance=instance, schema=schema)
        return True
    except ValidationError as e:
        logging.error(f"Validation error in {context}: {e.message} at {e.path}")
        return False


def load_json_from_source(source: Union[str, zipfile.ZipFile], path: str) -> dict:
    """
    Loads a JSON file from either a directory path or a zipfile.ZipFile object.

    :param source: The source, which can be a directory path (str) or an open zipfile.ZipFile object.
    :param path: The relative path to the JSON file within the source.
    :return: The loaded JSON content as a dictionary.
    """
    if isinstance(source, zipfile.ZipFile):
        with source.open(path) as file:
            return json.load(file)
    else:
        full_path = os.path.join(source, path)
        with open(full_path, 'r') as file:
            return json.load(file)


def create_zip_writer(destination: Union[str, IO[bytes]]) -> zipfile.ZipFile:
    """
    Creates a ZipFile object for writing, handling both file path and BytesIO destinations.

    :param destination: The path to the output zip file (str) or an in-memory BytesIO object.
    :return: A zipfile.ZipFile object ready for writing.
    """
    if isinstance(destination, str) and not destination.lower().endswith('.zip'):
        destination += '.zip'
    return zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED)


def convert_bbox_yolo_to_coco(annotation: dict, img_width: int, img_height: int) -> list:
    """
    Converts YOLO bounding box format (cx, cy, w, h normalized) to COCO format (x, y, width, height pixels).

    :param annotation: A dictionary containing the YOLO bounding box under the 'bbox' key.
    :param img_width: The width of the image in pixels.
    :param img_height: The height of the image in pixels.
    :return: A list [x, y, width, height] representing the bounding box in COCO format.
    """
    cx, cy, w, h = annotation[const.BBOX_KEY]
    x = (cx - w / 2) * img_width
    y = (cy - h / 2) * img_height
    return [x, y, w * img_width, h * img_height]


def convert_bbox_to_yolo_format(bbox: list, img_width: int, img_height: int) -> list:
    """
    Converts COCO bounding box format (x, y, width, height pixels) to YOLO format (cx, cy, w, h normalized).

    :param bbox: A list [x, y, width, height] representing the bounding box in COCO format.
    :param img_width: The width of the image in pixels.
    :param img_height: The height of the image in pixels.
    :return: A list [cx, cy, w, h] representing the bounding box in YOLO format (normalized).
    """
    x, y, w, h = bbox
    cx = (x + w / 2) / img_width
    cy = (y + h / 2) / img_height
    width = w / img_width
    height = h / img_height
    return [round(val, 6) for val in (cx, cy, width, height)]


def process_segmentation_data(segmentation: list, img_width: int, img_height: int) -> list:
    """
    Normalizes segmentation polygon coordinates from pixel values to YOLO format (0.0 to 1.0).

    :param segmentation: A list of lists, where each inner list is a polygon [x1, y1, x2, y2, ...].
                         Coordinates are in pixel values.
    :param img_width: The width of the image in pixels.
    :param img_height: The height of the image in pixels.
    :return: A list of lists, where each inner list is a normalized polygon.
    """
    yolo_segmentation = []
    if isinstance(segmentation, list):
        for seg_polygon in segmentation:
            if isinstance(seg_polygon, list):
                normalized_seg = [
                    coord / img_width if i % 2 == 0 else coord / img_height
                    for i, coord in enumerate(seg_polygon)
                ]
                yolo_segmentation.append(normalized_seg)
    return yolo_segmentation


def generate_yaml_content(class_names: list, target_format: str) -> str:
    """
    Generates the content for a YOLO 'data.yaml' file, adapting to standard YOLO or YOLOv8-obb 'names' format.

    :param class_names: A list of class names (e.g., ['class0', 'class1']).
    :param target_format: The target YOLO format ('yolo' or 'yolov8-obb').
    :return: A string containing the YAML content.
    """
    yaml_data = {}

    if target_format == const.CONVERTOR_FORMAT_YOLOv8_obb:
        yaml_data["train"] = "train/images"
        yaml_data["val"] = "valid/images"
        yaml_data["test"] = "test/images"
        yaml_data["nc"] = len(class_names)
        # For YOLOv8-OBB, names are a dictionary (e.g., 0: 0, 1: 1)
        names_dict = {i: str(i) for i, _ in enumerate(class_names)} # Use string representation for keys and values as in example
        yaml_data["names"] = names_dict
    else: # Default to standard YOLO list format
        yaml_data["train"] = "../train/images"
        yaml_data["val"] = "../valid/images"
        yaml_data["test"] = "../test/images"
        yaml_data["nc"] = len(class_names)
        # For standard YOLO, names are a list.
        # Assign the list directly; yaml.dump will handle the flow style for simple lists.
        yaml_data["names"] = class_names

    # Use yaml.dump to generate the full YAML content.
    # Set default_flow_style=False for block style for the overall document.
    # Set sort_keys=False to maintain order (especially for names dict in yolov8-obb).
    return yaml.dump(yaml_data, indent=2, default_flow_style=False, sort_keys=False)

def create_label_content(annotations: list, img_width: int, img_height: int) -> str:
    """
    Creates the content for a YOLO label (.txt) file from a list of annotations.
    Handles both standard YOLO (cx cy w h) and YOLOv8-obb (x1 y1 x2 y2 x3 y3 x4 y4) formats,
    as well as segmentation masks.

    :param annotations: A list of annotation dictionaries.
    :param img_width: The width of the image in pixels.
    :param img_height: The height of the image in pixels.
    :return: A string containing the label file content, with each annotation on a new line.
    """
    label_content = ""
    if not annotations:
        logger.debug(f"create_label_content received empty annotations list for an image.")
        return ""  # Explicitly return empty string if no annotations

    for annotation in annotations:
        logger.debug(f"Processing annotation in create_label_content: {annotation}")
        class_id = annotation[const.CLASS_ID_KEY]

        # Process segmentation first
        if const.SEGMENTATION_KEY in annotation and annotation[const.SEGMENTATION_KEY]:
            # annotation[const.SEGMENTATION_KEY] is now expected to be a single flat list of normalized coordinates
            seg_points = annotation[const.SEGMENTATION_KEY]
            if isinstance(seg_points, list) and all(isinstance(coord, (float, int)) for coord in seg_points):
                seg_str = " ".join(f"{coord:.6f}" for coord in seg_points)
                line = f"{class_id} {seg_str}"
                label_content += line + "\n"
            else:
                logger.warning(f"Skipping malformed segmentation for class_id {class_id}.")

        # If no segmentation, process bounding box
        elif const.BBOX_KEY in annotation and annotation[const.BBOX_KEY]:
            bbox = annotation[const.BBOX_KEY]
            if len(bbox) == 8:  # YOLOv8 OBB format (normalized x1 y1 x2 y2 x3 y3 x4 y4)
                obb_line = f"{class_id} " + " ".join(f"{coord:.6f}" for coord in bbox)
                label_content += obb_line + "\n"

            elif len(bbox) == 4:  # Standard YOLO format (normalized cx cy w h)
                cx, cy, width, height = bbox
                line = f"{class_id} {cx:.6f} {cy:.6f} {width:.6f} {height:.6f}"
                label_content += line + "\n"
            else:
                logger.warning(
                    f"Skipping malformed bbox for class_id {class_id}. Expected 4 or 8 coordinates, got {len(bbox)}.")
        else:
            logger.warning(f"Annotation for class_id {class_id} has no valid segmentation or bbox data.")

    return label_content


def create_error_entry(annotation: dict, images: list) -> dict:
    """
    Creates an error entry dictionary for annotations that fail validation.

    :param annotation: The annotation dictionary that caused the error.
    :param images: A list of image dictionaries to find the corresponding image file name.
    :return: A dictionary representing the error entry.
    """
    image = next((img for img in images if img[const.ID_KEY] == annotation[const.IMAGE_ID_KEY]), None)
    return {
        "annotation_type": "box",
        "annotation": {
            "x": annotation[const.BBOX_KEY][0],
            "y": annotation[const.BBOX_KEY][1],
            "width": annotation[const.BBOX_KEY][2],
            "height": annotation[const.BBOX_KEY][3]
        },
        const.IMAGE_ID_KEY: annotation[const.IMAGE_ID_KEY],
        const.FILE_NAME_KEY: image[const.FILE_NAME_KEY] if image else "",
        "error_message": f"Expected bbox height to be <= 1.0, got {annotation[const.BBOX_KEY][3]}"
    }


def save_images_to_zip(images: list, zip_file: zipfile.ZipFile) -> None:
    """
    Saves image content to a zip file, organizing them by split directories.

    :param images: A list of image dictionaries, each containing 'file_name', 'split', and 'image_content'.
    :param zip_file: An open zipfile.ZipFile object to write to.
    """
    created_dirs = set()
    for image in images:
        split_dir = const.VALIDATION_IMAGES_DIR if image[
                                                       const.SPLIT_KEY] in const.VALID_SPLIT_ALIASES else f"{image[const.SPLIT_KEY]}_images"

        if split_dir not in created_dirs:
            zip_file.writestr(f"{split_dir}/", b'')
            created_dirs.add(split_dir)

        image_path = os.path.join(split_dir, image[const.FILE_NAME_KEY])
        if image.get(const.IMAGE_CONTENT_KEY):
            zip_file.writestr(image_path, image.get(const.IMAGE_CONTENT_KEY))
        else:
            logging.warning(
                f"{const.SKIPPING_IMAGE} {image.get(const.FILE_NAME_KEY, 'Unknown')} due to missing content for path {image_path}.")


def create_coco_dict(data: dict, split_images: list, split_annotations: list, split: str) -> dict:
    """
    Creates a COCO-style dictionary for a specific data split.

    :param data: The full dataset dictionary (normalized or COCO-like).
    :param split_images: A list of image dictionaries belonging to the current split.
    :param split_annotations: A list of annotation dictionaries belonging to the current split.
    :param split: The name of the current split (e.g., 'train', 'valid', 'test').
    :return: A dictionary structured as a COCO annotation file for the given split.
    """
    original_images_map = {img[const.ID_KEY]: img for img in data.get(const.IMAGES_KEY, [])}

    return {
        const.INFO_KEY: {
            const.DESCRIPTION_KEY: data.get(const.INFO_KEY, {}).get(const.DESCRIPTION_KEY, const.DEFAULT_DESCRIPTION),
            const.DATASET_NAME_KEY: data.get(const.INFO_KEY, {}).get(const.DATASET_NAME_KEY,
                                                                     const.DEFAULT_DATASET_NAME),
            const.DATASET_TYPE_KEY: data.get(const.INFO_KEY, {}).get(const.DATASET_TYPE_KEY,
                                                                     const.DEFAULT_DATASET_TYPE),
            const.DATE_CREATED_KEY: data.get(const.INFO_KEY, {}).get(
                const.DATE_CREATED_KEY, datetime.datetime.now().strftime(const.DEFAULT_DATE_FORMAT)
            ),
        },
        const.LICENSES_KEY: data.get(const.LICENSES_KEY, []),
        const.IMAGES_KEY: [
            {
                const.ID_KEY: img.get(const.ID_KEY),
                const.FILE_NAME_KEY: img.get(const.FILE_NAME_KEY),
                const.WIDTH_KEY: img.get(const.WIDTH_KEY, 0),
                const.HEIGHT_KEY: img.get(const.HEIGHT_KEY, 0),
            }
            for img in split_images
        ],
        const.ANNOTATIONS_KEY: [
            {
                const.ID_KEY: ann.get(const.ID_KEY),
                const.IMAGE_ID_KEY: ann.get(const.IMAGE_ID_KEY),
                const.CATEGORY_ID_KEY: ann.get(const.CATEGORY_ID_KEY),
                const.BBOX_KEY: ann.get(const.BBOX_KEY, []),
                const.SEGMENTATION_KEY: ann.get(const.SEGMENTATION_KEY, []),
                const.AREA_KEY: ann.get(const.AREA_KEY, 0.0),
                const.ISCROWD_KEY: ann.get(const.ISCROWD_KEY, 0)
            }
            for ann in split_annotations
        ],
        const.CATEGORIES_KEY: data.get(const.CATEGORIES_KEY, [])
    }


def save_image_to_zip(image: dict, image_path: str, zip_file: zipfile.ZipFile) -> None:
    """
    Saves a single image's content to a specified path within a zip file.

    :param image: The image dictionary containing 'file_name' and 'image_content'.
    :param image_path: The full path including filename within the zip archive.
    :param zip_file: An open zipfile.ZipFile object to write to.
    """
    if image.get(const.IMAGE_CONTENT_KEY):
        zip_file.writestr(image_path, image.get(const.IMAGE_CONTENT_KEY))
    else:
        logging.warning(
            f"{const.SKIPPING_IMAGE} {image.get(const.FILE_NAME_KEY, 'Unknown')} due to missing content for path {image_path}.")


def convert_yolo_obb_to_coco(yolo_obb_coords: list, img_width: int, img_height: int) -> list:
    """
    Converts YOLOv8 OBB (Oriented Bounding Box) coordinates (normalized x1, y1, ..., x4, y4)
    to COCO's axis-aligned bounding box format (x, y, width, height pixels).

    This function calculates the minimum bounding rectangle of the OBB and returns its COCO representation.

    :param yolo_obb_coords: A list of 8 normalized coordinates [x1, y1, x2, y2, x3, y3, x4, y4].
    :param img_width: The width of the image in pixels.
    :param img_height: The height of the image in pixels.
    :return: A list [x, y, width, height] representing the axis-aligned bounding box in COCO format.
    """
    x1, y1, x2, y2, x3, y3, x4, y4 = yolo_obb_coords

    # Denormalize points to pixel coordinates
    x1_px, y1_px = x1 * img_width, y1 * img_height
    x2_px, y2_px = x2 * img_width, y2 * img_height
    x3_px, y3_px = x3 * img_width, y3 * img_height
    x4_px, y4_px = x4 * img_width, y4 * img_height

    # Find min/max x and y to get the axis-aligned bounding box
    min_x_px = min(x1_px, x2_px, x3_px, x4_px)
    min_y_px = min(y1_px, y2_px, y3_px, y4_px)
    max_x_px = max(x1_px, x2_px, x3_px, x4_px)
    max_y_px = max(y1_px, y2_px, y3_px, y4_px)

    x_coco = min_x_px
    y_coco = min_y_px
    w_coco = max_x_px - min_x_px
    h_coco = max_y_px - min_y_px

    return [x_coco, y_coco, w_coco, h_coco]


def convert_coco_to_yolo_obb(coco_bbox: list, img_width: int, img_height: int) -> list:
    """
    Convert COCO bbox (x, y, width, height) to YOLOv8 OBB (normalized x1, y1, x2, y2, x3, y3, x4, y4).
    The output order of points will match the user's 'original labels' convention:
    (Top-Right, Top-Left, Bottom-Left, Bottom-Right) clockwise.

    :param coco_bbox: List with COCO bbox data as [x, y, width, height] (pixel values).
    :param img_width: Image width in pixels.
    :param img_height: Image height in pixels.
    :return: YOLO-formatted OBB as [x1, y1, x2, y2, x3, y3, x4, y4] (normalized).
    """
    x, y, w, h = coco_bbox

    # Calculate the pixel coordinates for the 4 corners
    top_left_px = (x, y)
    top_right_px = (x + w, y)
    bottom_right_px = (x + w, y + h)
    bottom_left_px = (x, y + h)

    # Normalize pixel coordinates
    def normalize_point(px_x, px_y):
        return px_x / img_width, px_y / img_height

    tl_norm = normalize_point(top_left_px[0], top_left_px[1])
    tr_norm = normalize_point(top_right_px[0], top_right_px[1])
    br_norm = normalize_point(bottom_right_px[0], bottom_right_px[1])
    bl_norm = normalize_point(bottom_left_px[0], bottom_left_px[1])

    # Arrange points in the order observed in the user's "Original Label":
    # (Top-Right, Top-Left, Bottom-Left, Bottom-Right)
    ordered_points_norm = [
        tr_norm[0], tr_norm[1],  # x1, y1 (Top-Right)
        tl_norm[0], tl_norm[1],  # x2, y2 (Top-Left)
        bl_norm[0], bl_norm[1],  # x3, y3 (Bottom-Left)
        br_norm[0], br_norm[1]  # x4, y4 (Bottom-Right)
    ]

    return [round(val, 6) for val in ordered_points_norm]
