import json
import argparse
from pathlib import Path
import numpy as np

from pipeline.vision_pipeline import VisionPipeline

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def main():
    parser = argparse.ArgumentParser(description="Detect objects and classify car makes in an image.")
    parser.add_argument('--image_path', type=str, required=True, help='Path to the image file.')
    parser.add_argument('--confidence', type=float, default=0.5, help='Confidence threshold for object detection.')

    args = parser.parse_args()

    if not Path(args.image_path).is_file():
        print(f"Error: Image file not found at {args.image_path}")
        return

    pipeline = VisionPipeline()

    results = pipeline.process_image(args.image_path, args.confidence)

    print(json.dumps(results, cls=NumpyEncoder, indent=4))

if __name__ == '__main__':
    main()
