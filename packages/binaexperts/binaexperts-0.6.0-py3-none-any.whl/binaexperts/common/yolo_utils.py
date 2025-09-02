import os
import sys
import importlib
import torch
import cv2
import numpy as np
from binaexperts.common.logger import get_logger

# Initialize the logger using the current module name.
logger = get_logger(__name__)

# Define absolute paths for the YOLO model assets (YOLOv5 and YOLOv7).
YOLO_MODELS = {
    "yolov5": os.path.abspath(os.path.join(os.path.dirname(__file__), "../SDKs/YOLO/yolov5")),
    "yolov7": os.path.abspath(os.path.join(os.path.dirname(__file__), "../SDKs/YOLO/yolov7")),
}


def set_yolo_path(model_type):
    """
    Dynamically adjust the system path to include only the directory of the specified YOLO model.

    This avoids conflicts between different YOLO versions by removing paths of other models
    and inserting the path for the chosen model at the beginning of sys.path.

    Parameters:
        model_type (str): The YOLO model type to use ('yolov5' or 'yolov7').
    """
    # Remove the paths of models that are not the selected one.
    for yolo_type, path in YOLO_MODELS.items():
        if yolo_type != model_type and path in sys.path:
            sys.path.remove(path)
    # Add the selected model's path to the system path if not already present.
    if YOLO_MODELS[model_type] not in sys.path:
        sys.path.insert(0, YOLO_MODELS[model_type])


def dynamic_import(module_path, class_name):
    """
    Dynamically import a module and retrieve a specific class or function from it.

    This allows for flexible imports where the module path or function may change.

    Parameters:
        module_path (str): The dot-separated path of the module.
        class_name (str): The name of the class or function to import.

    Returns:
        The imported class or function.
    """
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def fallback_letterbox(im, new_shape=(640, 640), stride=32, color=(114, 114, 114),
                       auto=True, scaleFill=False, scaleup=True):
    """
    Resize and pad an image using a letterbox technique to maintain aspect ratio.

    The function resizes the image to a new shape while preserving its aspect ratio,
    adding padding to reach the target dimensions. It returns the processed image,
    the scaling ratio, and the padding values.

    Parameters:
        im (np.array): The input image.
        new_shape (tuple or int): The desired output dimensions. If an integer is given,
                                  the image will be resized to (new_shape, new_shape).
        stride (int): The stride used during resizing (typically related to the model).
        color (tuple): The color for padding (in BGR format).
        auto (bool): Whether to automatically adjust padding.
        scaleFill (bool): Whether to scale the image to exactly fill the new shape.
        scaleup (bool): Whether to allow the image to be scaled up.

    Returns:
        tuple: (resized and padded image, scaling ratio, (dw, dh) padding values)
    """
    # Get current image height and width.
    shape = im.shape[:2]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    # Determine the scaling ratio for resizing.
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:
        r = min(r, 1.0)
    # Compute the new dimensions after scaling.
    new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))
    # Calculate the padding needed to reach the desired shape.
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
    dw, dh = dw / 2, dh / 2

    # Resize the image if the new size is different.
    if shape[::-1] != new_unpad:
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)

    # Determine padding values (top, bottom, left, right).
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    # Apply border to the image with the specified padding and color.
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

    return im, r, (dw, dh)


