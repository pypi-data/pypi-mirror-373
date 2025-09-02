import json
import argparse
from pathlib import Path
import numpy as np
from rich.console import Console
from rich.table import Table

from utils.utils import NumpyEncoder, parse_config_yaml
from pipeline.vision_pipeline import VisionPipeline

def main():
    parser = argparse.ArgumentParser(description="Detect objects and classify car makes in an image.")
    parser.add_argument('--image_path', type=str, help='Path to a single image file. Overrides config file setting.')
    parser.add_argument('--images_dir', type=str, help='Path to a directory of image files. Overrides config file setting.')
    parser.add_argument('--config', type=str, default='configs/pipeline_config.yml', help='Path to a config.yml file.')
    parser.add_argument('--confidence', type=float, help='Confidence threshold for object detection. Overrides config file setting.')
    parser.add_argument('--output_dir', type=str, default='runs/detections', help='Directory to save the output images.')
    args = parser.parse_args()
    config = parse_config_yaml(args.config)
    if not config:
        print(f"Error: Could not read or parse config file at {args.config}")
        return

    image_path = args.image_path or config.get('image_path')
    images_dir = args.images_dir or config.get('images_dir')
    confidence = args.confidence or config.get('confidence', 0.5)

    if not image_path and not images_dir:
        print("Error: No image_path or images_dir specified in command line or config file.")
        return

    if image_path and images_dir:
        print("Error: Please specify either --image_path or --images_dir, not both.")
        return

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        pipeline = VisionPipeline(config_path=args.config)
        
        if image_path:
            if not Path(image_path).is_file():
                print(f"Error: Image file not found at {image_path}")
                return
            detections = pipeline.process_image(image_path, confidence, args.output_dir)
            results = {Path(image_path).name: detections}
        elif images_dir:
            if not Path(images_dir).is_dir():
                print(f"Error: Directory not found at {images_dir}")
                return
            results = pipeline.process_multiple_images(images_dir, confidence, args.output_dir)
        else:
            results = {}

    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return

    if results:
        for img_name, detections in results.items():
            json_filename = Path(img_name).stem + '.json'
            json_output_path = output_path / json_filename
            with open(json_output_path, 'w') as f:

                data_to_dump = detections if images_dir or image_path else results
                json.dump(data_to_dump, f, cls=NumpyEncoder, indent=4)

        print(f"Results saved to {json_output_path}")

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Image", style="dim")
        table.add_column("Top Prediction")
        table.add_column("Confidence", justify="right")

        for img_name, detections in results.items():
            if not detections:
                table.add_row(img_name, "No objects detected", "")
                continue

            top_prediction = max(detections, key=lambda p: p.get('object_detection', {}).get('confidence', 0))

            obj_details = top_prediction.get('object_detection', {})
            make_details_list = top_prediction.get('make_classification', [])

            label = obj_details.get('label', 'N/A')
            confidence = obj_details.get('confidence', 0)

            if make_details_list:
                top_make = max(make_details_list, key=lambda m: m.get('confidence', 0))
                label = top_make.get('label', label)
                confidence = top_make.get('confidence', confidence)

            table.add_row(
                img_name,
                label,
                f"{confidence:.4f}"
            )
        console.print(table)
    else:
        print("No results to save.")


if __name__ == '__main__':
    main()
