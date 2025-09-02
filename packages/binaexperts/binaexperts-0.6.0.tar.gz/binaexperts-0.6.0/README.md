# BinaExperts SDK

**BinaExperts SDK** is a comprehensive toolkit for computer vision, designed to empower developers and researchers in building innovative visual solutions. Focused on scalability and versatility, it provides a robust foundation for creating state-of-the-art computer vision applications. Its architecture supports seamless integration with various platforms and is continuously evolving to address emerging challenges and opportunities in the field.


## Installation

Install the BinaExperts SDK directly from PyPI:

```bash
pip install binaexperts
```
If you need additional dependencies for inference, install with:

```bash
pip install binaexperts[inference]
```

This will install additional packages required for running inference tasks, such as PyTorch and torchvision.
Ensure that you have a compatible CUDA setup if using GPU acceleration.

## Usage

Once installed, you can start leveraging the SDK’s two core functionalities:

- **Dataset Conversion**: Easily convert datasets between various formats using a unified API. The conversion module supports both file-based and in-memory operations and currently supports the following formats:
  - **COCO**
  - **YOLO**
  - **YOLO - Oriented Bounding Boxes**
  - **BinaExperts**
- **Inference**: Perform predictions on static images or live video streams. Inference currently supports YOLOv5 and YOLOv7 models for local and live applications.


## 1. Dataset Conversion

The `Convertor` class simplifies the process of converting datasets between formats such as COCO, YOLO, and BinaExperts.

```python
import binaexperts.convertors

# Initialize the Convertor
convertor = binaexperts.convertors.Convertor()

# Convert from a source dataset to a target format
converted_output = convertor.convert(
    target_format='yolo',
    source='path/to/source_dataset.zip',  # Use 'source' instead of 'source_path' to match method signature
    destination='path/to/target_dataset.zip'  # Optional; if omitted, returns a file-like object.
)

# Save the output if it's returned as an in-memory object
if converted_output:
    with open("output_dataset.zip", "wb") as f:
        f.write(converted_output.read())

print("Conversion completed successfully!")

```
### In-Memory IO Conversion Example

In this example, we demonstrate how to convert a dataset directly from an in-memory BytesIO object and obtain the result in memory—no disk I/O required.
```python
import io
from binaexperts.convertors import Convertor

# Initialize the Convertor
convertor = Convertor()


# Replace 'zip_file_path/file.zip' with the actual path to your zip file
try:
    with open('zip_file_path/file.zip', 'rb') as f:
        source_in_memory_zip = io.BytesIO(f.read())
except FileNotFoundError:
    print("Error: The source file was not found. Please check the path.")
    exit()

print(source_in_memory_zip)
# If you want the output to also be an in-memory BytesIO object, set destination=None
converted_output = convertor.convert(
    target_format='coco',
    source=source_in_memory_zip,
    # destination=None
    destination='path/to/target_dataset.zip'  # Set to None to get BytesIO object as return
)

# Save the output if it's returned as an in-memory object
if converted_output:
    # Ensure the BytesIO object's pointer is at the beginning before reading for saving
    converted_output.seek(0)
    with open("output_dataset.zip", "wb") as f:
        data_written_bytes = f.write(converted_output.read())

    print("Conversion completed successfully!")
    print(f"Data written to output_dataset.zip: {data_written_bytes} bytes")
    print(f"Type of converted_output: {type(converted_output)}")
    print(f"Converted output object: {converted_output}")
else:
    print(
        """Conversion completed, but no in-memory object was 
           returned (possibly due to a destination path being provided to the convert method).""")
```
**Summary**: Use the conversion module to seamlessly switch between dataset formats with minimal configuration, whether working with files on disk or in-memory streams.

---
## 2. Inference

The SDK now includes inference capabilities that allow you to run predictions on images and video streams.

### Static Image Inference

Use the `image_inference` function to perform predictions on a single image. Choose between **YOLOv5** or **YOLOv7** as your model type.

```python
from binaexperts.app import Inference

# Initialize local inference (choose 'yolov5' or 'yolov7')
inf = Inference(model_type='yolov5',
                device='cuda',
                model_path="path/to/model.pt",
                iou=0.5,
                confidence_thres=0.5)

result = inf.local_inference(image_path="path/to/image",
                             destination="path/to.destination")
```
For a complete, runnable example demonstrating how to use this class, please refer to the `run_local_inference.py` script located in the project's root directory.

