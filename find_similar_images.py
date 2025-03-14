import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageDraw
from annoy import AnnoyIndex
from torch.utils.data import Dataset, DataLoader
import json

from fuzzywuzzy import process

class ImageDataset(Dataset):
    def __init__(self, images_folder, transform=None):
        self.images_folder = images_folder
        self.images = os.listdir(images_folder)
        self.transform = transform
        self.valid_indices = []

        for idx in range(len(self.images)):
            image_path = os.path.join(self.images_folder, self.images[idx])
            try:
                Image.open(image_path).convert('RGB')
                self.valid_indices.append(idx)
            except Exception as e:
                print(f'Error opening {image_path}: {e}')

    def __len__(self):
        return len(self.valid_indices)

    def __getitem__(self, idx):
        
        actual_idx = self.valid_indices[idx]
        image_path = os.path.join(self.images_folder, self.images[actual_idx])

        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)
        return image, self.images[actual_idx]

class ImageSearcher:
    def __init__(self, images_folder, index_file):
        self.images_folder = images_folder
        self.index_file = index_file
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model()
        self.transform = self.create_transform()
        self.annoy_index = AnnoyIndex(512, 'angular')
        self.annoy_index.load(self.index_file)

    def load_model(self):
        weights = models.ResNet18_Weights.IMAGENET1K_V1
        model = models.resnet18(weights=weights)
        model = model.to(self.device)
        model.fc = nn.Identity()
        model.eval()
        return model

    def create_transform(self):
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def search_images(self):
        dataset = ImageDataset(self.images_folder, transform=self.transform)
        dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

        image_grid = Image.new('RGB', (1000, 1000))

        for i, (input_tensor, image_name) in enumerate(dataloader):
            input_tensor = input_tensor.to(self.device)

            with torch.no_grad():
                output_tensor = self.model(input_tensor)

            vector = output_tensor[0].cpu().numpy()
            nns = self.annoy_index.get_nns_by_vector(vector, 24)

            try:
                image = Image.open(os.path.join(self.images_folder, image_name[0])).convert('RGB')
            except Exception as e:
                print(f'Error opening {image_name[0]}: {e}')
                continue  # Skip this image if it cannot be opened

            image = image.resize((200, 200))
            image_draw = ImageDraw.Draw(image)
            image_draw.rectangle([(0, 0), (199, 199)], outline='red', width=8)
            image_grid.paste(image, ((0, 0)))

            for j in range(24):
                try:
                    search_image = Image.open(os.path.join(self.images_folder, dataset.images[nns[j]])).convert('RGB')
                except Exception as e:
                    print(f'Error opening {dataset.images[nns[j]]}: {e}')
                    continue  # Skip this image if it cannot be opened

                search_image = search_image.resize((200, 200))
                image_grid.paste(search_image, ((200 * ((j + 1) % 5), 200 * ((j + 1) // 5))))

            image_grid.save(f'ImageDumpDog/image_{i}.png')

    
    def search_by_breed(self, breed_name):
        with open('breed_predictions.json', 'r') as f:
            breed_predictions = json.load(f)

        normalized_predictions = {img: breed.lower() for img, breed in breed_predictions.items()}
        matching_images = [img for img, breed in normalized_predictions.items() if breed_name.lower() in breed]

        if not matching_images:
            all_breeds = set(normalized_predictions.values())
            suggested_breed, score = process.extractOne(breed_name.lower(), all_breeds)

            if score > 80:
                print(f'No exact matches found for breed: {breed_name}. Did you mean: {suggested_breed}?')
            else:
                print(f'No exact matches found for breed: {breed_name}')
            return []

        similar_images = matching_images[:5]
        image_grid = Image.new('RGB', (1000, 200))

        for j, img in enumerate(similar_images):
            try:
                image_path = os.path.join(self.images_folder, img)
                search_image = Image.open(image_path).convert('RGB')
                search_image = search_image.resize((200, 200))
                image_grid.paste(search_image, ((200*j, 0)))
            except Exception as e:
                print(f'Error opening {img}: {e}')
                continue  # Skip this image if it cannot be opened

        image_grid.save(f'ImageDumpDogSimilarPredictions/{breed_name}_similar_images.png')
        print(f'Saved similar images for breed: {breed_name}')

        return similar_images
        

if __name__ == '__main__':
    searcher = ImageSearcher('PetImages/Dog', 'dog_index.ann')
    breed_to_search = input('Enter the breed you want to search for: ')
    searcher.search_by_breed(breed_to_search)