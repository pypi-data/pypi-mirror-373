from typing import Optional
import cv2 as cv
from PIL import Image
import os
import glob
from tqdm import tqdm
import json
import numpy as np

from classification.objects.object_classifier import ObjectClassfier
from classification.makes.SiglipClassifier import MakeClassifier

from utils.utils import NumpyEncoder


class VisionPipeline:
    def __init__(self, object_model_version="yolov8l.pt", cache_dir="models"):
        """
        Initializes the vision pipeline by loading the object detection and car make classification models.
        """
        self.object_classifier = ObjectClassfier(model_version=object_model_version, cache_dir=cache_dir)
        self.make_classifier = MakeClassifier(cache_dir=cache_dir)

    def process_image(self, image_path, confidence=0.5, output_dir='runs/detect'):
        """
        Processes a single image through the full pipeline.

        Args:
            image_path (str): The path to the image file.
            confidence (float): The confidence threshold for object detection.
            output_dir (str): The directory to save the output images.

        Returns:
            list: A list of dictionaries, where each dictionary represents a detected vehicle
                  and its make classification.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f'Directory not found at {image_path}')
        
        img = cv.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        object_results = self.object_classifier.process(img, context={'confidence': confidence, 'output_dir': output_dir})
        detections = object_results.get('detections', [])

        results = []

        for det in detections:
            if det['class_name'] not in ['car', 'truck']:
                results.append({'object_detection': det})
                continue

            x1, y1, x2, y2 = [int(coord) for coord in det['bbox']]
            vehicle_img_bgr = img[y1:y2, x1:x2]
            if vehicle_img_bgr.size == 0:
                continue
            
            vehicle_img_rgb = cv.cvtColor(vehicle_img_bgr, cv.COLOR_BGR2RGB)
            pil_image = Image.fromarray(vehicle_img_rgb)

            make_results = self.make_classifier.process(pil_image, context={'k': 5})
            
            results.append({
                'object_detection': det,
                **make_results
            })

        return results

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
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.iglob(os.path.join(images_dir, ext), recursive=False))

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