### How to Run

The script is launched from the terminal. You must provide the path to a model file and the image you want to process.

### General Usage
```bash
python run_local_inference.py --model <path_to_model> --image <path_to_image> [options]
```
**Arguments:**
* `--model <path_to_model>`: The path to the detection model file (e.g., `yolov7.pt`).
* `--image <path_to_image>`: The path to the image file you want to analyze.
* `--model-type <type>`: **(Optional)** The model architecture. Defaults to `'yolov7'`.
    * Use `'yolov5'` for YOLOv5 models.
    * Use `'yolov7'` for YOLOv7 models.
* `--dest <name>`: **(Optional)** The base filename for the saved, annotated image. Defaults to `'result'`.

### Live Inference

For real-time applications, the SDK provides the advanced `LiveInference` class. This non-blocking controller is designed for high-performance, multi-camera scenarios and can be configured to run in different modes, such as `'detection'` or `'segmentation'`.

It abstracts away the complexity of concurrent video processing. By dedicating a background thread to each camera, it provides a simple yet powerful interface for building responsive, multi-camera applications without needing to manage threads manually.
```python
from binaexperts.app import Inference

# Initialize live inference (choose 'yolov5' or 'yolov7')
inf = Inference(
    model_type='yolov7',
    model_path="path/to/yolov7.pt",
)
# Available modes: 'detection', 'segmentation'
live_controller = inf.live_inference(mode='detection')

```
For a complete, runnable example demonstrating how to use this class, please refer to the `run_live_inference.py` script located in the project's root directory.

### How to Run 

The script is launched from the terminal. You must specify an inference mode and provide a path to a compatible model file using the following command structure.

### General Usage
```bash
python run_live_inference.py --mode <mode_choice> --model <path_to_model> [options]

```
**Arguments:**
* `--mode <mode_choice>`: The inference mode to run.
    * Use `'detection'` for bounding boxes.
    * Use `'segmentation'` for precise outlines (masks).
* `--model <path_to_model>`: The path to the corresponding model file.
* `--model-type <type>`: **(Optional)** Required only when `mode` is `'detection'`.
    * Use `'yolov5'` for YOLOv5 models.
    * Use `'yolov7'` for YOLOv7 models.

---


## Features

- **Dataset Conversion**: Convert datasets effortlessly between various formats.
- **Inference**: Run predictions on static images and live streams using YOLOv5/YOLOv7.
- **Flexible Multi-Camera LiveInference**: Run high-performance, non-blocking inference on multiple live camera streams using a unified controller with switchable modes for tasks like object detection and instance segmentation.
- **Modular Design**: Easily extendable for future formats, training pipelines, and additional inference features.
- **Flexible IO**: Supports both file-based and in-memory operations for versatile deployment scenarios.

---

## Future Roadmap

### Data Preparation
- Enhanced conversion tools and additional format support.
- Automated dataset validation to ensure data integrity.

### Training
- Auto-training workflows with model selection, hyperparameter tuning, and comprehensive training pipelines.

### Inference Enhancements
- Further improvements for local fast Inference
- Further improvements for live inference.
- Expanded support for additional model architectures.

### Community Suggestions
- We welcome your ideas and contributions to further enhance the SDK.

---

## Project Structure

```
binaexperts/
│
├── bina/
│   ├── app/
│   ├── services/
│   ├── __init__.py
│   
│
├── common/
│   ├── __init__.py
│   ├── loadhelpers.py
│   ├── logger.py
│   ├── setup_utils.py
│   ├── utils.py
│   ├── yolo_utils.py
│
├── convertors/
│   ├── schema/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── const.py
│   │   ├── convertor.py
│
├── SDKs/
│   ├── YOLO/
│   │   ├── yolov5/
│   │   ├── yolov7/
│   │   ├── __init__.py
│
├── __init__.py
```

---

## Contributing

The **BinaExperts SDK** was designed and developed by the technical team at **BinaExperts**, led by **Nastaran Dab** and **Mahdi Tajdari**. Contributions, bug reports, documentation improvements, and feature suggestions are welcome. Please reach out to the project team for contribution guidelines.

---

## Acknowledgments

Special thanks to **Nastaran Dab** and **Mahdi Tajdari** for their leadership and contributions in developing and maintaining the **BinaExperts SDK**.

---

## License

This project is licensed under the **MIT License**.
