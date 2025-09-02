import torch
import torch.nn as nn
from PIL import Image
from transformers import AutoImageProcessor
import json
from huggingface_hub import hf_hub_download

from classification.base import BaseClassifier
from classification.makes.finetuning_siglip import ImageClassificationModule
from .carmake_dataset import CarMakeDataset

class MakeClassifier(BaseClassifier):
    def __init__(self, model_name_for_processor='google/siglip-base-patch16-224', cache_dir="models"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        repo_id = "fnayres/car-make-recognition-google-siglip-base-patch16-224"
        model_filename = "sig_makes.ckpt"
        label_map_filename = "label_map.json"

        model_path = hf_hub_download(repo_id=repo_id, filename=model_filename, cache_dir=cache_dir)
        label_map_path = hf_hub_download(repo_id=repo_id, filename=label_map_filename, cache_dir=cache_dir)

        with open(label_map_path, 'r') as f:
            label_map = json.load(f)
        id2label = {int(k): v for k, v in label_map['id2label'].items()}
        label2id = label_map['label2id']

        self.model = ImageClassificationModule.load_from_checkpoint(
            model_path,
            id2label=id2label,
            label2id=label2id
        ).to(self.device)
        self.model.eval()
        self.processor = AutoImageProcessor.from_pretrained(model_name_for_processor, cache_dir=cache_dir)
        self.id2label = self.model.model.config.id2label

    @property
    def name(self) -> str:
        return "car_make_classification_siglip"

    def process(self, image: Image.Image, context: dict) -> dict:
        """Get top k predictions for an image."""
        k = context.get('k', 5)

        if image is None:
            raise ValueError("No image provided for classification")

        inputs = self.processor(images=image, return_tensors='pt').to(self.device)

        with torch.no_grad():
            logits = self.model(inputs['pixel_values'])
            predictions = nn.functional.softmax(logits, dim=-1)

        top_k_values, top_k_indices = torch.topk(predictions, k)

        results = []
        for i in range(k):
            class_idx = top_k_indices[0][i].item()
            confidence = top_k_values[0][i].item()

            if self.id2label:
                label = self.id2label[class_idx]
            else:
                label = f"Class: {class_idx}"

            results.append({
                'label': label,
                'confidence': confidence,
                'class_index': class_idx
            })

        return {'make_classification': results}
