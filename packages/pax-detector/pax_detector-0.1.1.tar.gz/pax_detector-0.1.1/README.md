# Pax Case: Object and Car Make Classification

This project provides a vision pipeline for object and car make classification. It includes a command-line interface (CLI) for processing images and a Gradio-based web interface for interactive demonstrations.

## Problem Statement

The goal is to build a tool that can:
1.  **Object Classification**: Identify whether an image contains a car, truck, bicycle, or person.
2.  **Car Make Classification**: If the image contains a car, identify its make (e.g., Volkswagen, Chevrolet).

The solution must be scalable to handle up to 10 million images daily and be flexible enough to accommodate future classification tasks.

## Features

- **Two-Stage Pipeline**:
    - **Object Detection**: Uses a YOLOv8 model to detect objects (person, bicycle, car, truck).
    - **Car Make Classification**: Uses a Google SigLIP model fine-tuned on the Stanford Cars dataset to classify the make of detected cars.
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

To process a single image:
```bash
detector --image_path /path/to/your/image.jpg
```

To process all images in a directory:
```bash
detector --images_dir /path/to/your/images/
```

**Using a Configuration File**:

You can also run the CLI using a `config.yml` file to specify parameters.

*Example `config.yml`:*
```yaml
image_path: '/path/to/your/image.jpg'
confidence: 0.6
```

*Run with config*:
```bash
detector --config config.yml
```

**Arguments**:
- `--image_path`: Path to a single input image.
- `--images_dir`: Path to a directory of images.
- `--config`: Path to a YAML configuration file.
- `--confidence`: Confidence threshold for object detection (default: 0.5).

**Example**:
```bash
detector --image_path datasets/car-camera/images/00001.jpg --confidence 0.4
```

This will process the image and print the JSON output to the console.

## Extensibility

For details on how to add more classification types (e.g., helmet color, t-shirt color), please refer to the `SCALING_STRATEGY.md` document, which outlines the proposed architecture for extending the pipeline.
