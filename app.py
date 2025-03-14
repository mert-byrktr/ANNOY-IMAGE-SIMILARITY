from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from train_breed_model import BreedPredictor
from find_similar_images import ImageSearcher
import os
from PIL import Image
import json
import torch
from torchvision import models
import uvicorn
import base64
from io import BytesIO

app = FastAPI()

predictor = BreedPredictor()
images_folder = 'PetImages/Dog'
searcher = ImageSearcher(images_folder, 'dog_index.ann')
weights = models.ResNet18_Weights.IMAGENET1K_V1

breed_names = weights.meta["categories"]


@app.get("/predict_breed")
async def predict_breed(image_path: str):
    try:
        image = Image.open(image_path).convert('RGB')
        breed_index = predictor.predict_breed(image)
        breed_name = breed_names[breed_index]
        return JSONResponse(content={"breed": breed_name})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")



@app.get("/search")
async def search_by_breed(breed: str):
    if not breed:
        raise HTTPException(status_code=400, detail="Breed name is required")

    similar_images = searcher.search_by_breed(breed)
    grid_path = f'ImageDumpDogSimilarPredictions/{breed}_similar_images.png'
    if not similar_images:
        raise HTTPException(status_code=404, detail=f"No similar images found for breed: {breed}")

    
    image_data = []
    for img in similar_images:
        image_path = os.path.join(images_folder, img)
        try:
            with Image.open(image_path) as image:
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                image_data.append({"image_name": img, "image": img_str})
        except Exception as e:
            print(f'Error processing image {img}: {e}')
            continue

    return FileResponse(grid_path, media_type="image/png")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
