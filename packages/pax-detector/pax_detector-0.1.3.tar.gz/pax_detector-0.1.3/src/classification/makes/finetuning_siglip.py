import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import RandomAdjustSharpness, RandomRotation

import numpy as np

import torchmetrics

import pytorch_lightning as pl
from pytorch_lightning.trainer import Trainer
from pytorch_lightning.callbacks import  EarlyStopping, ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger

from transformers import (
    AutoImageProcessor, 
    SiglipForImageClassification
)
from StanfordDataset import StanfordCarsDataset

class ImageClassificationModule(pl.LightningModule):
  def __init__(self, model_name: str, num_classes: int, learning_rate: float = 1e-4, weight_decay: float = 0.01):
    super().__init__()
    self.save_hyperparameters()

    self.model = SiglipForImageClassification.from_pretrained(model_name, num_labels=num_classes, ignore_mismatched_sizes=True)  

    self.train_accuracy = torchmetrics.Accuracy(task="multiclass", num_classes=num_classes)
    self.val_accuracy = torchmetrics.Accuracy(task="multiclass", num_classes=num_classes)
    self.test_accuracy = torchmetrics.Accuracy(task="multiclass", num_classes=num_classes)
    
    self.criterion = nn.CrossEntropyLoss()

  def forward(self, pixel_values):
    outputs = self.model(pixel_values=pixel_values)
    return outputs.logits
  
  def training_step(self, batch, batch_idx):
    images, labels = batch
    logits = self.forward(images)
    loss = self.criterion(logits, labels)

    preds = torch.argmax(logits, dim=1)
    self.train_accuracy(preds, labels)
    
    self.log('train_loss', loss, on_step=True, on_epoch=True, prog_bar=True)
    self.log('train_accuracy', self.train_accuracy, on_step=False, on_epoch=True, prog_bar=True)

    return loss

  def validation_step(self, batch, batch_idx):
    images, labels = batch
    logits = self.forward(images)
    loss = self.criterion(logits, labels)

    preds = torch.argmax(logits, dim=1)
    self.val_accuracy(preds, labels)
    
    self.log('val_loss', loss, on_step=True, on_epoch=True, prog_bar=True)
    self.log('val_accuracy', self.val_accuracy, on_step=False, on_epoch=True, prog_bar=True)

    return loss
  
  def test_step(self, batch, batch_idx):
    images, labels = batch
    logits = self.forward(images)
    loss = self.criterion(logits, labels)

    preds = torch.argmax(logits, dim=1)
    self.test_accuracy(preds, labels)
    
    self.log('test_loss', loss, on_step=True, on_epoch=True, prog_bar=True)
    self.log('test_accuracy', self.test_accuracy, on_step=False, on_epoch=True, prog_bar=True)

    return loss
  
  def configure_optimizers(self):
    optimizer = torch.optim.AdamW(self.parameters(), lr=self.hparams.learning_rate, weight_decay=self.hparams.weight_decay)

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=self.trainer.max_epochs, eta_min=1e-6)

    return {
      'optimizer': optimizer,
      'lr_scheduler': {
        'scheduler': scheduler,
        'interval': 'epoch',
        'frequency': 1
      }
    }
  

class StanfordCarsDataModule(pl.LightningDataModule):
  def __init__(self, batch_size: int = 32, num_workers: int = 4):
    super().__init__()
    self.batch_size = batch_size
    self.num_workers = num_workers

    model_str = 'google/siglip-base-patch16-224'
    self.processor = AutoImageProcessor.from_pretrained(model_str)
    

  def setup(self, stage=None):
        if stage == "fit" or stage is None:
            stanford_dataset = StanfordCarsDataset()
            train_hf, test_hf = stanford_dataset.load_data()  # This returns (train, test) tuple
            
            tr_loader = StanfordCarsDataset(processor=self.processor, is_training=True)
            val_loader = StanfordCarsDataset(processor=self.processor, is_training=False)
            
            self.train_dataset = tr_loader.to_torch_dataset(train_hf)
            self.val_dataset = val_loader.to_torch_dataset(test_hf)  # Using test as validation
        
        if stage == "test" or stage is None:
            stanford_dataset = StanfordCarsDataset()
            _, test_hf = stanford_dataset.load_data()
            test_loader = StanfordCarsDataset(processor=self.processor, is_training=False)
            self.test_dataset = test_loader.to_torch_dataset(test_hf)
  
  def train_dataloader(self):
      return DataLoader(
          self.train_dataset,
          batch_size=self.batch_size,
          shuffle=True,
          num_workers=self.num_workers,
          pin_memory=True
      )
  
  def val_dataloader(self):
      return DataLoader(
          self.val_dataset,
          batch_size=self.batch_size,
          shuffle=False,
          num_workers=self.num_workers,
          pin_memory=True
      )
  
  def test_dataloader(self):
      return DataLoader(
          self.test_dataset,
          batch_size=self.batch_size,
          shuffle=False,
          num_workers=self.num_workers,
          pin_memory=True
      )


if __name__ == '__main__':
  
  model_str = 'google/siglip-base-patch16-224'
  


  num_classes = 196  # Stanford Cars has 196 classes
  batch_size = 32 
  max_epochs = 10
  learning_rate = 1e-4
  weight_decay = 0.01


  data_module = StanfordCarsDataModule(batch_size=batch_size, num_workers=4)
  model = ImageClassificationModule(model_name=model_str, num_classes=num_classes, learning_rate=learning_rate, weight_decay=weight_decay)

  early_stopping = EarlyStopping(monitor='val_accuracy', mode='max', patience=5, verbose=True, min_delta=0.0)

  checkpoint_call = ModelCheckpoint(monitor='val_accuracy', mode='max', save_top_k=1, filename='best-checkpoint-{epoch:02d}-{val_accuracy:.3f}', verbose=True)

  logger = TensorBoardLogger('lightning_logs_20', name='stanf-cars')
  
  trainer = Trainer(
    max_epochs=max_epochs,
    callbacks=[early_stopping, checkpoint_call],
    logger=logger,
    accelerator='auto',
    devices='auto',
    precision="16-mixed",
    log_every_n_steps=50,
    val_check_interval=1.0,
    enable_progress_bar=True,
    enable_model_summary=True,
  )
  
  print("Starting training...")
  trainer.fit(model, data_module)
  
  print('Testing the model...')
  trainer.test(model, data_module, ckpt_path='best')

  print('Saving the model...')
  trainer.save_checkpoint('final_model.ckpt')
  
  print("Training completed!")
  print(f"Best model saved at: {checkpoint_call.best_model_path}")
  print(f"Best validation accuracy: {checkpoint_call.best_model_score:.4f}")
