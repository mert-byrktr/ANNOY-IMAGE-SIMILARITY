# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install the Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"]
