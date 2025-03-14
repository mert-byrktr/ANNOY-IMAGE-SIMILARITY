@echo off
REM Exit immediately if a command fails (simulate "set -e")
REM Each command is followed by an error check

REM Variables for Docker Hub
set DOCKER_USERNAME=merttbayrakttar
set IMAGE_NAME=annoy-similarity
set TAG=latest

REM Build the Docker image using docker-compose
echo Building Docker image...
docker-compose build
if errorlevel 1 goto error

REM Tag the image for Docker Hub
echo Tagging the image...
docker tag %IMAGE_NAME% %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%
if errorlevel 1 goto error

REM Log in to Docker Hub (this will prompt for your password)
echo Logging in to Docker Hub...
docker login
if errorlevel 1 goto error

REM Push the image to Docker Hub
echo Pushing the image to Docker Hub...
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%
if errorlevel 1 goto error

echo Docker image pushed to Docker Hub: %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%

REM Now run docker-compose to start the services
echo Starting Docker Compose services...
docker-compose up -d
if errorlevel 1 goto error

echo Docker Compose services are running. Access the app at http://localhost:8000
pause
goto end

:error
echo An error occurred. Exiting.
pause
exit /b 1

:end
