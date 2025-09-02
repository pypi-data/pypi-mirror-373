from ultralytics import YOLO
import cv2 as cv
import numpy as np
from pathlib import Path
import os
import shutil
from classification.base import BaseClassifier

class ObjectClassfier(BaseClassifier):
  def __init__(self, model_version="yolov8l.pt", cache_dir="models"):
    
    cache_path = Path(cache_dir)
    cache_path.mkdir(exist_ok=True)
    
    model_path = cache_path / model_version
    
    if model_path.exists():
        print(f"Loading cached model from {model_path}")
        self.model = YOLO(str(model_path))
    else:
        print(f"Downloading model {model_version}...")
        model = YOLO(model_version)
        downloaded_path = Path(model.ckpt_path)

        print(f"Moving model to {model_path}")
        shutil.move(str(downloaded_path), str(model_path))

        self.model = YOLO(str(model_path))

    self.classes = {
      0: 'person',
      1: 'bicycle',
      2: 'car',
      7: 'truck',
    }
    self.class_ids = list(self.classes.keys())

  @property
  def name(self) -> str:
      return "object_detection"

  def process(self, image, context: dict) -> dict:
      """Process an image and return object detection results."""
      confidence = context.get('confidence', 0.5)
      output_dir = context.get('output_dir', 'runs/detect')
      results = self.detect(image, confidence=confidence, save_results=True, project=output_dir)
      detections = self.process_detection(results)
      return {'detections': detections}

  def detect(self, img, save_results=True, confidence=0.5, project='runs/detect'):
    
    results = self.model.predict(source=img, conf=confidence, classes=self.class_ids, save=save_results, save_txt=save_results, save_conf=save_results, project=project)
    return results
  
  def process_detection(self, results):
    detections = []

    for res in results:

      boxes = res.boxes

      if boxes:
        for i in range(len(boxes)):

          x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
          confidence = boxes.conf[i].cpu().numpy()
          class_id = int(boxes.cls[i].cpu().numpy())
          class_name = self.classes[class_id]

          detection = {
            'bbox': [float(x1), float(y1), float(x2), float(y2)],
            'confidence': float(confidence),
            'class_id': class_id,
            'class_name': class_name,
            'center': [(x1 + x2) / 2, (y1 + y2) / 2],
            'width': x2 - x1,
            'height': y2 - y1
          }     
          detections.append(detection)

    return detections
  

# def main():
#     """
#     Example usage of Phase 1 Object Classification
#     """
#     classifier = ObjectClassfier() 
    
#     sources = [
#         "/Users/fnayres/pax-case/images/images/images/1479502700758590752.jpg",
#     ]
    
#     for source in sources[:1]:  
#         try:
#             detections = classifier.run_detection(
#                 img=source,
#                 confidence=0.5,
#                 out_dir="results/phase1"
#             )
            
#             for i, det in enumerate(detections):
#                 print(f"\nDetection {i+1}:")
#                 print(f"  Class: {det['class_name']}")
#                 print(f"  Confidence: {det['confidence']:.3f}")
#                 print(f"  Bounding Box: {det['bbox']}")
#                 print(f"  Center: ({det['center'][0]:.1f}, {det['center'][1]:.1f})")
                
#         except Exception as e:
#             print(f"Error processing {source}: {e}")

# if __name__ == "__main__":
#     main()
