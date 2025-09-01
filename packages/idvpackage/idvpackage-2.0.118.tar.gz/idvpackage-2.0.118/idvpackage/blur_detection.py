import cv2
import numpy as np


def is_blurry_laplace(image, threshold=70):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold


def is_blurry_canny(image, threshold=1500):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_count = np.sum(edges > 0)
    return edge_count < threshold


def fft_blur_check(image, threshold=150):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    fft_image = np.fft.fft2(gray)
    fft_shifted = np.fft.fftshift(fft_image)
    magnitude_spectrum = 20 * np.log(np.abs(fft_shifted))
    blur_metric = np.mean(magnitude_spectrum)
    return blur_metric < threshold


def has_bright_reflections(image, threshold=240, min_area_percentage=1.0):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    _, bright_areas = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    bright_percentage = (np.sum(bright_areas == 255) / (gray.shape[0] * gray.shape[1])) * 100
    return bright_percentage > min_area_percentage


def is_image_blur(
        image,
        laplace_threshold=70,
        canny_threshold=1500,
        fft_threshold=150,
        bright_reflection_threshold=240,
        bright_reflection_min_area=1.0
):
    conditions = []
    conditions.append(is_blurry_laplace(image, threshold=laplace_threshold))
    conditions.append(is_blurry_canny(image, threshold=canny_threshold))
    conditions.append(fft_blur_check(image, threshold=fft_threshold))
    conditions.append(has_bright_reflections(image, threshold=bright_reflection_threshold,
                                             min_area_percentage=bright_reflection_min_area))

    return sum(conditions) >= 2
