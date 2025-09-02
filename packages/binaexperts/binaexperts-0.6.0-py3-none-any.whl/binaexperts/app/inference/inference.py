# binaexperts/app/inference/inference.py (updated for optimized preprocessing and logging)
import cv2
import torch
import numpy as np
import time
import logging
from collections import deque  # For rolling average FPS
from threading import Thread, Event  # Import Event for graceful shutdown
import queue  # For thread-safe frame queue
from .base import BaseInference  # Import BaseInference
from binaexperts.common.yolo_utils import save_annotated_image, preprocess_image, draw_detections  # Import yolo_utils functions
from binaexperts.app.services.inference_service import InferenceService
from binaexperts.SDKs.camera.camera_manager import CameraManager
from binaexperts.SDKs.camera.multi_camera import CameraThread
from ultralytics import YOLO


# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Inference:
    """A class for finding objects in images and live video.

    This class serves as the primary user-facing entry point for the SDK's
    inference capabilities. It initializes a core InferenceService based on a
    specified model and provides methods to perform detection on static
    images or to create a controller for live, multi-camera inference.

    Attributes:
        inference_service (InferenceService): The underlying service engine
            that handles low-level model loading and prediction tasks.
    """
    def __init__(self, model_type, model_path, device='cuda', iou=0.5, confidence_thres=0.5, img_size=None):
        """Initializes the Inference class and its core service engine.

        Args:
            model_type (str): The model architecture to use (e.g., 'yolov5', 'yolov7').
            model_path (str): The file path to the pre-trained model weights (.pt).
            device (str, optional): The compute device ('cuda' or 'cpu'). 
                Defaults to 'cuda'.
            iou (float, optional): The Intersection over Union (IoU) threshold
                for non-max suppression. Defaults to 0.5.
            confidence_thres (float, optional): The confidence threshold for
                filtering detections. Defaults to 0.5.
            img_size (tuple, optional): The target image size for inference
                (e.g., (640, 640)). If None, it's inferred from the model.
                Defaults to None.
        
        Raises:
            FileNotFoundError: If the specified `model_path` does not exist.
            Exception: On critical model loading or warmup failures.
        """
        self.model_type = model_type
        self.model_path = model_path
        self.device = device
        self.iou = iou
        self.confidence_thres = confidence_thres
        self.img_size = img_size
        self.monitoring_data = []

        # Create and load the core service engine ONCE.
        print("Initializing and loading the core InferenceService...")
        self.inference_service = InferenceService(
            model_type=self.model_type, 
            device=self.device, 
            img_size=self.img_size
        )
        try:
            self.inference_service.load_model(self.model_path)
            self.inference_service.warmup()
            print("✅ Core service loaded successfully.")
        except Exception as e:
            logger.critical(f"❌ Failed to load model in main Inference class: {str(e)}")
            raise

    def local_inference(self, image_path: str, destination=None):
        """Performs inference on a single static image."""
        

        print(f"\n Starting local inference on: {image_path}")
        local_tool = LocalInference(
            inference_service_instance=self.inference_service,
            monitoring_data=self.monitoring_data
        )
        return local_tool.predict(
            image_path=image_path,
            iou_thres=self.iou,
            confidence_thres=self.confidence_thres,
            destination=destination
        )

    def live_inference(self,mode):
        """
        Creates and returns a non-blocking, multi-camera live inference controller
        configured for the specified mode.
        """
        print(f"\n Creating non-blocking live inference controller in '{mode}' mode...")
        
        live_controller = LiveInference(
            mode=mode,
            model_path=self.model_path,
            model_type=self.model_type,
            iou=self.iou,
            confidence_thres=self.confidence_thres
        )
        return live_controller


