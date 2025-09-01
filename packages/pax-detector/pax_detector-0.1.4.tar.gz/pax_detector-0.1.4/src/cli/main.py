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
    parser.add_argument('--output_dir', type=str, default='runs/detections', help='Directory to save the output images.')
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
                results = pipeline.process_image(image_path, confidence, args.output_dir)
                
            elif images_dir:
                if not Path(images_dir).is_dir():
                    print(f"Error: Directory not found at {images_dir}")
                    return
                results = pipeline.process_multiple_images(images_dir, confidence, args.output_dir)
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
                results = pipeline.process_image(args.image_path, args.confidence, args.output_dir)
            elif args.images_dir:
                if not Path(args.images_dir).is_dir():
                    print(f"Error: Directory not found at {args.images_dir}")
                    return
                results = pipeline.process_multiple_images(args.images_dir, args.confidence, args.output_dir)
        except Exception as e:
            print(f"An error occurred during processing: {e}")
            return

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if results:
        if args.image_path:
            json_filename = Path(args.image_path).stem + '.json'
        elif args.config and 'image_path' in config and config['image_path']:
            json_filename = Path(config['image_path']).stem + '.json'
        else:
            json_filename = 'results.json'

        json_output_path = output_path / json_filename

        with open(json_output_path, 'w') as f:
            json.dump(results, f, cls=NumpyEncoder, indent=4)

        print(f"Results saved to {json_output_path}")
    else:
        print("No results to save.")


if __name__ == '__main__':
    main()
