from typing import Optional
import cv2 as cv
from PIL import Image
import numpy as np
from pathlib import Path

from classification.objects.object_classifier import ObjectClassfier
from classification.makes.StanfordViT import Classifier as MakeClassifier

class VisionPipeline:
    def __init__(self, object_model_version="yolov8l.pt", make_model_name="therealcyberlord/stanford-car-vit-patch16", cache_dir="models"):
        """
        Initializes the vision pipeline by loading the object detection and car make classification models.
        """
        self.object_classifier = ObjectClassfier(model_version=object_model_version, cache_dir=cache_dir)
        self.make_classifier = MakeClassifier(model_name=make_model_name, cache_dir=cache_dir)

    def process_image(self, image_path, confidence=0.5):
        """
        Processes a single image through the full pipeline.

        Args:
            image_path (str): The path to the image file.
            confidence (float): The confidence threshold for object detection.

        Returns:
            list: A list of dictionaries, where each dictionary represents a detected vehicle
                  and its make classification.
        """
        img = cv.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        detections = self.object_classifier.run_detection(img, confidence=confidence)

        results = []

        for det in detections:
            if det['class_name'] not in ['car', 'truck']:
                x1, y1, x2, y2 = [int(coord) for coord in det['bbox']]
                label_img_bgr = img[y1:y2, x1:x2]
                pil_image = Image.fromarray(label_img_bgr)
                results.append({'object_detection': det})
            else:
                x1, y1, x2, y2 = [int(coord) for coord in det['bbox']]
                vehicle_img_bgr = img[y1:y2, x1:x2]
                # Convert from BGR (OpenCV) to RGB (PIL)
                vehicle_img_rgb = cv.cvtColor(vehicle_img_bgr, cv.COLOR_BGR2RGB)
                pil_image = Image.fromarray(vehicle_img_rgb)

                make_predictions = self.make_classifier.get_top_k_predictions(pil_image, k=5)

                results.append({
                    'object_detection': det,
                    'make_classification': make_predictions
                })

        return results

# if __name__ == '__main__':
#     pipeline = VisionPipeline()
    
#     example_image = "/Users/fnayres/pax-case/datasets/car-camera/images/images/1479502700758590752.jpg"

#     try:
#         output = pipeline.process_image(example_image)
        
#         print(f"Processing results for: {example_image}")
#         for i, result in enumerate(output):
#             print(f"\n--- Vehicle {i+1} ---")
#             obj_det = result['object_detection']
#             print(f"  Detected: {obj_det['class_name']} with confidence {obj_det['confidence']:.2f}")
#             print(f"  Bounding Box: {obj_det['bbox']}")
            
#             print("  Top 5 Make Predictions:")
#             for pred in result['make_classification']:
#                 print(f"    - {pred['label']}: {pred['confidence']:.3f}")

#     except Exception as e:
#         print(f"An error occurred: {e}")