class LocalInference(BaseInference):
    """A specialized tool for running inference on a single, static image file.

    This class uses a pre-initialized InferenceService to perform object
    detection on an image from a file path. It handles image loading,
    preprocessing, prediction, and visualization.

    It is designed to be created and used by a higher-level factory or
    controller, such as the `Inference` class.

    Attributes:
        service (InferenceService): The core engine used for prediction,
            inherited from BaseInference.
    """

    def __init__(self, inference_service_instance: InferenceService, monitoring_data=None):
        """Initializes the LocalInference tool.

        Args:
            inference_service_instance (InferenceService): An already initialized
                and loaded InferenceService object that will be used to run
                the model.
            monitoring_data (list, optional): A shared list for logging data.
                Defaults to None.
        """
        super().__init__(
            inference_service_instance=inference_service_instance, 
            monitoring_data=monitoring_data
        )

    def predict(self, image_path: str, iou_thres=0.5, confidence_thres=0.5, destination=None):
        """Runs inference on a single image file and optionally saves the result.

        This method takes a file path to an image, runs the full detection
        pipeline, draws the results on the image, and saves the annotated
        image if a destination is provided.

        Args:
            image_path (str): The file path to the image to be processed.
            iou_thres (float, optional): The IoU threshold for non-max
                suppression. Defaults to 0.5.
            confidence_thres (float, optional): The confidence threshold for
                filtering detections. Defaults to 0.5.
            destination (str, optional): The file path (without extension)
                to save the annotated image to. If None, the image is not
                saved. Defaults to None.

        Returns:
            np.ndarray | None: A NumPy array containing the detection data in
            the format [x1, y1, x2, y2, conf, cls], or None if no objects
            were detected or an error occurred.
        """
        if not self.service.model:
            raise RuntimeError("❌ Model is not loaded in the provided InferenceService.")

        try:
            original_img = cv2.imread(image_path)
            if original_img is None:
                logger.warning(f"⚠ Could not load image at {image_path}.")
                return None

            # Correctly pass the loaded image (NumPy array) to the preprocessor
            preprocessed_tensor = self._preprocess_image(original_img)

            # Get the raw detection tensor from the service
            results_list = self.service.predict(
                preprocessed_tensor, 
                iou_thres=iou_thres,
                confidence_thres=confidence_thres
            )
            detections = results_list[0] # This should be a tensor or None

            if detections is None:
                print("No detections found.")
                return None
            
            # Draw the results on a copy of the image
            annotated_img = draw_detections(
                image=original_img.copy(),
                detections=detections,
                names=self.names,
                scale_coords_func=self.service.scale_coords,
                infer_dims=self.imgsz
            )

            # Optionally save the annotated image
            if destination:
                save_annotated_image(annotated_img, destination)

            return detections.cpu().numpy() # Return results as a NumPy array

        except Exception as e:
            logger.error(f"❌ Error during local inference for {image_path}: {str(e)}")
            return None

