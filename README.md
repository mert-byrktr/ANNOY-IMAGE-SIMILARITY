⚠️ Note: This project is currently in active development and is subject to significant modifications.

This project first trains a breed model to predict the breed of a dog or cat. Then, it uses the breed model to search for similar images in a dataset of dog and cat images. Further, it can be extended to search for other things.

## Running the Project Locally

To run this project on your local machine, follow these steps:

### Prerequisites
- Ensure you have Python installed (version 3.7 or higher).
- Move your image data to appropriate directory.

### Clone the Repository
1. Open your terminal.
2. Navigate to the directory where you want to clone the project.
3. Run the following command:
   ```bash
   git clone <repository-url>
   ```

### Install Dependencies
1. Navigate into the project directory

2. Install any other dependencies listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### Run the Application

I have pre-computed the model and similarity indexes for my personal image dataset. You can also run it for your own dataset. After that you can use the API to search for similar images.

1. Run the build_annoy_index.py script to build the similarity indexes:
   ```bash
   python build_annoy_index.py
   ```

2. Run the train_breed_model.py script to train the breed model and save the predictions for each image:
   ```bash
   python train_breed_model.py
   ```
3. Run the app.py script to start the FastAPI server:
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8000 --reload
   ```
