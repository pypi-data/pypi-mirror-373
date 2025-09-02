import os
import torch
import time
from binaexperts.common.logger import get_logger
from binaexperts.common.yolo_utils import (
    fallback_letterbox_yolov5, fallback_letterbox_yolov7,
    load_model_yolov5, load_model_yolov7
)

logger = get_logger(__name__)


class InferenceService:
    def __init__(self, model_type="yolov5", device=None, img_size=None):
        """
        Initialize the inference service.

        :param model_type: Type of YOLO model ('yolov5' or 'yolov7').
        :param device: Device to run inference ('cuda' or 'cpu').
        :param img_size: Optional. The target image size for inference (height, width).
                         If None, it will be inferred from the loaded model.
        """
        self.model_type = model_type.lower() if model_type else None

        # Determine device for PyTorch/CUDA.
        self.device = torch.device("cuda" if torch.cuda.is_available() and device != "cpu" else "cpu")

        self.model = None  # PyTorch model
        self.non_max_suppression = None
        self.scale_coords = None
        self.letterbox = None
        self.names = []
        self.imgsz = img_size

        logger.info(f"🟢 Using device: {self.device}.")

        # Set cuDNN benchmark to False for troubleshooting severe slowdowns.
        # This was identified as the cause of 0 FPS in previous logs on your system.
        if self.device.type == 'cuda':
            torch.backends.cudnn.benchmark = False
            logger.info("⚡ torch.backends.cudnn.benchmark set to False to fix severe performance issues.")

    def load_model(self, model_path: str):
        """
        Load the YOLO model along with associated functions (PyTorch .pt format).

        :param model_path: Path to the YOLO model weights (.pt).
        """

        if self.model_type is None:
            logger.warning("⚠ model_type is None, skipping model loading in InferenceService.")
            return
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Model file not found: {model_path}")

        model_loader_func = None
        if self.model_type == "yolov5":
            model_loader_func = load_model_yolov5
        elif self.model_type == "yolov7":
            model_loader_func = load_model_yolov7
        else:
            raise ValueError(f"❌ Unsupported model type: {self.model_type}")

        try:
            self.model, self.non_max_suppression, self.scale_coords, \
                self.letterbox, model_img_size_from_model = model_loader_func(model_path, self.device)
            self.model.eval()  # Ensure model is in evaluation mode
        except Exception as e:
            logger.error(f"❌ Failed to load {self.model_type.upper()} PyTorch model from {model_path}: {str(e)}")
            raise

        # If img_size was not explicitly provided during init, use the one from the model
        if self.imgsz is None:
            self.imgsz = model_img_size_from_model
        logger.info(f"🟢 Model inference size set to: {self.imgsz}")

        # Store class names if available on the model
        if hasattr(self.model, 'names'):
            self.names = self.model.names
            logger.info(f"✅ Class names loaded: {self.names}")
        else:
            logger.warning("⚠ PyTorch model does not have a 'names' attribute. Class labels might not be available.")
            self.names = [f'class_{i}' for i in range(1000)]  # Generic list for placeholders

        logger.info(f"✅ {self.model_type.upper()} PyTorch Model loaded successfully.")

        # Check and set the default letterbox function if None
        if self.letterbox is None:
            logger.warning(f"⚠ Letterbox function is None for {self.model_type}. Using fallback.")
            self.letterbox = fallback_letterbox_yolov5 if self.model_type == "yolov5" else fallback_letterbox_yolov7
        logger.info(f"🟢 Letterbox function set successfully: {self.letterbox.__name__}")

    def warmup(self):
        """
        Performs a dummy inference run to warm up the model and allocate necessary resources.
        This helps to reduce the latency of the first actual prediction.
        """
        if self.model is None:
            logger.warning("⚠ Cannot warm up PyTorch model: Model is not loaded.")
            return

        if self.imgsz is None:
            logger.warning("⚠ Cannot warm up model: Inference size (imgsz) is not set.")
            return

        logger.info("🔥 Warming up model...")
        try:
            # Create a dummy input tensor with the expected shape (batch_size=1, channels=3, height, width)
            # Assuming self.imgsz is (width, height)
            dummy_input_shape = (1, 3, self.imgsz[1], self.imgsz[0])

            dummy_input = torch.zeros(dummy_input_shape).to(self.device)
            logger.info(f"Warmup dummy input shape: {dummy_input.shape} on device: {self.device}")

            with torch.no_grad():
                _ = self.model(dummy_input)

            logger.info("✅ Model warmed up successfully.")
        except Exception as e:
            logger.error(f"❌ Error during model warm-up: {str(e)}")

    def predict(self, image_tensor: torch.Tensor, iou_thres=0.5, confidence_thres=0.5):
        """
        Runs inference on a single preprocessed image tensor.

        :param image_tensor: A PyTorch tensor representing a single preprocessed image.
                              Shape: (1, C, H, W).
        :param iou_thres: IoU threshold for non-max suppression.
        :param confidence_thres: Confidence threshold for object detection.
        :return: A list of detection results for the single image.
                 Each element is a tensor of detections [x1, y1, x2, y2, conf, cls] or None.
        """
        if self.model is None:
            raise RuntimeError("❌ PyTorch model is not loaded. Call load_model() first.")

        if self.letterbox is None:
            raise RuntimeError("❌ Letterbox function is None. Ensure the model is correctly initialized.")
        if self.non_max_suppression is None:
            raise RuntimeError("❌ Non-Max Suppression function is None. Ensure the model is correctly initialized.")
        if self.scale_coords is None:
            raise RuntimeError("❌ Scale coordinates function is None. Ensure the model is correctly initialized.")

        if not isinstance(image_tensor, torch.Tensor):
            raise TypeError("❌ Input must be a PyTorch tensor.")
        if image_tensor.dim() != 4 or image_tensor.shape[0] != 1:
            raise ValueError(
                f"❌ Input tensor must have 4 dimensions and batch size 1 (1, C, H, W), got {image_tensor.shape}")

        logger.debug(f"Running inference on a single image using PyTorch.")
        logger.debug(f"Input tensor shape for model: {image_tensor.shape}")

        model_forward_start_time = time.time()

        # Ensure input tensor is on the correct device for PyTorch
        image_tensor = image_tensor.to(self.device)
        with torch.no_grad():
            outputs = self.model(image_tensor)[0]
        # Ensure GPU operations are complete before stopping timer
        if self.device.type == 'cuda':
            torch.cuda.synchronize()
        model_forward_end_time = time.time()
        logger.debug(
            f"Model forward pass time (PyTorch): {(model_forward_end_time - model_forward_start_time) * 1000:.2f} ms")

        logger.debug(f"Raw model output shape: {outputs.shape}")

        # Validate outputs before further processing
        if outputs is None or outputs.numel() == 0:
            logger.warning("⚠ Model did not return any outputs. Returning None.")
            return [None]  # Return list with None for single image

        # Apply Non-Max Suppression. This function typically returns a list of tensors,
        # where each tensor corresponds to the detections for one image in the batch.
        try:
            nms_start_time = time.time()
            detections_list = self.non_max_suppression(outputs, conf_thres=confidence_thres, iou_thres=iou_thres)
            if self.device.type == 'cuda':
                torch.cuda.synchronize()
            nms_end_time = time.time()
            logger.debug(f"NMS time: {(nms_end_time - nms_start_time) * 1000:.2f} ms")

        except Exception as e:
            logger.error(f"❌ Error during Non-Max Suppression: {str(e)}")
            return [None]  # Return list with None for single image

        logger.debug(f"Model output after NMS (list of tensors, len={len(detections_list)}): {detections_list}")

        return detections_list  # This will be a list containing one tensor for a single image