class LiveInference(BaseInference):
    """An all-in-one, non-blocking controller for multi-camera inference.

    This class provides a high-level interface to manage the entire lifecycle of
    a real-time, multi-camera computer vision application. It handles camera
    discovery, multithreaded frame grabbing, and AI model inference in the
    background, allowing it to be integrated into responsive applications.

    The controller can be configured to run in different modes, such as 'detection'
    (for bounding boxes) or 'segmentation' (for pixel-level masks).

    Attributes:
        mode (str): The operational mode ('detection' or 'segmentation').
        model_path (str): The file path to the AI model weights.
        is_running (bool): A flag indicating if the processing threads are active.
    
    Example:
        >>> inference_controller = LiveInference(
        ...     mode='segmentation',
        ...     model_path='yolov8n-seg.pt'
        ... )
        >>> inference_controller.start()
        >>> # Main app loop runs here, getting frames...
        >>> # frame = inference_controller.get_latest_frame('USB_0')
        >>> inference_controller.stop()
    """
    def __init__(self, mode, model_path, model_type=None, device='cuda', iou=0.45, confidence_thres=0.25):
        """Initializes the LiveInference controller.

        Args:
            mode (str): The inference mode to run. Must be either 'detection' or
                'segmentation'.
            model_path (str): The path to the AI model file (e.g., yolov7.pt).
            model_type (str, optional): The model architecture. Required for
                'detection' mode (e.g., 'yolov5', 'yolov7'). Defaults to None.
            device (str, optional): The compute device ('cuda' or 'cpu').
                Defaults to 'cuda'.
            iou (float, optional): The Intersection over Union (IoU) threshold for
                detection. Defaults to 0.45.
            confidence_thres (float, optional): The confidence threshold for
                detection. Defaults to 0.25.
        """
        # 1. Create the InferenceService instance first
        inference_service = InferenceService(
            model_type=model_type,
            device=device
        )

        # 2. Pass the created instance to the parent (BaseInference) constructor
        super().__init__(inference_service_instance=inference_service)

        # --- Configuration ---
        self.mode = mode
        self.model_path = model_path
        self.iou_thres = iou
        self.confidence_thres = confidence_thres
        
        # --- State Variables ---
        self.model = None
        self.camera_threads = {}
        self.processed_frames = {}
        self.is_running = False
        self.processing_thread = None
        
        # --- Visualization ---
        self.colors = self._generate_distinct_colors(80)

    
    def _generate_distinct_colors(self, num_colors):
        """Generates a list of visually distinct BGR colors."""
        hues = np.linspace(0, 179, num_colors, dtype=np.uint8)
        saturations = np.full_like(hues, 255)
        values = np.full_like(hues, 200)
        hsv_colors = np.stack([hues, saturations, values], axis=1)
        bgr_colors = cv2.cvtColor(
            hsv_colors.reshape(-1, 1, 3), cv2.COLOR_HSV2BGR)
        return bgr_colors.reshape(-1, 3)

    def _draw_segmentation_results(self, image, results, alpha=0.4):
        """Draws segmentation masks and labels."""
        overlay = image.copy()
        labels_to_draw = []
        if results[0].masks is not None:
            for i, mask in enumerate(results[0].masks.data):
                mask = mask.cpu().numpy().astype(bool)
                box = results[0].boxes[i]
                class_id = int(box.cls)
                color = self.colors[class_id].tolist()
                overlay[mask] = color
                class_name = results[0].names[class_id]
                label = f"{class_name}: {float(box.conf):.2f}"
                x1, y1, _, _ = box.xyxy[0].cpu().numpy().astype(int)
                labels_to_draw.append({'text': label, 'pos': (x1, y1)})
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        for item in labels_to_draw:
            label, (x1, y1) = item['text'], item['pos']
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(image, (x1, y1 - h - 10),
                          (x1 + w + 10, y1), (0, 0, 0), cv2.FILLED)
            cv2.putText(image, label, (x1 + 5, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return image

    def _initialize_cameras(self):
        """Discovers and prepares camera threads."""
        print(" Discovering all connected cameras...")
        device_lister = CameraManager()
        all_cameras_info = (device_lister.list_usb_cameras() +
                            device_lister.list_daheng_cameras() +
                            device_lister.list_zds_cameras())
        for cam_info in all_cameras_info:
            cam_id = f"{cam_info['type']}_{cam_info['index']}"
            manager = CameraManager()
            is_opened = False
            if cam_info['type'] == "USB":
                is_opened = manager.open_usb_camera(cam_info['index'])
            # Add other camera types if needed
            if is_opened:
                thread = CameraThread(manager, cam_id)
                self.camera_threads[cam_id] = thread

    def _process_frame(self, frame: np.ndarray, camera_id: int):
        """
        Process a single frame and return annotated frame with detections.
        This method will use the _preprocess_image and _postprocess_detections from BaseInference,
        and then the centralized draw_detections utility.
        """
        frame_monitoring_data = {
            "type": "live_inference",
            "camera_id": camera_id,
            "detections": None,
            "total_frame_processing_time_ms": 0,  # New metric
            "model_inference_time_ms": 0,  # From service.predict
            "status": "failed"
        }

        if self.service.model is None:
            logger.error(
                f"Camera {camera_id}: Model not loaded, cannot process frame.")
            frame_monitoring_data["status"] = "model_not_loaded"
            self.monitoring_data.append(frame_monitoring_data)
            return frame  # Return original frame if model isn't loaded

        try:
            # Start timing for full frame processing
            total_process_start_time = time.time()

            # Preprocess the frame for model input
            image_tensor = self._preprocess_image(frame)

            # Perform inference
            with torch.no_grad():
                # self.service.predict expects a single image tensor (batch size 1)
                # It returns a list of detections for that single image.
                detections_list = self.service.predict(image_tensor, iou_thres=self.iou_thres,
                                                       confidence_thres=self.confidence_thres)
                # Get detections for the single image
                detections = detections_list[0]

            if detections is None or detections.numel() == 0:
                logger.debug(f"Camera {camera_id}: ⚠️ No objects detected.")
                frame_monitoring_data["status"] = "no_detections"
                frame_monitoring_data["total_frame_processing_time_ms"] = (
                    time.time() - total_process_start_time) * 1000
                self.monitoring_data.append(frame_monitoring_data)
                return frame  # Return original frame if no detections

            logger.info(
                f"Camera {camera_id}: ✅ Detections found: {detections.shape[0]} objects.")

            # Draw detections using the centralized utility function
            annotated_frame = draw_detections(
                image=frame.copy(),  # Draw on a copy of the frame
                detections=detections,
                names=self.names,
                scale_coords_func=self.service.scale_coords,
                infer_dims=self.imgsz
            )

            total_process_end_time = time.time()  # End timing for full frame processing
            frame_monitoring_data["total_frame_processing_time_ms"] = (
                total_process_end_time - total_process_start_time) * 1000
            # Convert tensor to list
            frame_monitoring_data["detections"] = detections.tolist()
            frame_monitoring_data["status"] = "success"
            self.monitoring_data.append(frame_monitoring_data)
            return annotated_frame

        except Exception as e:
            logger.error(
                f"Camera {camera_id}: ❌ Error processing frame: {str(e)}")
            frame_monitoring_data["status"] = f"error: {str(e)}"
            frame_monitoring_data["total_frame_processing_time_ms"] = (
                time.time() - total_process_start_time) * 1000
            self.monitoring_data.append(frame_monitoring_data)
            return frame  # Return original frame on error

    def _processing_loop(self):
        """The main work loop that runs in a background thread."""
        prev_frame_time = {}
        fps_buffer = {}

        while self.is_running:
            frames_to_process = {}
            for cam_id, thread in self.camera_threads.items():
                latest_frame = thread.get_latest_frame()
                if latest_frame is not None:
                    frames_to_process[cam_id] = latest_frame

            for cam_id, frame in frames_to_process.items():
                final_frame = frame.copy()

                if self.mode == 'detection':
                    # This uses the original _process_frame inherited from BaseInference
                    final_frame = self._process_frame(frame, cam_id)

                elif self.mode == 'segmentation':
                    results = self.model(frame, verbose=False)
                    final_frame = self._draw_segmentation_results(
                        final_frame, results)

                # --- FPS Calculation and Display ---
                if cam_id not in prev_frame_time:
                    prev_frame_time[cam_id] = time.time()
                    fps_buffer[cam_id] = []

                new_frame_time = time.time()
                time_diff = new_frame_time - prev_frame_time[cam_id]
                prev_frame_time[cam_id] = new_frame_time

                if time_diff > 0:
                    current_fps = 1 / time_diff
                    fps_buffer[cam_id].append(current_fps)
                    if len(fps_buffer[cam_id]) > 30:
                        fps_buffer[cam_id].pop(0)

                avg_fps = sum(
                    fps_buffer[cam_id]) / len(fps_buffer[cam_id]) if fps_buffer[cam_id] else 0

                fps_text = f"Processing FPS: {avg_fps:.1f}"
                cv2.putText(final_frame, fps_text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # --- End of FPS Block ---

                self.processed_frames[cam_id] = final_frame
            time.sleep(0.001)

    # --- PUBLIC CONTROL METHODS ---
    def start(self):
        """Initializes and starts the non-blocking inference process."""
        if self.is_running:
            print("Inference is already running.")
            return

        self._initialize_cameras()

        print(f"\n Loading {self.mode} engine...")
        if self.mode == 'detection':
            # This correctly tells the service to load the model
            self.service.load_model(self.model_path)
            self.model = self
            self.names = self.service.names
            self.imgsz = self.service.imgsz
        elif self.mode == 'segmentation':
            # For segmentation, the model is the YOLO object
            self.model = YOLO(self.model_path)
        print(f" {self.mode.capitalize()} engine loaded successfully.")

        self.is_running = True
        for thread in self.camera_threads.values():
            thread.start()

        self.processing_thread = Thread(
            target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        print(f"\nLiveInference started in '{self.mode}' mode.")

    def stop(self):
        """Stops all background threads and performs cleanup."""
        if not self.is_running:
            return

        print("\n🛑 Stopping LiveInference...")
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join()

        for thread in self.camera_threads.values():
            thread.stop()
            thread.join()

        print("✅ LiveInference stopped.")

    def get_latest_frame(self, cam_id):
        """Public method to get the latest processed frame for a specific camera."""
        return self.processed_frames.get(cam_id)
