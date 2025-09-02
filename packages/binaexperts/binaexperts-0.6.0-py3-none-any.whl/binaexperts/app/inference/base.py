
from binaexperts.app.services.inference_service import InferenceService
import cv2
import torch
import numpy as np
from binaexperts.common.logger import get_logger
# Import preprocess_image directly
from binaexperts.common.yolo_utils import preprocess_image

logger = get_logger(__name__)


class BaseInference:
    
    """
    A base class for inference functionality that accepts a pre-initialized
    InferenceService instance.
    """
    def __init__(self, inference_service_instance: InferenceService, monitoring_data=None):
        """
        Initializes the base class with an existing, pre-loaded service instance.
        """
        if not isinstance(inference_service_instance, InferenceService):
            raise TypeError("The provided instance must be an object of the InferenceService class.")

        self.service = inference_service_instance
        self.names = self.service.names
        self.imgsz = self.service.imgsz
        self.monitoring_data = [] if monitoring_data is None else monitoring_data

        if self.service.model is None:
            logger.critical("❌ BaseInference initialized with an InferenceService that has no model loaded.")

    

    def _preprocess_image(self, image: np.ndarray):
        """
        Preprocess a single image (numpy array) or frame for inference.

        This method is primarily for live inference where the image is already in memory.
        For static image inference, the `preprocess_image` utility function from
        `yolo_utils` should be used directly with the image path.

        Parameters:
            image (np.ndarray): Input image (OpenCV BGR format).

        Returns:
            torch.Tensor: Preprocessed image tensor ready for inference (with batch dimension).
        """
        if self.imgsz is None:
            raise RuntimeError(
                "❌ Model inference size (imgsz) is not set. Load model first.")
        if self.service.letterbox is None:
            raise RuntimeError(
                "❌ Letterbox function is not set. Load model first.")

        try:
            # Apply letterbox resizing
            image_resized, _, _ = self.service.letterbox(
                image, new_shape=self.imgsz, stride=32, auto=False)

            # Convert from BGR to RGB and rearrange dimensions to (channels, height, width).
            image_rgb = image_resized[:, :, ::-1]  # BGR to RGB
            image_transposed = image_rgb.transpose(2, 0, 1)  # HWC to CHW
            image_contiguous = np.ascontiguousarray(image_transposed)

            # Convert to PyTorch tensor, normalize, and add batch dimension
            image_tensor = torch.from_numpy(image_contiguous).float() / 255.0
            image_tensor = image_tensor.unsqueeze(0).to(
                self.service.device)  # Ensure tensor is on correct device
            return image_tensor
        except Exception as e:
            logger.error(
                f"❌ Error during _preprocess_image (for live stream): {str(e)}")
            raise

    def _postprocess_detections(self, outputs: torch.Tensor, original_shape: tuple, iou_thres: float,
                                confidence_thres: float):
        """
        Postprocess detection outputs, applying NMS and scaling boxes.
        This method is primarily for live inference where raw model outputs are processed.
        For static image inference, NMS is handled by InferenceService.predict, and scaling/drawing
        is handled by local_inference.predict.

        Parameters:
            outputs (torch.Tensor): Raw model detection outputs before NMS.
            original_shape (tuple): Shape of the original image or frame (height, width).
            iou_thres (float): IoU threshold for non-max suppression.
            confidence_thres (float): Confidence threshold for filtering detections.

        Returns:
            List of detections (each a list [x1, y1, x2, y2, conf, cls]) with scaled coordinates.
        """
        if outputs is None or outputs.numel() == 0:
            return []

        # Apply NMS using the service's NMS function
        try:
            # non_max_suppression typically returns a list of tensors (one per batch item).
            # For a single frame, it will be a list containing one tensor.
            detections_list = self.service.non_max_suppression(outputs, conf_thres=confidence_thres,
                                                               iou_thres=iou_thres)
            if not detections_list or detections_list[0] is None or detections_list[0].numel() == 0:
                return []
            # Get the detections for the single frame
            detections = detections_list[0]
        except Exception as e:
            logger.error(
                f"❌ Error during non_max_suppression in _postprocess_detections: {str(e)}")
            return []

        # Scale coordinates to original image dimensions using the service's scale_coords function
        # self.imgsz is (width, height) from the model
        # detections[:, :4] are the bounding box coordinates [x1, y1, x2, y2]
        # original_shape[:2] is (height, width) of the original frame
        try:
            scaled_detections = self.service.scale_coords(
                self.imgsz, detections[:, :4], original_shape[:2]).round()
            # Combine scaled coordinates with confidence and class
            final_detections = torch.cat(
                (scaled_detections, detections[:, 4:]), dim=1)
            return final_detections.tolist()  # Convert to list of lists for easier handling
        except Exception as e:
            logger.error(
                f"❌ Error scaling coordinates in _postprocess_detections: {str(e)}")
            return []