def preprocess_image(image: np.ndarray, letterbox_func, device, infer_dims=(640, 640)):
    """
    Preprocess a single image for inference.

    This function takes an image (as a NumPy array), applies a letterbox resizing
    to maintain aspect ratio, converts the image from BGR to RGB format, rearranges the
    dimensions, normalizes pixel values, and converts it into a PyTorch tensor.

    Parameters:
        image (np.ndarray): The input image (OpenCV BGR format).
        letterbox_func (function): The letterbox function used for resizing and padding.
        device (torch.device): The device to which the tensor is moved (CPU or GPU).
        infer_dims (tuple): Target dimensions for the model inference (height, width).

    Returns:
        torch.Tensor: The preprocessed image tensor.

    Raises:
        ValueError: If the letterbox function is not provided or image is invalid.
    """
    if letterbox_func is None:
        raise ValueError("❌ Letterbox function is None. Model might not have been properly loaded.")
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("❌ Invalid image input. Expected a NumPy array.")

    try:
        # Apply letterbox resizing to the image.
        # Ensure infer_dims is (width, height) for letterbox function if it expects that
        image_resized = letterbox_func(image, new_shape=infer_dims, stride=32, auto=False)[0]

        # Convert from BGR to RGB using cv2.cvtColor (often more optimized)
        image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)

        # Rearrange dimensions to (channels, height, width).
        image_transposed = image_rgb.transpose(2, 0, 1)
        image_contiguous = np.ascontiguousarray(image_transposed)

        # Convert the image to a PyTorch tensor and normalize pixel values.
        image_tensor = torch.from_numpy(image_contiguous).float() / 255.0

        if device.type == 'cuda':
            # Use pinned memory for faster CPU-to-GPU transfers
            image_tensor = image_tensor.pin_memory()
            logger.debug("Image tensor pinned to memory.")
        # Move tensor to the target device asynchronously
        image_tensor = image_tensor.unsqueeze(0).to(device, non_blocking=True)

        return image_tensor
    except Exception as e:
        logger.error(f"❌ Error preprocessing image: {str(e)}")
        raise


def fallback_letterbox_yolov5(image, new_shape=(640, 640), stride=32, color=(114, 114, 114),
                              auto=True, scaleFill=False, scaleup=True):
    """
    A wrapper for the fallback_letterbox function specifically for YOLOv5.

    Parameters are identical to fallback_letterbox.

    Returns:
        tuple: The processed image, scaling ratio, and padding values.
    """
    return fallback_letterbox(image, new_shape, stride, color, auto, scaleFill, scaleup)


def fallback_letterbox_yolov7(image, new_shape=(640, 640), stride=32, color=(114, 114, 114),
                              auto=True, scaleFill=False, scaleup=True):
    """
    A wrapper for the fallback_letterbox function specifically for YOLOv7.

    Parameters are identical to fallback_letterbox.

    Returns:
        tuple: The processed image, scaling ratio, and padding values.
    """
    return fallback_letterbox(image, new_shape, stride, color, auto, scaleFill, scaleup)


def load_model_yolov5(model_path, device):
    """
    Dynamically load the YOLOv5 model and its utility functions.

    This function sets the appropriate system path for YOLOv5, imports the model loading
    function, loads the model from the provided path, moves it to the specified device, and
    sets it to evaluation mode. It also dynamically imports the non-max suppression and
    coordinate scaling utilities.

    Parameters:
        model_path (str): The file path to the YOLOv5 model.
        device (torch.device): The device to load the model onto.

    Returns:
        tuple: (model, non_max_suppression function, scale_coords function, letterbox function, model_img_size)

    Raises:
        FileNotFoundError: If the model file does not exist.
        ImportError: If the required utility functions cannot be imported.
    """
    set_yolo_path("yolov5")

    # Import the YOLOv5 model loading function from the experimental module.
    try:
        from binaexperts.SDKs.YOLO.yolov5.models.experimental import attempt_load as attempt_load_v5
    except ImportError as e:
        logger.error(f"❌ Error importing YOLOv5 attempt_load: {str(e)}")
        raise

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Model file not found: {model_path}")

    logger.info(f"🟢 Loading YOLOv5 model from {model_path}")

    try:
        # Load the model (YOLOv5 does not require map_location for loading).
        model = attempt_load_v5(model_path)
        model.to(device)
        model.eval()
    except Exception as e:
        logger.error(f"❌ Error loading YOLOv5 model {model_path}: {str(e)}")
        raise

    # Dynamically import the non-max suppression and coordinate scaling functions.
    non_max_suppression = None
    scale_coords = None
    letterbox_func = None
    try:
        non_max_suppression = dynamic_import("binaexperts.SDKs.YOLO.yolov5.utils.general", "non_max_suppression")
        scale_coords = dynamic_import("binaexperts.SDKs.YOLO.yolov5.utils.general", "scale_coords")
        # Attempt to get the native letterbox function from YOLOv5 utils
        letterbox_func = dynamic_import("binaexperts.SDKs.YOLO.yolov5.utils.augmentations", "letterbox")
    except ImportError as e:
        logger.warning(f"⚠ Could not import native YOLOv5 utilities, using fallbacks: {str(e)}")
        non_max_suppression = dynamic_import("binaexperts.SDKs.YOLO.yolov5.utils.general",
                                             "non_max_suppression")
        scale_coords = dynamic_import("binaexperts.SDKs.YOLO.yolov5.utils.general", "scale_coords")
        letterbox_func = fallback_letterbox_yolov5

    # Get model's expected image size, default to (640, 640) if not found
    model_img_size = getattr(model, 'imgsz', (640, 640))
    if isinstance(model_img_size, (int, float)):
        model_img_size = (int(model_img_size), int(model_img_size))
    elif isinstance(model_img_size, list) and len(model_img_size) == 2:
        model_img_size = tuple(model_img_size)
    else:
        model_img_size = (640, 640)

    return model, non_max_suppression, scale_coords, letterbox_func, model_img_size


