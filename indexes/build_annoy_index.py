import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from annoy import AnnoyIndex
from torch.utils.data import Dataset, DataLoader

class ImageIndexDataset(Dataset):
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
        return image

class ImageIndexer:
    def __init__(self, images_folder, index_file):
        self.images_folder = images_folder
        self.index_file = index_file
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model()
        self.transform = self.create_transform()
        self.annoy_index = AnnoyIndex(512, 'angular')

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

    def index_images(self):
        dataset = ImageIndexDataset(self.images_folder, transform=self.transform)
        dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

        for i, input_tensor in enumerate(dataloader):
            if input_tensor is None:
                print(f'Skipped image at index {i} due to loading error.')
                continue

            input_tensor = input_tensor.to(self.device)

            with torch.no_grad():
                output_tensor = self.model(input_tensor)

            vector = output_tensor[0].cpu().numpy()
            self.annoy_index.add_item(i, vector)

            if i % 100 == 0:
                print(f'Processed {i} images.')

        self.annoy_index.build(10)
        self.annoy_index.save(self.index_file)

if __name__ == '__main__':
    indexer = ImageIndexer('PetImages/Dog', 'indexes/dog_index.ann')
    indexer.index_images()



