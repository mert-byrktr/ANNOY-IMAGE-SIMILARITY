# tests/test_api.py
import os
import sys
import base64
from io import BytesIO
from PIL import Image
import pytest
from fastapi.testclient import TestClient

# Ensure the project root is on sys.path so that we can import the app module.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as app_module
from app import app

client = TestClient(app)

# --- Dummy Helpers for Monkeypatching ---

def dummy_image_open(path):
    """
    Instead of opening a file, return a dummy image.
    """
    return Image.new("RGB", (100, 100))

def dummy_file_response(path, **kwargs):
    """
    Instead of returning a real FileResponse, return a dummy response.
    """
    from fastapi.responses import Response
    return Response(content="dummy file content", media_type="image/png", status_code=200)

class DummySearcher:
    """
    A dummy searcher that returns a predefined list for search_by_breed.
    """
    def __init__(self, results):
        self.results = results

    def search_by_breed(self, breed):
        return self.results

# --- Tests for /predict_breed ---

def test_predict_breed_success(monkeypatch):
    # Patch Image.open in the app module to use our dummy function.
    monkeypatch.setattr(app_module.Image, "open", dummy_image_open)
    # Patch the predictor’s method to always return 0.
    monkeypatch.setattr(app_module.predictor, "predict_breed", lambda image: 0)
    # Override the global breed_names list with a controlled list.
    monkeypatch.setattr(app_module, "breed_names", ["Labrador", "Poodle", "Bulldog"])

    response = client.get("/predict_breed", params={"image_path": "dummy.jpg"})
    assert response.status_code == 200
    # Since predictor returns 0, we expect the first breed ("Labrador").
    assert response.json() == {"breed": "Labrador"}

def test_predict_breed_error(monkeypatch):
    # Define a function that raises an error when attempting to open an image.
    def raise_error(path):
        raise Exception("File not found")
    monkeypatch.setattr(app_module.Image, "open", raise_error)

    response = client.get("/predict_breed", params={"image_path": "nonexistent.jpg"})
    assert response.status_code == 400
    assert "Error processing image" in response.json()["detail"]

# --- Tests for /search ---

def test_search_breed_no_breed():
    # Test missing breed parameter.
    response = client.get("/search", params={"breed": ""})
    assert response.status_code == 400
    assert "Breed name is required" in response.json()["detail"]

def test_search_breed_no_similar(monkeypatch):
    # Patch the searcher global variable with a DummySearcher that returns an empty list.
    monkeypatch.setattr(app_module, "searcher", DummySearcher([]))
    
    response = client.get("/search", params={"breed": "Labrador"})
    assert response.status_code == 404
    assert "No similar images found for breed: Labrador" in response.json()["detail"]

def test_search_breed_success(monkeypatch):
    # Patch the searcher to return a list with one dummy image.
    monkeypatch.setattr(app_module, "searcher", DummySearcher(["dummy_image.jpg"]))
    # Override FileResponse in the app module so that we don’t try to load a real file.
    monkeypatch.setattr(app_module, "FileResponse", dummy_file_response)
    # Patch Image.open to return a dummy image.
    monkeypatch.setattr(app_module.Image, "open", dummy_image_open)

    response = client.get("/search", params={"breed": "Labrador"})
    assert response.status_code == 200
    # Check that the dummy file response content is returned.
    assert response.text == "dummy file content"