def load_model_yolov7(model_path, device):
    """
    Dynamically load the YOLOv7 model and its utility functions.

    This function sets the appropriate system path for YOLOv7, imports the model loading
    function, loads the model from the provided path, moves it to the specified device, and
    sets it to evaluation mode. It also dynamically imports the non-max suppression and
    coordinate scaling utilities.

    Parameters:
        model_path (str): The file path to the YOLOv7 model.
        device (torch.device): The device to load the model onto.

    Returns:
        tuple: (model, non_max_suppression function, scale_coords function, letterbox function, model_img_size)

    Raises:
        FileNotFoundError: If the model file does not exist.
        ImportError: If the required utility functions cannot be imported.
    """
    set_yolo_path("yolov7")

    # Import the YOLOv7 model loading function from the experimental module.
    try:
        from binaexperts.SDKs.YOLO.yolov7.models.experimental import attempt_load as attempt_load_v7
    except ImportError as e:
        logger.error(f"❌ Error importing YOLOv7 attempt_load: {str(e)}")
        raise

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Model file not found: {model_path}")

    logger.info(f"🟢 Loading YOLOv7 model from {model_path}")

    try:
        # Load the model using map_location to ensure proper device allocation.
        model = attempt_load_v7(model_path, map_location=device)
        model.to(device)
        model.eval()
    except Exception as e:
        logger.error(f"❌ Error loading YOLOv7 model {model_path}: {str(e)}")
        raise

    # Dynamically import the non-max suppression and coordinate scaling functions.
    non_max_suppression = None
    scale_coords = None
    letterbox_func = None
    try:
        non_max_suppression = dynamic_import("binaexperts.SDKs.YOLO.yolov7.utils.general", "non_max_suppression")
        scale_coords = dynamic_import("binaexperts.SDKs.YOLO.yolov7.utils.general", "scale_coords")
        # Attempt to get the native letterbox function from YOLOv7 utils
        letterbox_func = dynamic_import("binaexperts.SDKs.YOLO.yolov7.utils.datasets", "letterbox")
    except ImportError as e:
        logger.warning(f"⚠ Could not import native YOLOv7 utilities, using fallbacks: {str(e)}")
        non_max_suppression = dynamic_import("binaexperts.SDKs.YOLO.yolov7.utils.general",
                                             "non_max_suppression")
        scale_coords = dynamic_import("binaexperts.SDKs.YOLO.yolov7.utils.general", "scale_coords")
        letterbox_func = fallback_letterbox_yolov7

    # Get model's expected image size, default to (640, 640) if not found
    model_img_size = getattr(model, 'imgsz', (640, 640))
    if isinstance(model_img_size, (int, float)):
        model_img_size = (int(model_img_size), int(model_img_size))
    elif isinstance(model_img_size, list) and len(model_img_size) == 2:
        model_img_size = tuple(model_img_size)
    else:
        model_img_size = (640, 640)

    return model, non_max_suppression, scale_coords, letterbox_func, model_img_size


