# Pax Case: Object and Car Make Classification

This project provides a vision pipeline for object and car make classification. It includes a command-line interface (CLI) for processing images.

## Features

- **Two-Stage Pipeline**:
    - **Object Detection**: Uses a YOLOv8 model to detect objects (person, bicycle, car, truck).
    - **Car Make Classification**: Uses a Google SigLIP model fine-tuned on the Roboflow Car Make Model Recognition dataset to classify the make of detected cars.
- **CLI Tool** (`detector`):
    - Process single images or directories of images from the command line.
    - Supports configuration via a YAML file.
    - Adjustable confidence threshold for object detection.
- **Scalability and Extensibility**:
    - The architecture is designed to be scalable and extensible. See `SCALING_STRATEGY.md` for a detailed plan on scaling to 10M images/day and adding new classification types.

## Package usage
1. **Install PyPi package**
  ```bash
  pip install pax-detector
  ```

## Local Setup and Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd pax-case
    ```

2.  **Install dependencies**:
    It is recommended to use a virtual environment. This project uses `uv` https://docs.astral.sh/uv/getting-started/installation/ for package management.
    ```bash
    uv venv 
    source .venv/bin/activate

    uv pip install -e . # To build package locally
    uv sync # If want to install local dependencies 
    ```

## Usage

### Command-Line Interface (CLI)

The CLI tool (`detector`) is used for processing individual images.

**Basic Usage**:

**Using a Configuration File**:

You can also run the CLI using a `config.yml` file to specify parameters.

*Example `config.yml`:*
```yaml
image_path: '/Users/fnayres/Downloads/captura-de-tela-2022-12-08-as-13.36.55.webp'
images_dir: null
confidence: 0.5

pipeline:
  - name: object_detection
    class: classification.objects.object_classifier.ObjectClassfier
    params:
      model_version: yolov8l.pt

  - name: car_make_classification
    class: classification.makes.siglip_classifier.MakeClassifier
    depends_on: object_detection
    condition: "'car' in detection['class_name'] or 'truck' in detection['class_name']" # accept None condition
    
```

*Run with config*:
```bash
detector --config config.yml
# or
uv run detector --config config.yml
```

To process a single image:
```bash
detector --image_path /path/to/your/image.jpg
# or 
uv run detector --image_path /path/to/your/image.jpg
```

To process all images in a directory:
```bash
detector --images_dir /path/to/your/images/
# or
uv run detector --images_dir /path/to/your/images/
```

**Arguments**:
- `--image_path`: Path to a single input image.
- `--images_dir`: Path to a directory of images.
- `--config`: Path to a YAML configuration file.
- `--confidence`: Confidence threshold for object detection (default: 0.5).

This will process the image and print the JSON output to the console.

## Extensibility

For details on how to add more classification types (e.g., helmet color, t-shirt color), please refer to the `SCALING_STRATEGY.md` document, which outlines the proposed architecture for extending the pipeline.
