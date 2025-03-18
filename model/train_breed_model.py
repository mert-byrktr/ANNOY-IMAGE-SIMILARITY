import os
import torch
from torchvision import models, transforms
from PIL import Image
import json

class BreedPredictor:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model()
        self.transform = self.create_transform()

    def load_model(self):
        weights = models.ResNet18_Weights.IMAGENET1K_V1
        model = models.resnet18(weights=weights)
        model = model.to(self.device)
        model.eval() 
        return model

    def create_transform(self):
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def predict_breed(self, image):
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.model(image_tensor)
            _, predicted = torch.max(output, 1)
        return predicted.item()  # Return the predicted class index

if __name__ == "__main__":
    # Example usage
    predictor = BreedPredictor()
    images_folder = 'PetImages/Dog'  # Update with the path to the image
    predictions = {}
    weights = models.ResNet18_Weights.IMAGENET1K_V1
    breed_names = weights.meta["categories"]

    for image_name in os.listdir(images_folder):
        image_path = os.path.join(images_folder, image_name)
        try:
            image = Image.open(image_path).convert('RGB')
            breed_index = predictor.predict_breed(image)
            breed_name = breed_names[breed_index]
            predictions[image_name] = breed_name
            print(f'Predicted breed for {image_name}: {breed_name}')
        except Exception as e:
            print(f'Error processing {image_name}: {e}')

    with open('model/breed_predictions.json', 'w') as f:
        json.dump(predictions, f)
