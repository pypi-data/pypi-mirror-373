import transformers
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import torch
import torch.nn as nn
from PIL import Image
import requests

class Classifier:
    def __init__(self, model_name="therealcyberlord/stanford-car-vit-patch16", cache_dir="models", image=None):  
        self.image = image
        self.extractor = AutoFeatureExtractor.from_pretrained(model_name, cache_dir=cache_dir)
        self.model = AutoModelForImageClassification.from_pretrained(model_name, cache_dir=cache_dir)
    
    def classify_car_image(self, image=None):
        img_to_classify = image if image is not None else self.image
        
        if img_to_classify is None:
            raise ValueError("No image provided for classification")
        
        inputs = self.extractor(images=img_to_classify, return_tensors='pt')  
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = nn.functional.softmax(outputs.logits, dim=-1)
        
        predicted_class_idx = predictions.argmax().item()
        confidence = predictions.max().item()
        
        if hasattr(self.model.config, 'id2label') and self.model.config.id2label:
            predicted_label = self.model.config.id2label[predicted_class_idx]
        else:
            predicted_label = f"Class: {predicted_class_idx}"
        
        return {
            'predicted_class': predicted_label,
            'confidence': confidence,
            'class_index': predicted_class_idx
        }
    
    def classify_from_file(self, file_path):
        """Classify a car image from a file path"""
        image = Image.open(file_path)
        return self.classify_car_image(image)
    
    def classify_from_url(self, url):
        """Classify a car image from a URL"""
        image = Image.open(requests.get(url, stream=True).raw)
        return self.classify_car_image(image)
    
    def get_top_k_predictions(self, image=None, k=5):
        """Get top k predictions for an image"""
        img_to_classify = image if image is not None else self.image
        
        if img_to_classify is None:
            raise ValueError("No image provided for classification")
        
        inputs = self.extractor(images=img_to_classify, return_tensors='pt')
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = nn.functional.softmax(outputs.logits, dim=-1)
        
        top_k_values, top_k_indices = torch.topk(predictions, k)
        
        results = []
        for i in range(k):
            class_idx = top_k_indices[0][i].item()
            confidence = top_k_values[0][i].item()
            
            if hasattr(self.model.config, 'id2label') and self.model.config.id2label:
                label = self.model.config.id2label[class_idx]
            else:
                label = f"Class: {class_idx}"
            
            results.append({
                'label': label,
                'confidence': confidence,
                'class_index': class_idx
            })
        
        return results


if __name__ == "__main__":
    classifier = Classifier(model_name="therealcyberlord/stanford-car-vit-patch16", cache_dir="models")
    
    try:
        image = Image.open("/Users/fnayres/pax-case/datasets/car-camera/images/images/1479502700758590752.jpg")
        result = classifier.classify_car_image(image)
        print(f"Predicted car: {result['predicted_class']}")
        print(f"Confidence: {result['confidence']:.4f}")
        
        top_predictions = classifier.get_top_k_predictions(image, k=5)
        print("\nTop 5 predictions:")
        for i, pred in enumerate(top_predictions, 1):
            print(f"{i}. {pred['label']} - {pred['confidence']:.4f}")
            
    except Exception as e:
        print(f"Error: {e}")
