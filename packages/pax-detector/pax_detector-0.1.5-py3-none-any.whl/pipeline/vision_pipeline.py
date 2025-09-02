import cv2 as cv
from PIL import Image
import os
import glob
from tqdm import tqdm
import json
import importlib

from utils.utils import NumpyEncoder, parse_config_yaml


def _load_classifier(class_path: str):
    try:
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import classifier '{class_path}': {e}")


class VisionPipeline:
    def __init__(self, config_path: str, cache_dir="models"):
        self.config = parse_config_yaml(config_path)

        self.pipeline_steps = self.config.get('pipeline', [])
        self.classifiers = {}
        for step in self.pipeline_steps:
            class_path = step['class']
            params = step.get('params', {})
            params['cache_dir'] = cache_dir
            classifier_class = _load_classifier(class_path)
            self.classifiers[step['name']] = classifier_class(**params)

    def process_image(self, image_path: str, confidence: float = 0.5, output_dir: str = 'runs/detect'):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f'Image not found at {image_path}')
        
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image from {image_path}")

        context = {}
        final_results = []

        initial_step = self.pipeline_steps[0]
        classifier = self.classifiers[initial_step['name']]
        step_context = {'confidence': confidence, 'output_dir': output_dir}
        initial_results = classifier.process(img, context=step_context)
        context[initial_step['name']] = initial_results

        detections = initial_results.get('detections', [])
        if not detections:
            return []

        for det in detections:
            detection_result = {initial_step['name']: det}
            
            for step in self.pipeline_steps[1:]:
                condition = step.get('condition')
                if condition and not eval(condition, {'detection': det}):
                    continue

                x1, y1, x2, y2 = [int(coord) for coord in det['bbox']]
                cropped_img_bgr = img[y1:y2, x1:x2]
                if cropped_img_bgr.size == 0:
                    continue
                
                cropped_img_rgb = cv.cvtColor(cropped_img_bgr, cv.COLOR_BGR2RGB)
                pil_image = Image.fromarray(cropped_img_rgb)

                classifier = self.classifiers[step['name']]
                step_context = step.get('params', {})
                step_result = classifier.process(pil_image, context=step_context)
                detection_result.update(step_result)

            final_results.append(detection_result)

        return final_results

    def process_multiple_images(self, images_dir: str, confidence: float = 0.5, output_dir: str = 'runs/detect'):
        """
        Processes a sequence of images through the full pipeline.

        Args:
            images_dir (str): The path to the image dir.
            confidence (float): The confidence threshold for object detection.
            output_dir (str): The directory to save the output images and JSON files.

        Returns:
            dict: A dictionary where each key is the filename of an image and the value is a list of dictionaries,
                  where each dictionary represents a detected vehicle and its make classification.
        """
        if not os.path.isdir(images_dir):
            raise FileNotFoundError(f'Directory not found at {images_dir}')

        os.makedirs(output_dir, exist_ok=True)

        image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(images_dir, ext)))

        all_results = {}
        for image_path in tqdm(image_files, desc="Processing Images"):
            filename = os.path.basename(image_path)
            try:
                result = self.process_image(image_path, confidence, output_dir)
                all_results[filename] = result
                if output_dir:
                    output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
                    with open(output_path, 'w') as f:
                        json.dump(result, f, cls=NumpyEncoder, indent=4)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                all_results[filename] = []
        
        print(f"Completed processing {len(image_files)} images")
        return all_results
