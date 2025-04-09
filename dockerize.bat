@echo off
REM =========================================================
REM Configure your Docker Hub username, repository, and tag.
REM =========================================================
set USERNAME=merttbayrakttar
set REPO=annoy-similarity
set TAG=latest

REM =========================================================
REM Log in to Docker Hub (this will prompt for credentials)
REM =========================================================
echo Logging in to Docker Hub...
docker login
if errorlevel 1 (
    echo Docker login failed. Please check your credentials.
    pause
    exit /b 1
)

REM =========================================================
REM Build the Docker image defined in docker-compose.yml
REM =========================================================
echo Building the Docker image with Docker Compose...
docker compose up -d --build
if errorlevel 1 (
    echo Docker Compose build failed.
    pause
    exit /b 1
)

REM =========================================================
REM Push the Docker image using Docker Compose push command
REM =========================================================
echo Pushing the Docker image to Docker Hub via Docker Compose...
docker compose push
if errorlevel 1 (
    echo Docker Compose push failed.
    pause
    exit /b 1
)

echo Docker image %USERNAME%/%REPO%:%TAG% pushed successfully!
pause
