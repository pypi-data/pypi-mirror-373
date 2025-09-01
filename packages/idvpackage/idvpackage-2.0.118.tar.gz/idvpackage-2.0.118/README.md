# Optical Character Recognition (OCR) and Facial Recognition Program
This repository contains a Python program designed to execute Optical Character Recognition (OCR) and Facial Recognition on images.

## Table of Contents
1. Introduction
2. Prerequisites
3. Usage
4. Modules Description

## Introduction
The Python program imports several packages necessary for OCR and facial recognition. It accepts a list of images as input, performs OCR, rotates the images to the busiest rotation, extracts ID information, and performs facial recognition by extracting the biggest face from the images. The program then computes the similarity between the faces and exports the extracted ID information into a JSON file.

## Prerequisites
Ensure the following packages are installed:
cv2
PIL (Image)
easyocr
pandas (pd)
skimage.transform (radon)
regular expressions (re)
datetime
concurrent.futures
NumPy (np)
TensorFlow (tf)
VGG16 model from Keras (tensorflow.keras.applications.vgg16)
tensorflow.keras.preprocessing (image)
scipy.spatial.distance
model_from_json from Keras (tensorflow.keras.models)
subprocess
urllib.request
dlib
time
matplotlib.pyplot
facenet
json
io
importlib.resources
You can install these packages using pip:

pip install opencv-python Pillow easyocr pandas scikit-image regex datetime concurrent.futures numpy tensorflow dlib matplotlib facenet-pytorch jsonpickle importlib_resources

Note: Keras and the VGG16 model come with TensorFlow, so there is no need to install them separately.

## Usage
To use this program, you can clone the repository, place your images in the same directory and modify the IMAGES list accordingly. Run the program in your terminal or command prompt as:
python ocr_and_facial_recognition.py

Please note that this program does not include any user interface and does not handle any errors or exceptions beyond what is included in the code.

## Modules Description
Importing Necessary Packages:
The program begins by importing all the necessary packages used in the OCR and Facial recognition steps.

## Data Introduction:
This section defines a list of image file names that will be used as input for the OCR and facial recognition steps of the program.

## Load easyocr and Anti-Spoofing Model:
Two functions to load the easyOCR package with English language support and the anti-spoofing model respectively.

## Data Preprocessing:
Several functions are defined here to open and read an image file, convert it to grayscale, perform a radon transform, find the busiest rotation, and rotate the image accordingly.

## Facial recognition:
This section is dedicated to detecting faces in an image using a HOG (Histogram of Oriented Gradients) face detector, extracting features, and computing the similarity between two sets of features using the cosine similarity metric.

## Information Extraction:
Finally, the program uses OCR to extract information from an image, computes the similarity between faces in different images, and outputs this information in a JSON file.

Please refer to the source code comments for more detailed explanations.

This is a basic explanation of the project and its usage. This project was last updated on 24th May 2023 and does not have any GUI or error handling beyond what is included in the code. For more details, please refer to the comments in the source code.
