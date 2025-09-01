from ultralytics import YOLO
import cv2 as cv
import numpy as np
from pathlib import Path
import os
import shutil

class ObjectClassfier:
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

  def detect(self, img, save_results=True, confidence=0.5):
    
    results = self.model.predict(source=img, conf=confidence, classes=self.class_ids, save=save_results, save_txt=True, save_conf=True)
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
  
  def run_detection(self, img, out_dir="results/phase1", confidence=0.5):

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    results = self.detect(img, confidence=confidence)
    detections = self.process_detection(results)

    class_counts = {}
    for det in detections:
      class_name = det['class_name']
      class_counts[class_name] = class_counts.get(class_name, 0) + 1
      
    for class_name, count, in class_counts.items():
      print(f"{class_name}: {count}")

    return detections
  
def main():
    """
    Example usage of Phase 1 Object Classification
    """
    # Initialize classifier
    classifier = ObjectClassfier()  # Using nano model for speed
    
    sources = [
        "/Users/fnayres/pax-case/images/images/images/1479502700758590752.jpg",
    ]
    
    for source in sources[:1]:  # Process first source only in example
        try:
            detections = classifier.run_detection(
                img=source,
                confidence=0.5,
                out_dir="results/phase1"
            )
            
            # Optional: Print detailed results
            for i, det in enumerate(detections):
                print(f"\nDetection {i+1}:")
                print(f"  Class: {det['class_name']}")
                print(f"  Confidence: {det['confidence']:.3f}")
                print(f"  Bounding Box: {det['bbox']}")
                print(f"  Center: ({det['center'][0]:.1f}, {det['center'][1]:.1f})")
                
        except Exception as e:
            print(f"Error processing {source}: {e}")

if __name__ == "__main__":
    main()
