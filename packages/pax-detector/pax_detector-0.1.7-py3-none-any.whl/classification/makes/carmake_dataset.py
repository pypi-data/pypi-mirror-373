import os
import torch
from torch.utils.data import Dataset
from PIL import Image
from typing import Optional, Dict, List, Tuple
from transformers import AutoImageProcessor
import torchvision.transforms as transforms

class CarMakeDataset(Dataset):
    def __init__(self, root_dir: str, split: str = 'train', processor: Optional[AutoImageProcessor] = None, is_training: bool = True):
        """
        Car Make Dataset for folder-based structure
        
        Args:
            root_dir: Path to the dataset root directory
            split: 'train', 'test', or 'valid'
            processor: SigLIP AutoImageProcessor for preprocessing
            is_training: Whether to apply training augmentations
        """
        self.root_dir = root_dir
        self.split = split
        self.processor = processor
        self.is_training = is_training
        
        self.split_dir = os.path.join(root_dir, split)
        
        self.classes = sorted([d for d in os.listdir(self.split_dir) 
                              if os.path.isdir(os.path.join(self.split_dir, d))])
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.classes)}
        self.num_classes = len(self.classes)
        
        self.samples = []
        self._load_samples()
    
        self.augmentations = None
    
    def _load_samples(self):
        """Load all image paths and their corresponding labels"""
        for class_name in self.classes:
            class_dir = os.path.join(self.split_dir, class_name)
            class_idx = self.class_to_idx[class_name]
            
            for filename in os.listdir(class_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')):
                    img_path = os.path.join(class_dir, filename)
                    self.samples.append((img_path, class_idx))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a black image as fallback
            image = Image.new('RGB', (224, 224), color=(0, 0, 0))
        
        if self.augmentations is not None:
            image = self.augmentations(image)
        
        if self.processor is not None:
            processed = self.processor(images=image, return_tensors="pt")
            pixel_values = processed['pixel_values'].squeeze(0)  
        else:
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            pixel_values = transform(image)
        
        return pixel_values, torch.tensor(label, dtype=torch.long)
    
    def get_class_names(self) -> List[str]:
        """Return list of class names"""
        return self.classes
    
    def get_class_to_idx(self) -> Dict[str, int]:
        """Return class name to index mapping"""
        return self.class_to_idx

    def get_class_names(self):
        return self.classes