def save_annotated_image(image, destination, output_format="jpg"):
    """
    Save an annotated image to the specified destination with the given format.

    Parameters:
        image (np.ndarray): The annotated image to save.
        destination (str): The file path to save the image (without extension).
        output_format (str, optional): The format for the saved image (e.g., 'jpg', 'jpeg', 'png'). Default is 'jpg'.

    Raises:
        ValueError: If the output format is not supported.
        RuntimeError: If saving the image fails.
    """
    # Define valid output formats and their extensions
    valid_formats = {
        "jpg": ".jpg",
        "jpeg": ".jpeg",
        "png": ".png"
    }

    # Convert output_format to lowercase and validate
    output_format = output_format.lower()
    if output_format not in valid_formats:
        raise ValueError(f"Unsupported output format: {output_format}. Use 'jpg', 'jpeg', or 'png'.")

    output_path = f"{destination}{valid_formats[output_format]}"
    try:
        success = cv2.imwrite(output_path, image)
        if success:
            logger.info(f"✅ Annotated image saved to {output_path}")
            print(f"✅ Annotated image saved to {output_path}")
        else:
            logger.error(f"❌ Failed to save annotated image to {output_path}")
            raise RuntimeError(f"Failed to save image to {output_path}")
    except Exception as e:
        logger.error(f"❌ Error saving image to {output_path}: {str(e)}")
        raise


def validate_output_format(output_format):
    """
    Validate and return the canonical format for the output image.

    Parameters:
        output_format (str): The format to validate (e.g., 'jpg', 'jpeg', 'png').

    Returns:
        str: The lowercase, validated format.

    Raises:
        ValueError: If the format is not supported.
    """
    valid_formats = {"jpg", "jpeg", "png"}
    format_lower = output_format.lower()
    if format_lower not in valid_formats:
        raise ValueError(f"Unsupported output format: {output_format}. Use 'jpg', 'jpeg', or 'png'.")
    return format_lower


def draw_detections(image: np.ndarray, detections: torch.Tensor, names: list, scale_coords_func, infer_dims: tuple):
    """
    Draws bounding boxes and labels on an image.

    Parameters:
        image (np.ndarray): The original image (OpenCV format).
        detections (torch.Tensor): A tensor of detections in the format [x1, y1, x2, y2, conf, cls].
        names (list): A list of class names.
        scale_coords_func (function): Function to rescale coordinates from inference dimensions to original dimensions.
        infer_dims (tuple): The (width, height) dimensions used for model inference.

    Returns:
        np.ndarray: The image with detections drawn.
    """
    if detections is None or detections.shape[0] == 0:
        return image  # Return original image if no detections

    # Ensure detections are on CPU for numpy conversion
    detections = detections.cpu()

    # Rescale bounding box coordinates to the original image dimensions
    # scale_coords_func expects (img1_shape, coords, img0_shape)
    # img1_shape is the inference size, img0_shape is the original image size
    detections[:, :4] = scale_coords_func(infer_dims, detections[:, :4], image.shape[:2]).round()

    for *xyxy, conf, cls in detections:
        x1, y1, x2, y2 = map(int, xyxy)
        class_id = int(cls)
        confidence = float(conf)

        # Ensure coordinates are within image bounds
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w - 1, x2), min(h - 1, y2)

        class_name = names[class_id] if names and len(names) > class_id else f"Class {class_id}"
        label = f"{class_name}: {confidence:.2f}"

        # Draw rectangle
        color = (0, 255, 0)  # Green color for bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        # Put text label
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        text_x = x1
        text_y = max(10, y1 - 10)  # Position text above the box, or at top if box is too high

        # Draw a filled rectangle behind the text for better readability
        cv2.rectangle(image, (text_x, text_y - text_size[1] - 5), (text_x + text_size[0] + 5, text_y + 5), color, -1)
        cv2.putText(image, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Black text

    return image
