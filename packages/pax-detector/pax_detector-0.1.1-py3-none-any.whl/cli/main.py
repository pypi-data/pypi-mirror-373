import json
import argparse
from pathlib import Path
import numpy as np

from utils.utils import NumpyEncoder, parse_config_yaml
from pipeline.vision_pipeline import VisionPipeline

def main():
    parser = argparse.ArgumentParser(description="Detect objects and classify car makes in an image.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image_path', type=str, help='Path to a single image file.')
    group.add_argument('--images_dir', type=str, help='Path to a directory of image files.')
    group.add_argument('--config', type=str, help='Path to a config.yml file')
    parser.add_argument('--confidence', type=float, default=0.5, help='Confidence threshold for object detection.')

    args = parser.parse_args()
    results = {}

    if args.config:
        config = parse_config_yaml(args.config)
        try:
            pipeline = VisionPipeline()
            confidence = config.get('confidence', 0.5)
            image_path = config.get('image_path')
            images_dir = config.get('images_dir')

            if image_path:
                if not Path(image_path).is_file():
                    print(f"Error: Image file not found at {image_path}")
                    return
                results = pipeline.process_image(image_path, confidence)
            elif images_dir:
                if not Path(images_dir).is_dir():
                    print(f"Error: Directory not found at {images_dir}")
                    return
                results = pipeline.process_multiple_images(images_dir, confidence)
        except Exception as e:
            print(f"An error occurred during processing: {e}")
            return
    else:
        try:
            pipeline = VisionPipeline()
            if args.image_path:
                if not Path(args.image_path).is_file():
                    print(f"Error: Image file not found at {args.image_path}")
                    return
                results = pipeline.process_image(args.image_path, args.confidence)
            elif args.images_dir:
                if not Path(args.images_dir).is_dir():
                    print(f"Error: Directory not found at {args.images_dir}")
                    return
                results = pipeline.process_multiple_images(args.images_dir, args.confidence)
        except Exception as e:
            print(f"An error occurred during processing: {e}")
            return

    print(json.dumps(results, cls=NumpyEncoder, indent=4))


if __name__ == '__main__':
    main()
