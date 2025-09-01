#!/usr/bin/python
# -*- coding: utf-8 -*-
import torch
import torchvision
import torchvision.transforms as transforms
import cv2
import numpy as np
from typing import List, Tuple
from PIL import Image
import os

# class ModelLoader:
#     """Handles loading and managing the pretrained model"""
    
#     def __init__(self, model_name: str = 'resnet50'):
#         self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#         self.model = self._load_pretrained_model(model_name)
        
#     def _load_pretrained_model(self, model_name: str) -> torch.nn.Module:
#         """Load pretrained model from torchvision.models"""
#         model = getattr(torchvision.models, model_name)(pretrained=True)
#         return model.eval().to(self.device)

class ModelLoader:
    """Handles loading and managing the pretrained model"""

    def __init__(self, model_name: str = 'resnet50'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_dir = "models" 
        os.makedirs(self.model_dir, exist_ok=True) 
        self.model = self._load_pretrained_model(model_name)

    def _load_pretrained_model(self, model_name: str) -> torch.nn.Module:
        """Load pretrained model from torchvision.models. If not found locally, download and save it."""
        model_path = os.path.join(self.model_dir, f"{model_name}.pth")  

        try:
            model = getattr(torchvision.models, model_name)(pretrained=False)  
            model.load_state_dict(torch.load(model_path))  
            print(f"Loaded {model_name} from local directory: {model_path}")
        except FileNotFoundError:
            print(f"Model {model_name} not found locally. Downloading...")
            model = getattr(torchvision.models, model_name)(pretrained=True)  
            torch.save(model.state_dict(), model_path)  
            print(f"Downloaded and saved {model_name} to: {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load or download the model: {e}")

        return model.eval().to(self.device)
    

class ImageProcessor:
    """Handles image preprocessing and transformations"""
    
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Load and preprocess image for model input"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found at {image_path}")
                
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Unable to read image at {image_path}")
                
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image for torchvision transforms
            image = Image.fromarray(image)
            return self.transform(image).unsqueeze(0)
        except Exception as e:
            print(f"Error processing image: {e}")
            raise

class Predictor:
    """Handles model predictions and visualization"""
    
    def __init__(self, model_loader: ModelLoader, labels_path: str = 'imagenet_classes.txt'):
        self.model = model_loader.model
        self.device = model_loader.device
        self.labels = self._load_labels(labels_path)
        
    def _load_labels(self, labels_path: str) -> List[str]:
        """Load class labels from file"""
        try:
            with open(labels_path) as f:
                labels = [line.strip() for line in f.readlines()]
                if len(labels) != 1000:
                    raise ValueError(f"Expected 1000 ImageNet classes, got {len(labels)}")
                return labels
        except Exception as e:
            print(f"Error loading labels: {e}")
            raise
            
    def predict(self, input_tensor: torch.Tensor) -> Tuple[int, str]:
        """Run model prediction on input tensor"""
        with torch.no_grad():
            input_tensor = input_tensor.to(self.device)
            pred = self.model(input_tensor)
            pred_index = torch.argmax(pred, 1).cpu().detach().numpy()[0]
            
            if pred_index >= len(self.labels):
                raise ValueError(f"Prediction index {pred_index} out of range for {len(self.labels)} classes")
                
            return pred_index, self.labels[pred_index]
            
    def visualize_prediction(self, image_path: str, class_name: str):
        """Display image with predicted class label"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise FileNotFoundError(f"Image not found at {image_path}")
                
            cv2.putText(image, class_name, (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            # cv2.imshow("Prediction", image)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            output_path = f"output_image_{class_name}.jpg"  # 替换为你想保存的路径
            cv2.imwrite(output_path, image)
            print(f"Image saved to {output_path}")
        except Exception as e:
            print(f"Error visualizing prediction: {e}")
            raise

def main():
    try:
        # Initialize components
        model_loader = ModelLoader()
        image_processor = ImageProcessor()
        predictor = Predictor(model_loader)
        
        # Process image and make prediction
        image_path = "./space_shuttle.jpg"
        input_tensor = image_processor.preprocess_image(image_path)
        pred_index, class_name = predictor.predict(input_tensor)
        
        # Display results
        print(f"Predicted class index: {pred_index}")
        print(f"Predicted class name: {class_name}")
        predictor.visualize_prediction(image_path, class_name)
        
    except Exception as e:
        print(f"Error in main execution: {e}")

# if __name__ == "__main__":
#     main()
