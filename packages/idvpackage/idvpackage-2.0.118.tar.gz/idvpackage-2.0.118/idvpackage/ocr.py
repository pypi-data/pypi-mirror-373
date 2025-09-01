import pandas as pd
from google.oauth2.service_account import Credentials
from google.cloud import vision_v1
import json
import pycountry
from googletrans import Translator
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import base64
import io
import numpy as np
import cv2
from datetime import datetime, timedelta
import tempfile
from rapidfuzz import fuzz
import face_recognition
import re
import os

from idvpackage.constants import BRIGHTNESS_THRESHOLD, BLUR_THRESHOLD
from io import BytesIO
import time
import logging
# import anthropic
import openai
from idvpackage.blur_detection import is_image_blur
# from idvpackage.common import (
#     # load_and_process_image_deepface,
#     load_and_process_image_deepface_all_orientations
# )



logging.basicConfig(level=logging.INFO)

google_client_dict = {}



class IdentityVerification:

    def __init__(self, credentials_string, api_key=None, genai_key=None):
        """
        This is the initialization function of a class that imports a spoof model and loads an OCR
        reader.
        """
        st = time.time()
        credentials_dict = json.loads(credentials_string)
        credentials = Credentials.from_service_account_info(credentials_dict)

        self.client = google_client_dict.get(credentials)
        if not self.client:
            self.client = vision_v1.ImageAnnotatorClient(credentials=credentials)
            google_client_dict[credentials] = self.client

        self.api_key = api_key

        # self.genai_client = anthropic.Anthropic(
        #         api_key=genai_key,
        #     )

        openai.api_key = genai_key

        self.translator = Translator()
        self.iso_nationalities = [country.alpha_3 for country in pycountry.countries]
        print(f"\nInitialization time inside IDV Package: {time.time() - st}")

    def preprocess_image(self, image, sharpness=1.0, contrast=2.0,radius=2, percent=150, threshold=3):
        """Preprocess the image by sharpening and enhancing contrast."""

        # Apply sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(sharpness)  # Sharpen the image (increase sharpness)

        # Enhance the contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)  # Increase contrast

        image = image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))

        return image

    def image_conversion(self,image):
        """
        This function decodes a base64 string data and returns an image object.
        If the image is in RGBA mode, it is converted to RGB mode.
        :return: an Image object that has been created from a base64 encoded string.
        """
        # Decode base64 String Data
        # img = Image.open(io.BytesIO(base64.decodebytes(bytes(image, "utf-8"))))

        img_data = io.BytesIO(base64.decodebytes(bytes(image, "utf-8")))
        with Image.open(img_data) as img:
            if img.mode == 'RGBA':
                # Create a blank background image
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Paste the image on the background.
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            else:
                img = img.copy()
            return img

    def rgb2yuv(self, img):
        """
        Convert an RGB image to YUV format.
        """
        try:
            img = np.array(img)
            return cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
        except Exception as e:
            raise Exception(f"Error: {e}")

    def find_bright_areas(self, image, brightness_threshold):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh_image = cv2.threshold(gray_image, brightness_threshold, 255, cv2.THRESH_BINARY)[1]
        contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bright_areas = []

        for contour in contours:
            bounding_box = cv2.boundingRect(contour)

            area = bounding_box[2] * bounding_box[3]

            if area > 800:
                bright_areas.append(bounding_box)

        return len(bright_areas)

    def is_blurry(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        laplacian_variance = cv2.Laplacian(gray_image, cv2.CV_64F).var()

        return laplacian_variance

    def identify_input_type(self, data):
        if isinstance(data, bytes):
            return "video_bytes"
        else:
            pass

        try:
            decoded_data = base64.b64decode(data)

            if decoded_data:
                return "base_64"
        except Exception:
            pass

        return "unknown"

    def sharpen_image(self, image):
        kernel = np.array([[-1, -1, -1],
                           [-1, 9, -1],
                           [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)

    def adjust_contrast(self, image, factor):
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer.enhance(factor)
        return np.array(enhanced_image)

    def adjust_brightness(self, image, factor):
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Brightness(pil_image)
        enhanced_image = enhancer.enhance(factor)
        return np.array(enhanced_image)

    def enhance_quality(self, image):
        sharpened_image = self.sharpen_image(image)
        enhanced_image = self.adjust_brightness(sharpened_image, 1.2)
        enhanced_contrast = self.adjust_contrast(enhanced_image, 1.2)
        # grayscale_image = cv2.cvtColor(enhanced_contrast, cv2.COLOR_BGR2GRAY)

        return enhanced_contrast

    def check_document_quality(self, data):
        video_quality = {"error": ""}
        temp_video_file = tempfile.NamedTemporaryFile(delete=False)
        temp_video_file_path = temp_video_file.name

        try:
            # Write video bytes to the temporary file and flush
            temp_video_file.write(data)
            temp_video_file.flush()
            temp_video_file.close()  # Close the file to ensure it can be accessed by other processes

            video_capture = cv2.VideoCapture(temp_video_file.name)

            if video_capture.isOpened():
                frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

                for _ in range(frame_count):
                    ret, frame = video_capture.read()
                    #                         if ret:
                    # frame_count_vid+=1
                    # if frame_count_vid % 10 == 0:
                    _, buffer = cv2.imencode(".jpg", frame)
                    image_data = buffer.tobytes()

                    image = vision_v1.Image(content=image_data)

                    response = self.client.face_detection(image=image)
                    if len(response.face_annotations) >= 1:
                        break

            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            selfie_result = self.extract_selfie_from_video(video_capture)
            if isinstance(selfie_result, dict):
                video_quality["error"] = selfie_result["error"]
            else:
                (
                    selfie_blurry_result,
                    selfie_bright_result,
                ) = self.get_blurred_and_glared_for_doc(selfie_result)
                if (
                        selfie_blurry_result == "consider"
                        or selfie_bright_result == "consider"
                ):
                    video_quality["error"] = "face_not_clear_in_video"
                else:
                    video_quality["selfie"] = selfie_result
                    video_quality["shape"] = selfie_result.shape

            video_capture.release()  # Release the video capture

        # except Exception as e:
        #     video_quality["error"] = "bad_video"

        finally:
            # Ensure the temporary file is deleted
            if os.path.exists(temp_video_file_path):
                os.remove(temp_video_file_path)
                # print(f"Temporary file {temp_video_file_path} has been deleted.")

        return video_quality

    def extract_selfie_from_video(self, video_capture):
        """Extract the best quality selfie from video with speed optimizations for frontal faces."""
        video_dict = {'error': ''}

        try:
            total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                video_dict['error'] = 'invalid_video_frame_count'
                return video_dict

            # Check only 6 frames - 2 at start, 2 in the middle, 2 at the end
            frame_positions = [
                int(total_frames * 0.05),
                int(total_frames * 0.15),
                int(total_frames * 0.45),
                int(total_frames * 0.55),
                int(total_frames * 0.85),
                int(total_frames * 0.95)
            ]

            best_face = None
            best_score = -1
            best_frame = None
            best_frame_position = None
            frame_results = []

            print(f"Analyzing video with {total_frames} frames")
            print(f"Checking {len(frame_positions)} strategic frames")

            for target_frame in frame_positions:
                if target_frame >= total_frames:
                    target_frame = total_frames - 1
                if target_frame < 0:
                    target_frame = 0

                video_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                ret, frame = video_capture.read()
                if not ret or frame is None or frame.size == 0:
                    continue

                try:
                    scale = 0.7
                    small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)

                    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 90]
                    _, buffer = cv2.imencode(".jpg", small_frame, encode_params)

                    image = vision_v1.Image(content=buffer.tobytes())
                    response = self.client.face_detection(image=image, max_results=2)
                    faces = response.face_annotations

                    if not faces:
                        continue

                    frame_best_face = None
                    frame_best_score = -1

                    for face in faces:
                        vertices = [(int(vertex.x / scale), int(vertex.y / scale))
                                  for vertex in face.bounding_poly.vertices]

                        left = min(v[0] for v in vertices)
                        upper = min(v[1] for v in vertices)
                        right = max(v[0] for v in vertices)
                        lower = max(v[1] for v in vertices)

                        # Validate face coordinates
                        if not (0 <= left < right <= frame.shape[1] and 0 <= upper < lower <= frame.shape[0]):
                            continue

                        # Calculate face metrics
                        face_width = right - left
                        face_height = lower - upper
                        face_area = (face_width * face_height) / (frame.shape[0] * frame.shape[1])

                        # Reject small faces
                        if face_area < 0.05:
                            continue

                        # Calculate how centered the face is
                        face_center_x = (left + right) / 2
                        face_center_y = (upper + lower) / 2
                        frame_center_x = frame.shape[1] / 2
                        frame_center_y = frame.shape[0] / 2

                        center_dist_x = abs(face_center_x - frame_center_x) / (frame.shape[1] / 2)
                        center_dist_y = abs(face_center_y - frame_center_y) / (frame.shape[0] / 2)
                        center_score = 1.0 - (center_dist_x + center_dist_y) / 2

                        # For frontal faces, left and right eye/ear should be roughly symmetric
                        if len(face.landmarks) > 0:
                            # Head rotation detection
                            roll, pan, tilt = 0, 0, 0
                            if hasattr(face, 'roll_angle'):
                                roll = abs(face.roll_angle)
                            if hasattr(face, 'pan_angle'):
                                pan = abs(face.pan_angle)
                            if hasattr(face, 'tilt_angle'):
                                tilt = abs(face.tilt_angle)

                            head_angle_penalty = (roll + pan + tilt) / 180.0

                            # Symmetry detection from face bounding box
                            left_half = face_center_x - left
                            right_half = right - face_center_x
                            width_ratio = min(left_half, right_half) / max(left_half, right_half)

                            # Frontal-face score: higher for more frontal faces
                            # Perfect frontal face would be 1.0
                            frontal_score = width_ratio * (1.0 - head_angle_penalty)
                        else:
                            # No landmarks, estimate from bounding box
                            left_half = face_center_x - left
                            right_half = right - face_center_x
                            frontal_score = min(left_half, right_half) / max(left_half, right_half)

                        # Combined score weights different factors
                        # More weight for frontal-ness and face confidence
                        score = (
                            face.detection_confidence * 0.3 +
                            face_area * 0.2 +
                            center_score * 0.2 +
                            frontal_score * 0.3
                        )

                        # Heavy bonus for very frontal faces (nearly symmetric)
                        if frontal_score > 0.8:
                            score *= 1.5

                        # Extra bonus for centered faces
                        if center_score > 0.8:
                            score *= 1.2

                        if score > frame_best_score:
                            # Add margins for the face
                            margin_x = int(face_width * 0.2)
                            margin_y_top = int(face_height * 0.3)
                            margin_y_bottom = int(face_height * 0.1)

                            left_with_margin = max(0, left - margin_x)
                            upper_with_margin = max(0, upper - margin_y_top)
                            right_with_margin = min(frame.shape[1], right + margin_x)
                            lower_with_margin = min(frame.shape[0], lower + margin_y_bottom)

                            # Store the best face info
                            frame_best_score = score
                            frame_best_face = {
                                'face': face,
                                'left': left_with_margin,
                                'upper': upper_with_margin,
                                'right': right_with_margin,
                                'lower': lower_with_margin,
                                'frontal_score': frontal_score,
                                'center_score': center_score,
                                'confidence': face.detection_confidence,
                                'frame': target_frame
                            }

                    if frame_best_face is not None:
                        frame_results.append({
                            'frame': target_frame,
                            'face': frame_best_face,
                            'score': frame_best_score,
                            'frame_data': frame.copy()
                        })

                        if frame_best_score > best_score:
                            best_score = frame_best_score
                            best_face = frame_best_face
                            best_frame = frame.copy()
                            best_frame_position = target_frame

                except Exception as e:
                    continue

            # Process results
            if len(frame_results) > 0:
                # Sort faces by score
                frame_results.sort(key=lambda x: x['score'], reverse=True)

                for i, result in enumerate(frame_results[:min(3, len(frame_results))]):
                    face_info = result['face']
                    print(f"Rank {i+1}: Frame {face_info['frame']}, "
                          f"Score: {result['score']:.2f}, "
                          f"Frontal: {face_info['frontal_score']:.2f}, "
                          f"Center: {face_info['center_score']:.2f}")

                # Use the best frame
                best_result = frame_results[0]
                best_face = best_result['face']
                best_frame = best_result['frame_data']

                print(f"Selected frame {best_face['frame']} as best selfie")

            if best_face and best_frame is not None:
                try:
                    left = best_face['left']
                    upper = best_face['upper']
                    right = best_face['right']
                    lower = best_face['lower']

                    # Convert to RGB and crop
                    rgb_frame = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
                    cropped_face = rgb_frame[upper:lower, left:right]

                    # Validate cropped face
                    if cropped_face is None or cropped_face.size == 0:
                        video_dict['error'] = 'invalid_cropped_face'
                        return video_dict

                    print(f"Face shape: {cropped_face.shape}")
                    return cropped_face

                except Exception as e:
                    video_dict['error'] = 'error_processing_detected_face'
                    return video_dict
            else:
                video_dict['error'] = 'no_suitable_face_detected_in_video'
                return video_dict

        except Exception as e:
            video_dict['error'] = 'video_processing_error'
            return video_dict



    def is_colored(self, base64_image):
        img = self.image_conversion(base64_image)
        img = np.array(img)

        return len(img.shape) == 3 and img.shape[2] >= 3

    def get_blurred_and_glared_for_doc(self, image, brightness_threshold=BRIGHTNESS_THRESHOLD,
                                       blur_threshold=BLUR_THRESHOLD):
        blurred = 'clear'
        glare = 'clear'

        blurry1 = self.is_blurry(image)
        if blurry1 < blur_threshold:
            blurred = 'consider'

        brightness1 = np.average(image[..., 0])
        if brightness1 > brightness_threshold:
            glare = 'consider'

        return blurred, glare

    def standardize_date(self, input_date):
        input_formats = [
            "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y",
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y",
            "%Y%m%d", "%m%d%Y", "%d%m%Y",
            "%Y.%m.%d", "%d.%m.%Y", "%m.%d.%Y",
            "%Y %m %d", "%d %m %Y", "%m %d %Y",
        ]

        for format in input_formats:
            try:
                parsed_date = datetime.strptime(input_date, format)
                standardized_date = parsed_date.strftime("%d/%m/%Y")
                return standardized_date
            except ValueError:
                pass

        return None

    def compare_dates(self, date_str1, date_str2):
        date_format = "%d/%m/%Y"

        date1 = datetime.strptime(date_str1, date_format)
        date2 = datetime.strptime(date_str2, date_format)

        if date1 == date2:
            return True
        else:
            return False

    def check_nationality_in_iso_list(self, nationality):
        try:
            if len(nationality) > 3:
                try:
                    country = pycountry.countries.lookup(nationality)
                    nationality = country.alpha_3
                except:
                    return 'consider'

            ## Handling case for OMN as it comes as MN, due to O being considered as 0
            if nationality.upper() == 'MN':
                nationality = 'OMN'

            if nationality.upper() in self.iso_nationalities:
                return 'clear'
            else:
                return 'consider'

        except:
            return 'consider'

    def get_face_orientation(self, face_landmarks):
        left_eye = np.array(face_landmarks['left_eye']).mean(axis=0)
        right_eye = np.array(face_landmarks['right_eye']).mean(axis=0)

        eye_slope = (right_eye[1] - left_eye[1]) / (right_eye[0] - left_eye[0])
        angle = np.degrees(np.arctan(eye_slope))

        return angle

    def rotate_image(self, img):
        from skimage.transform import radon

        img_array = np.array(img)

        if len(img_array.shape) == 2:
            gray = img_array
        else:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        h, w = gray.shape
        if w > 640:
            gray = cv2.resize(gray, (640, int((h / w) * 640)))
        gray = gray - np.mean(gray)
        sinogram = radon(gray)
        r = np.array([np.sqrt(np.mean(np.abs(line) ** 2)) for line in sinogram.transpose()])
        rotation = np.argmax(r)
        angle = round(abs(90 - rotation) + 0.5)

        if abs(angle) > 5:
            rotated_img = img.rotate(angle, expand=True)
            return rotated_img

        return img

    def load_and_process_image_fr(self, base64_image, arr=False):
        try:
            if not arr:
                img = self.image_conversion(base64_image)
                img = np.array(img)
                image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                if base64_image.dtype != np.uint8:
                    base64_image = base64_image.astype(np.uint8)

                image = cv2.cvtColor(base64_image, cv2.COLOR_BGR2RGB)

            # base64_image = base64_image.split(',')[-1]
            # image_data = base64.b64decode(base64_image)
            # image_file = io.BytesIO(image_data)

            # image = face_recognition.load_image_file(image_file)

            face_locations = []
            face_locations = face_recognition.face_locations(image)

            if not face_locations:
                return [], []

            face_encodings = []
            face_encodings = face_recognition.face_encodings(image, face_locations)

            return face_locations, face_encodings
        except:
            return [], []

    def calculate_similarity(self, face_encoding1, face_encoding2):
        similarity_score = 1 - face_recognition.face_distance([face_encoding1], face_encoding2)[0]
        return round(similarity_score + 0.25, 2)
    

    def extract_face_and_compute_similarity(self, selfie, front_face_locations, front_face_encodings):
        from idvpackage.common import load_and_process_image_deepface
        try:
            if selfie is None:
                print("Error: Selfie image is None")
                return 0

            # Ensure the input array is contiguous and in the correct format
            if not selfie.flags['C_CONTIGUOUS']:
                selfie = np.ascontiguousarray(selfie)

            # Convert array to uint8 if needed
            if selfie.dtype != np.uint8:
                if selfie.max() > 255:
                    selfie = (selfie / 256).astype(np.uint8)
                else:
                    selfie = selfie.astype(np.uint8)

            # Try DeepFace first as it's generally more reliable
            # start_time = time.time()
            face_locations1, face_encodings1 = load_and_process_image_deepface(selfie)
            # end_time = time.time()

            if not face_locations1 or not face_encodings1:
                print("No face detected in Selfie Video by DeepFace")
                return 0

            # print(f"Face detection took {end_time - start_time:.3f} seconds")

            face_locations2, face_encodings2 = front_face_locations, front_face_encodings

            if not face_encodings2.any():
                print('No face detected in front ID')
                return 0

            largest_face_index1 = face_locations1.index(
                max(face_locations1, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))
            largest_face_index2 = face_locations2.index(
                max(face_locations2, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))

            face_encoding1 = face_encodings1[largest_face_index1]
            face_encoding2 = face_encodings2[largest_face_index2]

            similarity_score = self.calculate_similarity(face_encoding1, face_encoding2)
            # print(f"Calculated similarity score: {similarity_score}")

            return min(1, similarity_score)

        except Exception as e:
            print(f"Error in extract_face_and_compute_similarity: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def calculate_landmarks_movement(self, current_landmarks, previous_landmarks):
        return sum(
            abs(cur_point.position.x - prev_point.position.x) +
            abs(cur_point.position.y - prev_point.position.y)
            for cur_point, prev_point in zip(current_landmarks, previous_landmarks)
        )

    def calculate_face_movement(self, current_face, previous_face):
        return abs(current_face[0].x - previous_face[0].x) + abs(current_face[0].y - previous_face[0].y)

    def calculate_liveness_result(self, eyebrow_movement, nose_movement, lip_movement, face_movement):
        eyebrow_movement_threshold = 15.0
        nose_movement_threshold = 15.0
        lip_movement_threshold = 15.0
        face_movement_threshold = 10.0

        if (
                eyebrow_movement > eyebrow_movement_threshold or
                nose_movement > nose_movement_threshold or
                lip_movement > lip_movement_threshold or
                face_movement > face_movement_threshold
        ):
            return True
        else:
            return False

    def detect_image_format(self, base64_image):
        import imghdr

        decoded_image = base64.b64decode(base64_image)
        format = imghdr.what(None, decoded_image)

        return format

    def frame_count_and_save(self, cap):
        frames = []
        status, frame = cap.read()
        while status:
            frames.append(frame)
            status, frame = cap.read()

        cap.release()
        return frames

    def check_for_liveness(self, similarity, video_bytes, face_match_threshold=0.59):
        st = time.time()
        from idvpackage.liveness_spoofing_v2 import test
        # Create a temporary file that will not be deleted automatically
        temp_video_file = tempfile.NamedTemporaryFile(delete=False)
        temp_video_file_path = temp_video_file.name

        try:
            # Write video bytes to the temporary file and flush
            temp_video_file.write(video_bytes)
            temp_video_file.flush()
            temp_video_file.close()  # Close the file to ensure it can be accessed by other processes

            try:
                result = test(temp_video_file_path)
                if result:
                    return result
            except Exception as e:
                print(f'\nError in Liveness: {e}')
                return None

        finally:
            # Ensure the temporary file is deleted
            if os.path.exists(temp_video_file_path):
                os.remove(temp_video_file_path)
                # print(f"Temporary file {temp_video_file_path} has been deleted.")
            logging.info(
                f"--------------Time taken for Liveness and Spoofing in IDV package: {time.time() - st} seconds\n")

    def convert_dob(self, input_date):
        day = input_date[4:6]
        month = input_date[2:4]
        year = input_date[0:2]

        current_year = datetime.now().year
        current_century = current_year // 100
        current_year_last_two_digits = current_year % 100

        century = current_century
        # If the given year is greater than the last two digits of the current year, assume last century
        if int(year) > current_year_last_two_digits:
            century = current_century - 1

        final_date = f"{day}/{month}/{century}{year}"

        return final_date

    def convert_expiry_date(self, input_date):
        day = input_date[4:6]
        month = input_date[2:4]
        year = input_date[0:2]

        current_year = datetime.now().year
        current_century = current_year // 100
        current_year_last_two_digits = current_year % 100
        century = current_century

        if int(year) <= current_year_last_two_digits:
            century = current_century
        else:
            century = current_century
        final_date = f"{day}/{month}/{century}{year}"

        return final_date

    def clean_string(self, input_string):
        cleaned_string = re.sub(r'[^\w\s]', ' ', input_string)
        return cleaned_string.strip()

    def find_and_slice_number(input_number, digits):
        from itertools import permutations
        # Generate all possible permutations of the digits
        perms = [''.join(p) for p in permutations(digits)]

        # Initialize variables to keep track of the found pattern and its index
        found_pattern = None
        found_index = -1

        # Search for any permutation of the digits in the input_number
        for perm in perms:
            found_index = input_number.find(perm)
            if found_index != -1:
                found_pattern = perm
                break

        # If a pattern is found, slice the number accordingly
        if found_pattern:
            if found_index > len(input_number) - found_index - len(found_pattern):
                # Slice to the left
                sliced_number = input_number[:found_index + len(found_pattern)]
            else:
                # Slice to the right
                sliced_number = input_number[found_index:]

            return sliced_number
        else:
            return ''

    def get_ocr_results(self, processed_image, country=None, side=None):
        # with io.BytesIO() as output:
        #     processed_image.save(output, format="PNG")
        #     image_data = output.getvalue()

        # image = vision_v1.types.Image(content=image_data)

        if country == 'QAT' or country == 'LBN' or country == 'IRQ' or country == 'SDN':
            image = vision_v1.types.Image(content=processed_image)

        else:
            compressed_image = BytesIO()
            processed_image.save(compressed_image, format="JPEG", quality=60, optimize=True)
            compressed_image_data = compressed_image.getvalue()
            image = vision_v1.types.Image(content=compressed_image_data)

        response = self.client.text_detection(image=image)
        id_infos = response.text_annotations

        return id_infos

    def extract_document_info(self, image, side, document_type, country, nationality, step_data=None):
        st = time.time()
        document_data = {}
        #side=auto only in testing mode.
        # if document_type != 'passport' and country == 'IRQ':
        #     document_data = self.agent_extraction(image, country, side)
        #     logging.info(
        #         f"--------------Time taken for Front ID Extraction in IDV package: {time.time() - st} seconds\n")
        #     return document_data

        if country == 'IRQ':
            document_data = self.agent_extraction(image, country, nationality,side, step_data)
            logging.info(
                f"--------------Time taken for Front ID Extraction in IDV package: {time.time() - st} seconds\n")
            return document_data

        if document_type == 'national_id' and side == 'front':
            document_data = self.extract_front_id_info(image, country, nationality)
            logging.info(
                f"--------------Time taken for Front ID Extraction in IDV package: {time.time() - st} seconds\n")
            return document_data

        if document_type == 'national_id' and side == 'back':
            document_data = self.extract_back_id_info(image, country, nationality)
            logging.info(
                f"--------------Time taken for Back ID Extraction in IDV package: {time.time() - st} seconds\n")

        if document_type == 'passport' and (side == 'first' or side == 'page1' or side == ''):
            document_data = self.exract_passport_info(image, country, nationality, step_data)
            logging.info(
                f"--------------Time taken for Passport Extraction in IDV package: {time.time() - st} seconds\n")

        if document_type == 'passport' and (side == 'last' or side == 'page2'):
            document_data = self.exract_passport_info_back(image, country, nationality)
            logging.info(
                f"--------------Time taken for Passport Extraction in IDV package: {time.time() - st} seconds\n")

        if document_type == 'driving_license':
            pass

        return document_data

    def agent_extraction(self, front_id, country, nationality,side, step_data=None):
        from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
        from idvpackage.common import get_facial_encodings_deepface_irq, load_and_process_image_deepface, cosine_similarity
        from idvpackage.iraq_id_extraction_withopenai import extraction_chain
        import idvpackage.genai_utils as sanity_utils
        result = {'error': '', "error_details": ''}
        try:
            st = time.time()
            processed_front_id = self.image_conversion(front_id)
            logging.info(f'----------------Time taken for image conversion: {time.time() - st} seconds\n')
            compressed_image = BytesIO()
            processed_front_id.save(compressed_image, format="JPEG", quality=85, optimize=True)
            compressed_image_data = compressed_image.getvalue()

            st = time.time()
            front_id_text = self.get_ocr_results(compressed_image_data, country=country)
            front_id_text_desc = front_id_text[0].description
            logging.info(f'----------------Time taken for Google Vision API call: {time.time() - st} seconds\n')

            #To allow for non-iraqi passports

            #when uploading passports later, after one has 'skipped passport' during onboading, we get nationality=None


            if side in ['page1', 'first'] and nationality != 'IRQ' and nationality is not None:
                front_data = self.exract_passport_info(front_id, country, nationality)

                if front_data.get("name", ''):
                    front_data['full_name'] = front_data.get('name', '')
                elif front_data.get('first_name') and front_data.get("last_name"):
                    front_data['full_name'] = front_data.get("first_name", '') + ' ' + front_data.get("last_name", "")

                # handle expired passports
                expiry_date = (
                        front_data.get("expiry_date")
                        or front_data.get("date_of_expiry")
                )
                if expiry_date:
                    is_doc_expired = sanity_utils.is_expired_id(expiry_date)

                    if is_doc_expired:
                        return {"error": "expired_id", "error_details": "expired ID"}

                return front_data

            if side in ['page2','last'] and nationality!='IRQ':
                front_data = self.exract_passport_info_back(front_id,country,nationality)

                if front_data.get("name",''):
                    front_data['full_name'] = front_data.get('name','')
                elif front_data.get('first_name') and front_data.get("last_name"):
                    front_data['full_name'] = front_data.get("first_name",'')+ ' ' + front_data.get("last_name","")

                #handle expired passports
                expiry_date = (
                        front_data.get("expiry_date")
                        or front_data.get("date_of_expiry")
                )
                if expiry_date:
                    is_doc_expired = sanity_utils.is_expired_id(expiry_date)

                    if is_doc_expired:
                        return {"error": "expired_id", "error_details": "expired ID"}

                return front_data

            #the extra side here is for testing. So that when we test, we can pass in side='auto', instead of passing front and back seperately.
            st = time.time()
            result_extraction, side = extraction_chain(ocr_text=front_id_text_desc, openai_key=openai.api_key, side=side)
            logging.info(f'----------------Time taken for Extraction Chain (openAI + langchain call): {time.time() - st} seconds\n')

            if result_extraction['error']:
                return result_extraction
            result.update(result_extraction)


            st = time.time()
            image = np.array(processed_front_id)
            doc_on_pp_result = 'clear'
            template_result = 'clear'
            logo_result = 'clear'

            #uses google vision api
            st = time.time()
            # screenshot_result = detect_screenshot(self.client, front_id)
            # #
            # # #uses google vision api
            # photo_on_screen_result = detect_photo_on_screen(self.client, front_id)
            # valid_nationality_result = self.check_nationality_in_iso_list(result.get('nationality',''))
            # front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)
            #logging.info(f'----------------Time taken for fraud detection attributes: {time.time() - st} seconds\n')


            logging.info(f'----------------Time taken for gvision api calls for: detect screensot, detect_photo_on_screen, get_blurred_and_glared_for_doc: {time.time() - st} seconds\n')

            # if side=='front' or side=='page1':
            #     st = time.time()
            #     front_face_locations, front_face_encodings = load_and_process_image_deepface(front_id)
            #     logging.info(f'----------------Time taken for face extraction: {time.time() - st} seconds\n')
            #
            #     front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
            #     front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])
            #
            #
            #     if step_data:
            #         try:
            #             print(f"Matching face from Passport with National ID")
            #             national_id_front_face_locations = step_data.get("front_face_locations")
            #             national_id_front_face_encodings = json.loads(step_data.get("front_face_encodings"))
            #             st = time.time()
            #             national_id_front_face_encodings = np.array(national_id_front_face_encodings[0], dtype=np.float32)
            #             similarity = self.calculate_similarity(national_id_front_face_encodings, front_face_encodings[0])
            #             logging.info(f'----------------Time taken for face extraction for matching passport with front id: {time.time() - st} seconds\n')
            #             result["similarity_score"] = similarity
            #             print(f"Front ID and Passport similarity score: {similarity}")
            #             if similarity <= 0.65:
            #                 result["error"] = 'face_mismatch'
            #                 return {"error":"face_mismatch", "error_details":"Front ID and Passport Face dont match."}
            #         except Exception as e:
            #             result["error"] = 'National ID Image Not Found'
            #             result["error_details"] = e
            #             return result


            if side=='front' or side=='page1':

                st = time.time()
                if step_data and len(json.loads(step_data.get("front_face_encodings"))[0])==128:
                    front_face_locations, front_face_encodings = load_and_process_image_deepface(front_id)
                else:
                    front_face_locations, front_face_encodings = get_facial_encodings_deepface_irq(image,country=country)
                logging.info(f'----------------Time taken for face extraction: {time.time() - st} seconds\n')

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])


                if step_data:
                    try:
                        print(f"Matching face from Passport with National ID")
                        national_id_front_face_locations = json.loads(step_data.get("front_face_locations"))
                        national_id_front_face_encodings = json.loads(step_data.get("front_face_encodings"))
                        st = time.time()

                        largest_face_index1 = national_id_front_face_locations.index(max(national_id_front_face_locations, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))
                        largest_face_index2 = front_face_locations.index(max(front_face_locations, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))

                        face_encoding1 = national_id_front_face_encodings[largest_face_index1]
                        face_encoding2 = front_face_encodings[largest_face_index2]

                        if len(national_id_front_face_encodings[0])==128:
                            national_id_front_face_encodings = np.array(national_id_front_face_encodings[0],
                                                                        dtype=np.float32)
                            similarity = self.calculate_similarity(national_id_front_face_encodings,
                                                                   front_face_encodings[0])
                            logging.info(
                                f'----------------Time taken for face extraction for matching passport with front id: {time.time() - st} seconds\n')
                            result["similarity_score"] = similarity
                            print(f"Front ID and Passport similarity score: {similarity}")
                            if similarity <= 0.65:
                                result["error"] = 'face_mismatch'
                                return {"error": "face_mismatch",
                                        "error_details": "Front ID and Passport Face dont match."}
                        else:

                            similarity = cosine_similarity(face_encoding1, face_encoding2)
                            logging.info(f'----------------Time taken for face extraction for matching passport with front id: {time.time() - st} seconds\n')
                            result["similarity_score"] = similarity
                            print(f"Front ID and Passport similarity score: {similarity}")
                            if similarity <= 0.30:
                                result["error"] = 'face_mismatch'
                                return {"error":"face_mismatch", "error_details":"Front ID and Passport Face dont match."}
                    except Exception as e:
                        result["error"] = 'covered_photo'
                        result["error_details"] = e
                        return result

                if side=='front':
                    data_temp = {
                        'front_extracted_data': front_id_text_desc,
                        f'translated_{side}_id_text':'',
                        'front_coloured': True,
                        'back_coloured':True,
                        'front_doc_on_pp': doc_on_pp_result,
                        'front_logo_result': logo_result,
                        'front_template_result': template_result,
                        'front_screenshot_result': '',
                        'front_photo_on_screen_result': '',
                        'front_blurred': '',
                        'front_glare': '',
                        'front_face_locations': front_face_locations_str,
                        'front_face_encodings': front_face_encodings_str,
                        'front_tampered_result': 'clear',
                        'issuing_country':'IRQ',
                        'valid_nationality': 'valid_nationality_result'
                    }

                elif side=='page1':
                    data_temp = {
                        # 'back_tampered_result': tampered_result_back,
                        'passport_data': front_id_text_desc,
                        'front_coloured': True,
                        'back_coloured': True,
                        'front_logo_result': 'clear',
                        'front_doc_on_pp': doc_on_pp_result,
                        'front_screenshot_result': 'screenshot_result',
                        'front_photo_on_screen_result': 'photo_on_screen_result',
                        'doc_on_pp': doc_on_pp_result,
                        'screenshot_result': 'screenshot_result',
                        'photo_on_screen_result': 'photo_on_screen_result',
                        'front_blurred': 'front_blurred',
                        'front_glare': 'front_glare',
                        'back_blurred': 'front_blurred',
                        'back_glare': 'front_glare',
                        'front_face_locations': front_face_locations_str,
                        'front_face_encodings': front_face_encodings_str,
                        'valid_nationality': 'valid_nationality_result',
                        'issuing_country': 'IRQ',
                        'nationality_received': nationality
                    }
                else:
                    data_temp={}

                result.update(data_temp)
                required_keys = ["front_face_locations", "front_face_encodings"]
                empty_string_keys = [key for key, value in result.items() if key in required_keys and value == '']
                empty_string_keys = [key for key, value in result.items() if key in required_keys and value == '[]']



                if empty_string_keys:
                    result['error'] = 'covered_photo'
                    result['error_details'] = f"Missing fields: {empty_string_keys}"
            if side=='page1':
                result['passport_data'] = front_id_text_desc
            if side=='back':
                valid_nationality_result = self.check_nationality_in_iso_list(result.get('nationality'))
                back_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'valid_nationality': valid_nationality_result,
                    'back_extracted_data': front_id_text_desc,
                    'translated_back_id_text': '',
                    'back_coloured': True,
                    'occupation': '',
                    'employer': '',
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': 'screenshot_result',
                    'photo_on_screen_result': 'photo_on_screen_result',
                    'back_blurred': 'front_blurred',
                    'back_glare': 'front_glare',
                    'back_tampered_result':'clear'
                }

                result.update(back_data_update)


        except Exception as e:
            result['error'] = 'bad_image'
            result['error_details'] = e

        return result

    def extract_front_id_info(self, front_id, country, nationality):
        if country == 'UAE':
            print("working on UAE")
            from idvpackage.ocr_utils import detect_logo, detect_photo_on_screen, detect_screenshot, \
                document_on_printed_paper
            from idvpackage.common import detect_id_card_uae, load_and_process_image_deepface

            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                processed_front_id = self.image_conversion(front_id)
                front_id_text = self.get_ocr_results(processed_front_id)
                front_id_text_desc = front_id_text[0].description
                combined_pattern = r'(Resident Identity|Identity Card|Golden Card|FEDERAL AUTHORITY FOR IDENTITY)'
                match = re.search(combined_pattern, front_id_text_desc, re.IGNORECASE)

                if not match:
                    front_data["error"] = "not_front_id"
                    return front_data

                img = processed_front_id
                image = np.array(img)
                pil_image = Image.fromarray(image)

                doc_on_pp_result = document_on_printed_paper(image)

                with io.BytesIO() as output:
                    pil_image.save(output, format="PNG")
                    image_data = output.getvalue()

                # logo_result = detect_logo(self.client, image_data, country)
                logo_result = 'clear'

                screenshot_result = detect_screenshot(self.client, front_id)
                photo_on_screen_result = detect_photo_on_screen(self.client, front_id)

                front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)
                # print(f"blurred, glare: {front_blurred, front_glare}")

                front_face_locations, front_face_encodings = load_and_process_image_deepface(front_id)
                # front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                tampered_result, part_text = detect_id_card_uae(self.client, image_data, front_id_text)

                # dob, expiry = '', ''
                # date_matches = re.findall(r'\d{2}/\d{2}/\d{4}', front_id_text_desc)
                # sorted_dates = sorted(date_matches)

                # if len(sorted_dates) > 1:
                #     dob = sorted_dates[0]
                #     expiry = sorted_dates[-1]

                front_data = {
                    'front_extracted_data': front_id_text_desc,
                    'front_coloured': True,
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_logo_result': logo_result,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': front_blurred,
                    'front_glare': front_glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str,
                    'front_tampered_result': tampered_result
                }

                non_optional_keys = ["front_face_locations", "front_face_encodings"]
                empty_string_keys = [key for key, value in front_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    front_data['error'] = 'covered_photo'

            except Exception as e:
                front_data['error'] = 'bad_image'
                front_data['error_details'] = e

            return front_data

        if country == 'SAU':
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.sau_id_extraction import extract_id_details
            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                processed_front_id = self.image_conversion(front_id)
                front_id_text = self.get_ocr_results(processed_front_id)
                front_id_text = front_id_text[0].description
                front_id_text_list = front_id_text.split('\n')

                img = self.image_conversion(front_id)
                image = np.array(img)
                pil_image = Image.fromarray(image)

                doc_on_pp_result = document_on_printed_paper(image)

                with io.BytesIO() as output:
                    pil_image.save(output, format="PNG")
                    image_data = output.getvalue()
                logo_result = 'clear'
                screenshot_result = detect_screenshot(self.client, front_id)
                photo_on_screen_result = detect_photo_on_screen(self.client, front_id)

                front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)

                front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                front_data_fields = extract_id_details(front_id_text_list)
                valid_nationality_result = self.check_nationality_in_iso_list(front_data_fields.get('nationality'))

                front_data = {
                    'valid_nationality': valid_nationality_result,
                    'front_extracted_data': front_id_text,
                    'front_coloured': True,
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_logo_result': logo_result,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': front_blurred,
                    'front_glare': front_glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str
                }

                front_data.update(front_data_fields)

                non_optional_keys = ["front_face_locations", "front_face_encodings", "id_number", "name", "dob",
                                     "expiry_date", "gender", "nationality"]
                empty_string_keys = [key for key, value in front_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    front_data['error'] = 'covered_photo'

            except Exception as e:
                front_data['error'] = 'bad_image'
                front_data['error_details'] = e

            return front_data

        if country == 'IRQ':
            logging.info("-------------Working on IRQ \n")
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.iraq_id_extraction import iraq_front_id_extraction, extract_mother_surname, \
                extract_mother_name, extract_paternal_grandfather_name
            from idvpackage.common import load_and_process_image_deepface
            from deep_translator import GoogleTranslator

            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                st = time.time()
                processed_front_id = self.image_conversion(front_id)
                logging.info(f'----------------Time taken for image conversion: {time.time() - st} seconds\n')

                st = time.time()
                compressed_image = BytesIO()
                processed_front_id.save(compressed_image, format="JPEG", quality=75, optimize=True)
                compressed_image_data = compressed_image.getvalue()

                front_id_text = self.get_ocr_results(compressed_image_data, country='IRQ', side='front')
                front_id_text_desc = front_id_text[0].description
                logging.info(f'----------------Time taken for vision: {time.time() - st} seconds\n')

                try:
                    translated_id_text = self.translator.translate(front_id_text_desc, src='ar', dest='en').text
                except Exception as e:
                    logging.info(f'--------------Fallback for translation keyword matching\n')
                    translated_id_text = GoogleTranslator('ar', 'en').translate(front_id_text_desc)

                # logging.info(f'\n----------------Time taken for translation: {time.time() - st} seconds')

                combined_pattern = r'(Ministry of Interior|Republic of Iraq|National Card|Passports and Residence|Republic|Ministry|Iraq)'
                match = re.search(combined_pattern, translated_id_text, re.IGNORECASE)

                if not match:
                    front_data["error"] = "not_front_id"
                    return front_data

                st = time.time()
                image = np.array(processed_front_id)
                # pil_image = Image.fromarray(image)

                ## TODO: uncomment this later with more sophisticated approach for doc_on_pp
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'

                # with io.BytesIO() as output:
                #     pil_image.save(output, format="PNG")
                #     image_data = output.getvalue()

                template_result = 'clear'
                logo_result = 'clear'

                screenshot_result = detect_screenshot(self.client, front_id)
                photo_on_screen_result = detect_photo_on_screen(self.client, front_id)

                front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)
                logging.info(f'----------------Time taken for fraud detection attributes: {time.time() - st} seconds\n')

                st = time.time()
                front_face_locations, front_face_encodings = load_and_process_image_deepface(front_id)
                logging.info(f'----------------Time taken for face extraction: {time.time() - st} seconds\n')
                # front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                # image_format = 'jpg'
                st = time.time()
                image_format = self.detect_image_format(front_id)

                front_data_fields = iraq_front_id_extraction(self.client, compressed_image_data, front_id_text,
                                                             front_id_text_desc, translated_id_text, image_format)
                logging.info(
                    f'----------------Time taken for iraq data formatting and final extraction: {time.time() - st} seconds\n')

                front_data_temp = {
                    'front_extracted_data': front_id_text_desc,
                    'translated_front_id_text': translated_id_text,
                    'front_coloured': True,
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_logo_result': logo_result,
                    'front_template_result': template_result,
                    # 'front_tampered_result': tampered_result_front,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': front_blurred,
                    'front_glare': front_glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str
                }

                front_data.update(front_data_fields)

                front_data.update(front_data_temp)

                required_keys = ["front_face_locations", "front_face_encodings", "id_number", "name"]
                empty_string_keys = [key for key, value in front_data.items() if key in required_keys and value == '']

                if empty_string_keys:
                    front_data['error'] = 'covered_photo'

            except Exception as e:
                front_data['error'] = 'bad_image'
                front_data['error_details'] = e

            try:
                dict_mother_surname = extract_mother_surname(front_id_text_desc)
                dict_mother_surname['mother_last_name_en'] = GoogleTranslator('ar', 'en').translate(
                    f"Name: {dict_mother_surname['mother_last_name']}").upper()
                # Check if "NAME: " is in the translated string, and remove it
                if "NAME: " in dict_mother_surname['mother_last_name_en']:
                    dict_mother_surname['mother_last_name_en'] = dict_mother_surname['mother_last_name_en'].replace(
                        "NAME: ", "")


            except Exception as e:
                dict_mother_surname = {"mother_last_name": '', 'mother_last_name_en': ''}

            front_data.update(dict_mother_surname)

            try:
                dict_third_name = extract_paternal_grandfather_name(front_id_text_desc)
                dict_third_name['third_name_en'] = GoogleTranslator('ar', 'en').translate(
                    dict_third_name['third_name']).upper()
            except Exception as e:
                dict_third_name = {"third_name_en": '', 'third_name': ''}

            front_data.update(dict_third_name)

            try:
                dict_mother_name = extract_mother_name(front_id_text_desc)
                dict_mother_name['mother_first_name_en']= GoogleTranslator('ar', 'en').translate(f'Name: {dict_mother_name["mother_first_name"]}').upper()
                # Check if "NAME: " is in the string, and remove it
                if "NAME: " in dict_mother_name['mother_first_name_en']:
                    dict_mother_name['mother_first_name_en'] = dict_mother_name['mother_first_name_en'].replace(
                        "NAME: ", "")


            except Exception as e:
                dict_mother_name = {"mother_first_name": '', 'mother_first_name_en': ''}

            front_data.update(dict_mother_name)

            if front_data.get('last_name', '') and front_data.get('mother_first_name', ''):
                if front_data.get('last_name') == front_data.get('mother_last_name'):
                    front_data['last_name'], front_data['last_name_en'] = '', ''

            return front_data

        if country == 'QAT':

            print("working on QAT with compression")
            from idvpackage.qatar_id_extraction import qatar_front_id_extraction
            from idvpackage.common import load_and_process_image_deepface_all_orientations

            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                st = time.time()
                processed_front_id = self.image_conversion(front_id)
                logging.info(f'----------------Time taken for image conversion front: {time.time() - st} seconds\n')

                st = time.time()
                compressed_image = BytesIO()
                processed_front_id.save(compressed_image, format="JPEG", quality=70, optimize=True)
                compressed_image_data = compressed_image.getvalue()

                front_id_text = self.get_ocr_results(compressed_image_data, country='QAT', side='front')
                front_id_text_desc = front_id_text[0].description
                logging.info(f'----------------Time taken for vision front: {time.time() - st} seconds\n')
                combined_pattern = r'(State of Qatar|Residency Permit)'
                match = re.search(combined_pattern, front_id_text_desc, re.IGNORECASE)

                if not match:
                    front_data["error"] = "not_front_id"
                    return front_data

                # image = np.array(processed_front_id)
                # doc_on_pp_result = document_on_printed_paper(image)

                st = time.time()
                #qatar's original face encodings code
                front_face_locations, front_face_encodings = load_and_process_image_deepface_all_orientations(front_id)


                # front_face_locations, front_face_encodings = load_and_process_image_deepface_optimized(front_id)
                logging.info(f'----------------Time taken for face extraction front: {time.time() - st} seconds\n')
                # front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                st = time.time()
                front_data_fields = qatar_front_id_extraction(self.client, compressed_image_data, front_id_text,
                                                              front_id_text_desc, openai.api_key)

                if 'error' in front_data_fields.keys():
                    return front_data_fields
                logging.info(
                    f'----------------Time taken for qatar data formatting and final extraction front: {time.time() - st} seconds\n')

                expiry_date = front_data_fields.get('expiry_date', '')

                # print(f"TAMPERING: {tampered_result_front}")
                # valid_nationality_result = self.check_nationality_in_iso_list(front_data_fields.get('nationality'))

                front_data_temp = {
                    'front_extracted_data': front_id_text_desc,
                    'valid_nationality': 'clear',
                    'front_coloured': True,
                    'front_doc_on_pp': 'clear',
                    'front_logo_result': 'clear',
                    'front_template_result': 'clear',
                    # 'front_tampered_result': tampered_result_front,
                    'front_screenshot_result': 'clear',
                    'front_photo_on_screen_result': 'clear',
                    'front_blurred': 'clear',
                    'front_glare': 'clear',
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str
                }

                front_data_fields.update(front_data_temp)
                front_data.update(front_data_fields)

                error = ""
                if expiry_date:
                    try:
                        dt_obj = datetime.strptime(expiry_date, '%d/%m/%Y')
                        tomorrow = datetime.today() + timedelta(days=1)
                        if dt_obj < tomorrow:
                            front_data['error'] = 'expired_id'
                    except:
                        pass

                required_keys = ["expiry", "name", "id_number"]
                empty_string_keys = [key for key, value in front_data.items() if key in required_keys and value == '']

                if empty_string_keys:
                    front_data['error'] = 'covered_photo'


            except Exception as e:
                print(e)
                front_data['error'] = 'bad_image'
                front_data['error_details'] = e

            return front_data

        if country == 'LBN':
            logging.info("----------------Working on LBN\n")
            from idvpackage.ocr_utils import detect_logo, detect_photo_on_screen, detect_screenshot, \
                document_on_printed_paper
            from idvpackage.lebanon_id_extraction import lebanon_front_id_extraction
            from idvpackage.common import load_and_process_image_deepface

            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                st = time.time()
                processed_front_id = self.image_conversion(front_id)
                logging.info(f'----------------Time taken for image conversion front: {time.time() - st} seconds\n')

                st = time.time()
                compressed_image = BytesIO()
                processed_front_id.save(compressed_image, format="JPEG", quality=90, optimize=True)
                compressed_image_data = compressed_image.getvalue()

                front_id_text = self.get_ocr_results(compressed_image_data, country='LBN')
                front_id_text_desc = front_id_text[0].description
                logging.info(f'----------------Time taken for vision front: {time.time() - st} seconds\n')

                st = time.time()
                try:
                    translated_id_text = self.translator.translate(front_id_text_desc, src='ar', dest='en').text
                except:
                    logging.info(f'\n--------------Fallback for translation keyword matching')
                    from deep_translator import GoogleTranslator
                    translated_id_text = GoogleTranslator('ar', 'en').translate(front_id_text_desc)
                logging.info(f'----------------Time taken for ar-en translation front: {time.time() - st} seconds\n')

                combined_pattern = r'(Lebanon Republic|Ministry of)'
                match = re.search(combined_pattern, translated_id_text, re.IGNORECASE)

                if not match:
                    front_data["error"] = "not_front_id"
                    return front_data

                image = np.array(processed_front_id)

                st = time.time()
                ## TODO: doc_on_pp and detect_photo_on_screen for LBN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                ## no logo for Lebanon ID's
                logo_result = 'clear'
                template_result = 'clear'
                ## TODO: template matching for Lebanon ID's
                # template_result = detect_logo(self.client, compressed_image_data, country, compare_type='template', side='front')
                ## TODO: tampering result for Lebanon ID's - pending tampered samples
                # tampered_result_front = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(front_id, "utf-8"))))))
                screenshot_result = detect_screenshot(self.client, front_id)
                # photo_on_screen_result = detect_photo_on_screen(self.client, image)
                photo_on_screen_result = 'clear'
                front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)
                logging.info(
                    f'----------------Time taken for fraud detection attributes front: {time.time() - st} seconds\n')

                # front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)
                st = time.time()
                front_face_locations, front_face_encodings = load_and_process_image_deepface(front_id)
                logging.info(f'----------------Time taken for face extraction front: {time.time() - st} seconds\n')

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                st = time.time()
                front_data_fields = lebanon_front_id_extraction(front_id_text_desc)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction front: {time.time() - st} seconds\n')

                # print(f"TAMPERING: {tampered_result_front}")

                front_data_temp = {
                    'front_extracted_data': front_id_text_desc,
                    'translated_front_id_text': translated_id_text,
                    'front_coloured': True,
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_logo_result': logo_result,
                    'front_template_result': template_result,
                    # 'front_tampered_result': tampered_result_front,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': front_blurred,
                    'front_glare': front_glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str
                }

                front_data.update(front_data_temp)
                front_data.update(front_data_fields)

                required_keys = ["front_face_locations", "front_face_encodings", "name", "dob", "dob_en",
                                 "place_of_birth_ar", "id_number", "expiry_date"]

                empty_string_keys = [
                    key for key, value in front_data.items()
                    if key in required_keys and (value == '' or value == '[]' or value == [] or not value)
                ]

                if empty_string_keys:
                    front_data['error'] = 'covered_photo'

            except Exception as e:
                front_data['error'] = 'bad_image'
                front_data['error_details'] = e

            return front_data

        if country == 'SDN':
            logging.info("----------------Working on SDN\n")
            from idvpackage.ocr_utils import detect_logo, detect_photo_on_screen, detect_screenshot, \
                document_on_printed_paper
            from idvpackage.sudan_id_extraction import sdn_front_id_extraction
            from idvpackage.common import load_and_process_image_deepface
            from idvpackage.blur_detection import is_image_blur

            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                st = time.time()
                processed_front_id = self.image_conversion(front_id)
                logging.info(f'----------------Time taken for image conversion front: {time.time() - st} seconds\n')

                st = time.time()
                compressed_image = BytesIO()
                processed_front_id.save(compressed_image, format="JPEG", quality=90, optimize=True)
                compressed_image_data = compressed_image.getvalue()

                front_id_text = self.get_ocr_results(compressed_image_data, country='SDN')
                front_id_text_desc = front_id_text[0].description
                logging.info(f'----------------Time taken for vision front: {time.time() - st} seconds\n')

                st = time.time()
                try:
                    translated_id_text = self.translator.translate(front_id_text_desc, src='ar', dest='en').text
                except:
                    logging.info(f'\n--------------Fallback for translation keyword matching')
                    from deep_translator import GoogleTranslator
                    translated_id_text = GoogleTranslator('ar', 'en').translate(front_id_text_desc)
                logging.info(f'----------------Time taken for ar-en translation front: {time.time() - st} seconds\n')

                combined_pattern = r'(Republic of the Sudan|Republic of Sudan|ID Card|SDN)'
                match = re.search(combined_pattern, translated_id_text, re.IGNORECASE)

                if not match:
                    front_data["error"] = "not_front_id"
                    return front_data

                image = np.array(processed_front_id)

                # blur_test = is_image_blur(image)
                # if blur_test == True:
                #     print(f"Front ID Document is blurry, marking as covered photo")
                #     front_data['error'] = 'covered_photo'
                #     return front_data

                ## TODO: doc_on_pp for SDN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                ## no logo detection for SDN ID's
                logo_result = 'clear'
                template_result = 'clear'
                ## TODO: template matching for SDN ID's
                # template_result = detect_logo(self.client, compressed_image_data, country, compare_type='template', side='front')
                ## TODO: tampering result for SDN ID's - pending tampered samples
                # tampered_result_front = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(front_id, "utf-8"))))))

                st = time.time()
                front_data_fields = sdn_front_id_extraction(self.client, front_id_text_desc, compressed_image_data,
                                                            front_id_text, compressed_image)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction front: {time.time() - st} seconds\n')
                # Check age based on DOB
                try:
                    dob = front_data_fields.get('dob', '')
                    if dob:
                        try:
                            dob_date = datetime.strptime(dob, "%Y/%m/%d")
                        except:
                            try:
                                dob_date = datetime.strptime(dob, "%Y-%m-%d")
                            except:
                                try:
                                    dob_date = datetime.strptime(dob, "%d/%m/%Y")
                                except:
                                    dob_date = None

                        if dob_date:
                            current_date = datetime.now()
                            age = current_date.year - dob_date.year - (
                                        (current_date.month, current_date.day) < (dob_date.month, dob_date.day))
                            if age < 18:
                                front_data['error'] = 'under_age'
                                return front_data
                except:
                    pass

                st = time.time()
                screenshot_result = detect_screenshot(self.client, front_id)
                # photo_on_screen_result = detect_photo_on_screen(self.client, image)
                photo_on_screen_result = 'clear'
                front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)
                logging.info(
                    f'----------------Time taken for fraud detection attributes front: {time.time() - st} seconds\n')

                # front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)
                st = time.time()
                front_face_locations, front_face_encodings = load_and_process_image_deepface(front_id, country='SDN')
                logging.info(f'----------------Time taken for face extraction front: {time.time() - st} seconds\n')

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                # print(f"TAMPERING: {tampered_result_front}")

                front_data_temp = {
                    'front_extracted_data': front_id_text_desc,
                    'translated_front_id_text': translated_id_text,
                    'front_coloured': True,
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_logo_result': logo_result,
                    'front_template_result': template_result,
                    # 'front_tampered_result': tampered_result_front,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': front_blurred,
                    'front_glare': front_glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str
                }

                front_data_fields.update(front_data_temp)
                front_data.update(front_data_fields)

                required_keys = ["front_face_locations","id_number", "front_face_encodings", "full_name", "dob"]
                empty_string_keys = [key for key, value in front_data.items() if key in required_keys and value == '']

                if empty_string_keys:
                    front_data['error'] = 'missing_key_fields'

            
            except Exception as e:
                front_data['error'] = 'Something went wrong'
                print(f"-------------->> Something went wrong error trace:: {e}")
                front_data['error_details'] = e

            # try:
            #     list_1 = front_data['name_ar'].split(" ")
            #     filtered_names = [name for name in list_1 if len(name) > 1]
            #     front_data['first_name_ar'] = filtered_names[0]
            #     front_data['last_name_ar'] = filtered_names[3]
            #     front_data['middle_name_ar'] = filtered_names[1]+' '+filtered_names[2]
            # except Exception as e:
            #     front_data['first_name_ar'] = ''
            #     front_data['last_name_ar'] = ''
            #     front_data['middle_name_ar'] = ''

            try:
                list_1 = front_data['name_ar'].split(" ")
                filtered_names = [name for name in list_1 if len(name) > 1]
                if len(filtered_names) == 4:
                    front_data['first_name_ar'] = filtered_names[0]
                    front_data['last_name_ar'] = filtered_names[3]
                    front_data['middle_name_ar'] = filtered_names[1] + ' ' + filtered_names[2]
                elif len(filtered_names) == 5:
                    front_data['first_name_ar'] = filtered_names[0]
                    front_data['last_name_ar'] = filtered_names[4]
                    front_data['middle_name_ar'] = filtered_names[1] + ' ' + filtered_names[2] + ' ' + filtered_names[3]
                elif len(filtered_names) == 6:
                    front_data['first_name_ar'] = filtered_names[0]
                    front_data['last_name_ar'] = filtered_names[5]
                    front_data['middle_name_ar'] = filtered_names[1] + ' ' + filtered_names[2] + ' ' + filtered_names[
                        3] + ' ' + filtered_names[4]
                elif len(filtered_names) == 7:
                    front_data['first_name_ar'] = filtered_names[0]
                    front_data['last_name_ar'] = filtered_names[6]
                    front_data['middle_name_ar'] = filtered_names[1] + ' ' + filtered_names[2] + ' ' + filtered_names[
                        3] + ' ' + filtered_names[4] + ' ' + filtered_names[5]
                else:
                    front_data['first_name_ar'] = ''
                    front_data['last_name_ar'] = ''
                    front_data['middle_name_ar'] = ''

            except Exception as e:
                front_data['first_name_ar'] = ''
                front_data['last_name_ar'] = ''
                front_data['middle_name_ar'] = ''

            return front_data

    def extract_back_id_info(self, back_id, country, nationality):
        if country == 'UAE':
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.common import remove_special_characters1, remove_special_characters2, func_id_number, \
                convert_date_format, detect_id_card_uae, convert_gender, count_digits_after_pattern, \
                remove_special_characters_mrz2, validate_string
            from idvpackage.ocr_utils import is_valid_and_not_expired
            import pytesseract
            import sys
            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                processed_back_id = self.image_conversion(back_id)
                id_infos = self.get_ocr_results(processed_back_id)
                text = id_infos[0].description
                pattern4 = r'(Card Number|<<|ILARE|IDARE|(?=.*\bOccupation\b).*|(?=.*\bEmployer\b).*|(?=.*\bIssuing Place\b).*)'
                k = re.search(pattern4, text.replace(" ", ""), re.IGNORECASE)

                if not k:
                    back_data["error"] = "not_back_id"
                    return back_data

                original_text = text

                # print('this is original text:',original_text)

                patterns = {
                    'id_number': (r'(?:ILARE|IDARE)\s*([\d\s]+)',
                                  lambda match: match.group(0).replace(" ", "")[15:30] if match else ''),
                    'card_number': (r'(?:ILARE|IDARE)(\d{1,9})', lambda match: match.group(1) if match else ''),
                    'nationality': (r'([A-Z]+)<<', lambda match: match.group(1) if match else ''),
                    'gender': (r'(?<=\d)[A-Z](?=\d)', lambda match: match.group(0) if match else ''),
                    'dob': (r'(\d+)[MF]', lambda match: self.convert_dob(match.group(1)) if match else ''),
                    'expiry_date': (
                    r'[MF](\d+)', lambda match: self.convert_expiry_date(match.group(1)) if match else ''),
                    'name': (r'(.*[A-Za-z]+<[<]+[A-Za-z].*)',
                             lambda match: match.group(0).replace('<', ' ').strip() if match else ''),
                    # 'first_name': (r'<<([^<]+)', lambda match: match.group(0).replace("<", "") if match else ''),
                    # 'last_name': (r'([^<]+)(?=<<)', lambda match: match.group(0).replace("<", "") if match else ''),
                    # 'occupation': (r'Occupation:\s*([-\w\s.]+)', lambda match: match.group(1).strip().split('\n', 1)[0] if match else '', re.IGNORECASE),
                    # 'employer': (r'Employer:\s*([\w\s.]+)', lambda match: match.group(1).strip().split('\n', 1)[0] if match else '', re.IGNORECASE),
                    'place_of_issuance': (r'Issuing Place:\s*([\w\s.]+)',
                                      lambda match: match.group(1).strip().split('\n', 1)[0] if match else '',
                                      re.IGNORECASE),
                    'issuing_place': (r'Issuing Place:\s*([\w\s.]+)',
                                      lambda match: match.group(1).strip().split('\n', 1)[0] if match else '',
                                      re.IGNORECASE)
                }

                mrz_pattern = r'(ILAR.*\n*.*\n*.*\n*.*|IDAR.*\n*.*\n*.*\n*.*)'

                try:
                    mrz = re.findall(mrz_pattern, original_text.replace(" ", "").strip(), re.MULTILINE)
                    mrz_list = mrz[0].replace(" ", "").split("\n", 3)
                    mrz1 = mrz_list[0]

                except:
                    mrz1 = ''

                #### EXTRACT mrz2

                # try:
                #     mrz2=mrz_list[1]
                # except:
                #     mrz2=''
                try:

                    mrz2 = \
                    [s for s in [remove_special_characters1(ele).replace(' ', '') for ele in original_text.split('\n')]
                     if len(re.findall(r'<', s)) >= 2 and not (re.fullmatch(r'[A-Za-z<]+', s))][0]

                except:

                    mrz2 = ''
                ### Extract mrz3
                try:
                    mrz3 = \
                    [s for s in [remove_special_characters1(ele).replace(' ', '') for ele in original_text.split('\n')]
                     if len(re.findall(r'<', s)) >= 2 and re.fullmatch(r'[A-Za-z<]+', s)][0]
                    back_data['name'] = remove_special_characters2(mrz3[0]).strip()
                    back_data['last_name'] = remove_special_characters2(
                        re.search(r'([^<]+)(?=<<)', mrz3).group(0)).strip() if re.search(r'([^<]+)(?=<<)', mrz3) else ''
                    back_data['first_name'] = remove_special_characters2(
                        re.search(r'<<([^<]+)', mrz3).group(0)).strip() if re.search(r'<<([^<]+)', mrz3) else ''

                except:
                    mrz3, back_data['name'], back_data['last_name'], back_data['first_name'] = '', '', '', ''

                pattern = r'ARE\d{25}'

                extracted_data_tesseract = ''

                if not re.search(pattern, original_text.replace(' ', '')):

                    img = self.image_conversion(back_id)
                    # Decode the base64 string
                    image_data = base64.b64decode(back_id)
                    # Convert to an image
                    with Image.open(io.BytesIO(image_data)) as image:
                        # Use PyTesseract to do OCR on the image
                        try:
                            extracted_data_tesseract = pytesseract.image_to_string(image)
                            match = re.search(pattern, extracted_data_tesseract.replace(' ', ''))
                            mrz1 = (mrz1[:2] + match[0]).strip()
                        except:
                            pass

                mrz1_keys = ['id_number', 'card_number']
                mrz2_keys = ['nationality', 'gender', 'dob', 'expiry_date']
                # mrz3_keys = [ 'first_name', 'last_name']

                for key, value in patterns.items():
                    pattern = value[0]
                    transform_func = value[1]
                    flags = value[2] if len(value) > 2 else 0

                    text = original_text
                    if key in mrz1_keys:
                        text = mrz1
                    if key in mrz2_keys:
                        text = mrz2
                    # if key in mrz3_keys:
                    #     text = mrz3

                    match = re.search(pattern, text, flags)
                    back_data[key] = transform_func(match) if match else ''

                back_data.update({
                    'mrz1': mrz1,
                    'mrz2': mrz2,
                    'mrz3': mrz3
                })

                # print("ths is gender :",back_data['gender'])

                ## extracting occupation and employer
                occ_word = 'Occupation'
                occ = ''
                emp_word = 'Employer'
                emp = ''
                try:
                    lines = original_text.split('\n')
                    for line in lines:
                        if occ_word in line:
                            start_index = line.find(occ_word)
                            end_index = start_index + len(occ_word)
                            occ = line[end_index:]
                            occ = self.clean_string(occ)

                        if emp_word in line:
                            start_index1 = line.find(emp_word)
                            end_index1 = start_index1 + len(emp_word)
                            emp = line[end_index1:]
                            emp = self.clean_string(emp)
                except:
                    occ = ''
                    emp = ''

                family_sponsor_word = 'Family Sponsor'
                family_sponsor = ''
                try:
                    lines = original_text.split('\n')
                    for line in lines:
                        if family_sponsor_word in line:
                            start_index = line.find(family_sponsor_word)
                            end_index = start_index + len(family_sponsor_word)
                            family_sponsor = line[end_index:]
                            family_sponsor = self.clean_string(family_sponsor)
                except:
                    family_sponsor = ''

                ### new rule
                if len(str(back_data['id_number'])) != 15:
                    back_data['id_number'] = ''

                ### new rule
                if len(str(back_data['card_number'])) != 9:
                    back_data['card_number'] = ''

                current_module = sys.modules[__name__]

                for key in ['dob', 'expiry_date', 'card_number', 'name', 'nationality']:
                    # if not back_data[key] and key not in ['occupation', 'employer', 'first_name', 'last_name', 'issuing_place', 'error']:

                    if not back_data[key]:
                        transform_func_new = getattr(current_module, f'func_{key}')
                        back_data[key] = transform_func_new(original_text)

                for key in ['dob', 'expiry_date']:
                    if not back_data[key]:
                        transform_func_new = getattr(current_module, f'find_{key}')
                        back_data[key] = transform_func_new(original_text, back_data['mrz2'])

                if not back_data['id_number']:
                    back_data['id_number'] = func_id_number(original_text, back_data['dob'])

                if is_valid_and_not_expired(back_data.get('expiry_date'), country) == 'consider':
                    back_data['error'] = 'expired_document'

                ### convert the date format
                if back_data['dob']:
                    try:
                        back_data['dob'] = convert_date_format(back_data['dob'])
                    except:
                        back_data['dob'] = ''

                if back_data['expiry_date']:
                    try:
                        back_data['expiry_date'] = convert_date_format(back_data['expiry_date'])
                    except:
                        back_data['expiry_date'] = ''

                img = self.image_conversion(back_id)
                if hasattr(img, '_getexif'):
                    orientation = 0x0112
                    exif = img._getexif()
                    if exif is not None and orientation in exif:
                        orientation = exif[orientation]
                        rotations = {
                            3: Image.ROTATE_180,
                            6: Image.ROTATE_270,
                            8: Image.ROTATE_90
                        }
                        if orientation in rotations:
                            img = img.transpose(rotations[orientation])

                image = np.array(img)
                pil_image = Image.fromarray(image)

                with io.BytesIO() as output:
                    pil_image.save(output, format="PNG")
                    image_data = output.getvalue()

                tampered_result, third_part_text = detect_id_card_uae(self.client, image_data, id_infos, part='third')
                back_data['back_tampered_result'] = tampered_result

                ### layer of gender extraction
                if not back_data['gender']:
                    # print(f"TEXT: {third_part_text}")
                    mrz2 = re.search(r'\b\d{7}.*?(?:<<\d|<<\n)', third_part_text)
                    mrz2 = mrz2.group(0) if mrz2 else None

                    gender_ptrn = r'\d{7}([A-Z])\d{4,}'
                    if mrz2:
                        gender_match = re.search(gender_ptrn, mrz2)
                        gender = gender_match.group(1)
                        back_data['gender'] = gender
                    else:
                        gender_match = re.search(gender_ptrn, third_part_text)
                        gender = gender_match.group(0)
                        back_data['gender'] = gender

                ### another layer of gender extraction + formatting
                if not back_data['gender']:
                    extract_no_space = original_text.replace(' ', '')
                    try:
                        pattern = r'\sM|F'
                        m = re.search(pattern, original_text)
                        back_data['gender'] = m.group(0)[-1]
                    except:
                        pattern = r'\d{3}(?:M|F)\d'
                        m = re.findall(pattern, extract_no_space)
                        if len(m) != 0:
                            back_data['gender'] = m[0][3:4]
                        else:
                            back_data['gender'] = ''

                ### if still no gender then one more layer of gender extraction + formatting
                if not back_data['gender']:

                    if not extracted_data_tesseract:
                        # Decode the base64 string
                        image_data = base64.b64decode(back_id)
                        # Convert to an image
                        with Image.open(io.BytesIO(image_data)) as image:
                            # Use PyTesseract to do OCR on the image
                            extracted_data_tesseract = pytesseract.image_to_string(image)

                    mrzs_tesseract = [s for s in [ele.replace(' ', '') for ele in extracted_data_tesseract.split('\n')]
                                      if re.search(r'<<{2,}', s)]
                    mrz3_tesseract = [s for s in mrzs_tesseract if re.fullmatch(r'[A-Za-z<]+', s)]

                    if mrzs_tesseract and mrz3_tesseract:
                        mrz2_tesseract = list(set(mrzs_tesseract) - set(mrz3_tesseract))[0]
                        gender = mrz2_tesseract[7].lower()
                        if gender in ['f', 'm']:
                            back_data['gender'] = convert_gender(gender)
                else:
                    back_data['gender'] = convert_gender(back_data['gender'])

                if back_data['name']:
                    back_data['name'] = re.sub('[^a-zA-Z]', ' ', back_data['name']).strip()

                ### new rule
                if len(str(back_data['id_number'])) != 15:
                    back_data['id_number'] = ''

                ### new rule
                if len(str(back_data['card_number'])) != 9:
                    back_data['card_number'] = ''

                count = count_digits_after_pattern(mrz2)

                if count > 1:
                    mrz2 = mrz2[:-int(count - 1)]

                ## fix a special case where O comes as zero

                if re.sub(r'O([A-Z]{3})', r'0\1', mrz2):
                    mrz2 = re.sub(r'O([A-Z]{3})', r'0\1', mrz2)

                if not validate_string(remove_special_characters_mrz2(mrz2)):
                    if (back_data['mrz2']) and (back_data['gender']) and (back_data['mrz2'][-1].isdigit()):
                        try:
                            # Regular expression to extract two sequences of 7 digits
                            matches = re.findall(r'\d{7}', back_data['mrz2'])

                            # Check if we found two sequences
                            extracted_digits = matches[:2] if len(matches) >= 2 else None

                            if extracted_digits:
                                mrz2 = extracted_digits[0] + back_data['gender'][:1] + extracted_digits[
                                    -1] + '<<<<<<<<<<<' + back_data['mrz2'][-1]
                        except:
                            mrz2 = ''
                    else:
                        mrz2 = ''

                if len(back_data['nationality']) > 3:
                    back_data['nationality'] = back_data['nationality'][-3:]

                ### check if teh extracted nationality is valid
                valid_nationality_result = self.check_nationality_in_iso_list(back_data.get('nationality'))

                img = self.image_conversion(back_id)
                image = np.array(img)
                # pil_image = Image.fromarray(image)

                doc_on_pp_result = document_on_printed_paper(image)
                screenshot_result = detect_screenshot(self.client, back_id)
                photo_on_screen_result = detect_photo_on_screen(self.client, back_id)
                back_blurred, back_glare = self.get_blurred_and_glared_for_doc(image)
                # print(f"blurred, glare: {back_blurred, back_glare}")

                back_data_update = {
                    'valid_nationality': valid_nationality_result,
                    'back_extracted_data': original_text,
                    'back_coloured': True,
                    'mrz': mrz,
                    'mrz1': mrz1,
                    'mrz2': mrz2,
                    'mrz3': mrz3,
                    'occupation': occ,
                    'employer': emp,
                    'family_sponsor': family_sponsor,
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'back_blurred': back_blurred,
                    'back_glare': back_glare
                }

                back_data.update(back_data_update)
                back_data['issuing_country']='ARE'

                non_optional_keys = ["id_number", "card_number", "name", "dob", "expiry_date", "gender", "nationality",
                                     "mrz", "mrz1", "mrz2", "mrz3"]
                empty_string_keys = [key for key, value in back_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    back_data['error'] = 'covered_photo'


            except Exception as e:
                back_data['error'] = 'bad_image'
                back_data['error_details'] = e

            return back_data

        if country == 'IRQ':
            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.iraq_id_extraction import iraq_back_id_extraction, update_family_number_cases, \
                extract_family_number

            try:
                processed_back_id = self.image_conversion(back_id)

                st = time.time()
                compressed_image = BytesIO()
                processed_back_id.save(compressed_image, format="JPEG", quality=75, optimize=True)
                compressed_image_data = compressed_image.getvalue()

                id_infos = self.get_ocr_results(compressed_image_data, country='IRQ', side='front')
                text = id_infos[0].description
                logging.info(f'----------------Time taken for vision: {time.time() - st} seconds\n')

                # print(f"\nORIGINAL TEXT: {text}\n")
                # translated_id_text = self.translator.translate(text, from_lang='ar', to_lang='en').text
                try:
                    translated_id_text = self.translator.translate(text, src='ar', dest='en').text
                except Exception as e:
                    logging.info(f'--------------Fallback for translation keyword matching\n')
                    from deep_translator import GoogleTranslator
                    translated_id_text = GoogleTranslator('ar', 'en').translate(text)

                # print(f"\nTRANS: {translated_id_text}\n")

                pattern4 = r'(Register|Signature|IDIRQ|Family number|The Directorate of Nationality|IDIR)'
                k = re.search(pattern4, translated_id_text, re.IGNORECASE)

                if not k:
                    k1 = re.search(pattern4, text, re.IGNORECASE)
                    if not k1:
                        back_data["error"] = "not_back_id"
                        return back_data

                original_text = text

                # print('this is original text:',original_text)
                image = np.array(processed_back_id)
                # pil_image = Image.fromarray(image)

                # with io.BytesIO() as output:
                #     pil_image.save(output, format="PNG")
                #     image_data = output.getvalue()

                # template_result='clear'
                # tampered_result_back = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(back_id, "utf-8"))))))

                # image_format = 'jpg'
                image_format = self.detect_image_format(back_id)

                st = time.time()
                back_extraction_result = iraq_back_id_extraction(self.client, compressed_image_data, id_infos,
                                                                 original_text, image_format)
                logging.info(
                    f'--------------Time taken for back id data formatting final extraction: {time.time() - st}\n')

                error = ""
                expiry_date = back_extraction_result.get('expiry_date', '')

                if expiry_date:
                    try:
                        dt_obj = datetime.strptime(expiry_date, '%d/%m/%Y')
                        tomorrow = datetime.today() + timedelta(days=1)
                        if dt_obj < tomorrow:
                            back_data['error'] = 'expired_id'
                    except:
                        pass

                back_data.update(back_extraction_result)
                valid_nationality_result = self.check_nationality_in_iso_list(back_data.get('nationality'))
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                screenshot_result = detect_screenshot(self.client, back_id)
                photo_on_screen_result = detect_photo_on_screen(self.client, back_id)
                back_blurred, back_glare = self.get_blurred_and_glared_for_doc(image)

                back_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'valid_nationality': valid_nationality_result,
                    'back_extracted_data': original_text,
                    'translated_back_id_text': translated_id_text,
                    'back_coloured': True,
                    'occupation': '',
                    'employer': '',
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'back_blurred': back_blurred,
                    'back_glare': back_glare
                }

                back_data.update(back_data_update)

                non_optional_keys = ["id_number", "card_number", "dob", "expiry_date", "nationality"]
                empty_string_keys = [key for key, value in back_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    back_data['error'] = 'covered_photo'

            except Exception as e:
                back_data['error'] = 'bad_image'
                back_data['error_details'] = e

            try:
                family_num_dict = extract_family_number(text)
                family_num_dict = update_family_number_cases(family_num_dict, text)

                back_data['family_number_en'] = family_num_dict['family_number']
                back_data['family_number'] = family_num_dict['family_number']
            except Exception as e:
                back_data['family_number_en'] = None
                back_data['family_number'] = None

                print('error in family number:', e)

            return back_data

        if country == 'QAT':
            from idvpackage.qatar_id_extraction import qatar_back_id_extraction

            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            # is_colored2 = self.is_colored(back_id)
            # if is_colored2:
            try:
                processed_back_id = self.image_conversion(back_id)

                compressed_image = BytesIO()
                processed_back_id.save(compressed_image, format="JPEG", quality=80, optimize=True)
                compressed_image_data = compressed_image.getvalue()

                id_infos = self.get_ocr_results(compressed_image_data, country='QAT')

                text = id_infos[0].description
                # print(f'Original text: {text}')

                # translated_id_text = self.translator.translate(text, from_lang='ar', to_lang='en').text
                pattern4 = r'(Director General of the General Department|Directorate of Passports|Passport number|Serial)'
                k = re.search(pattern4, text, re.IGNORECASE)
                # print('this is translated_id_text',translated_id_text)
                if not k:
                    back_data["error"] = "not_back_id"

                    return back_data

                original_text = text

                # print('this is original text:',original_text)

                ## TODO: template matching for Qatar ID's
                image_data = base64.b64decode(back_id)

                back_extraction_result = qatar_back_id_extraction(original_text)
                back_data.update(back_extraction_result)

                # image = np.array(processed_back_id)

                back_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'back_extracted_data': original_text,
                    'back_coloured': True,
                    'doc_on_pp': 'clear',
                    'screenshot_result': 'clear',
                    'photo_on_screen_result': 'clear',
                    'back_blurred': 'clear',
                    'back_glare': 'clear'
                }

                back_data.update(back_data_update)

            # non_optional_keys = ["card_number"]
            # empty_string_keys = [key for key, value in back_data.items() if key in non_optional_keys and value == '']

            # if empty_string_keys:
            #     back_data['error'] = 'covered_photo'

            except Exception as e:
                back_data['error'] = 'bad_image'
                back_data['error_details'] = e

                # back_data['error_details'] = e
            # else:
            #     back_data['error'] = 'bad_image'

            return back_data

        if country == 'LBN':
            from idvpackage.ocr_utils import detect_logo, detect_photo_on_screen, detect_screenshot, \
                document_on_printed_paper
            from idvpackage.lebanon_id_extraction import lebanon_back_id_extraction

            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                st = time.time()
                processed_back_id = self.image_conversion(back_id)
                logging.info(f'----------------Time taken for image conversion back: {time.time() - st} seconds\n')

                st = time.time()
                compressed_image = BytesIO()
                processed_back_id.save(compressed_image, format="JPEG", quality=100, optimize=True)
                compressed_image_data = compressed_image.getvalue()
                id_infos = self.get_ocr_results(compressed_image_data, country='LBN')
                text = id_infos[0].description
                logging.info(f'----------------Time taken for vision back: {time.time() - st} seconds\n')

                try:
                    translated_id_text = self.translator.translate(text, src='ar', dest='en').text
                except:
                    logging.info(f'\n--------------Fallback for translation keyword matching')
                    from deep_translator import GoogleTranslator
                    translated_id_text = GoogleTranslator('ar', 'en').translate(text)
                logging.info(f'----------------Time taken for ar-en translation back: {time.time() - st} seconds\n')

                pattern4 = r'(Marital status|Family|Release|Sex|Register number)'
                k = re.search(pattern4, translated_id_text, re.IGNORECASE)

                if not k:
                    back_data["error"] = "not_back_id"
                    return back_data

                ## TODO: template matching for Lebanon ID's
                # image_data = base64.b64decode(back_id)
                # template_result = detect_logo(self.client, image_data, country, compare_type='template', side='back')
                # if template_result == 'consider':
                #     back_data["error"] = "not_back_id"
                #     return back_data

                ## TODO: tampering result for Lebanon ID's
                # tampered_result_back = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(back_id, "utf-8"))))))

                st = time.time()
                back_extraction_result = lebanon_back_id_extraction(text)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction back: {time.time() - st} seconds\n')

                back_data.update(back_extraction_result)
                image = np.array(processed_back_id)

                st = time.time()
                ## TODO: doc_on_pp and detect_photo_on_screen for LBN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                screenshot_result = detect_screenshot(self.client, back_id)
                # photo_on_screen_result = detect_photo_on_screen(self.client, image)
                photo_on_screen_result = 'clear'
                back_blurred, back_glare = self.get_blurred_and_glared_for_doc(image)
                logging.info(
                    f'----------------Time taken for fraud detection attributes back: {time.time() - st} seconds\n')

                back_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'back_extracted_data': text,
                    'translated_back_id_text': translated_id_text,
                    'back_coloured': True,
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'back_blurred': back_blurred,
                    'back_glare': back_glare
                }

                back_data.update(back_data_update)

                if not back_data.get('gender') or not back_data.get('issue_date') or not back_data.get('card_number'):
                    back_data['error'] = 'covered_photo'

                non_optional_keys = ["gender", "issue_date"]
                empty_string_keys = [key for key, value in back_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    back_data['error'] = 'covered_photo'

            except Exception as e:
                back_data['error'] = 'bad_image'
                back_data['error_details'] = e

            return back_data

        if country == 'SDN':
            from idvpackage.ocr_utils import detect_logo, detect_photo_on_screen, detect_screenshot, \
                document_on_printed_paper
            from idvpackage.sudan_id_extraction import sdn_back_id_extraction
            from idvpackage.blur_detection import is_image_blur

            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            try:
                st = time.time()
                processed_back_id = self.image_conversion(back_id)
                logging.info(f'----------------Time taken for image conversion back: {time.time() - st} seconds\n')

                st = time.time()
                compressed_image = BytesIO()
                processed_back_id.save(compressed_image, format="JPEG", quality=90, optimize=True)
                compressed_image_data = compressed_image.getvalue()
                id_infos = self.get_ocr_results(compressed_image_data, country='SDN')
                text = id_infos[0].description
                logging.info(f'----------------Time taken for vision back: {time.time() - st} seconds\n')

                try:
                    translated_id_text = self.translator.translate(text, src='ar', dest='en').text
                except:
                    logging.info(f'\n--------------Fallback for translation keyword matching')
                    from deep_translator import GoogleTranslator
                    translated_id_text = GoogleTranslator('ar', 'en').translate(text)
                logging.info(f'----------------Time taken for ar-en translation back: {time.time() - st} seconds\n')

                pattern4 = r'(IDSDN|Name)'
                k = re.search(pattern4, translated_id_text, re.IGNORECASE)

                if not k:
                    back_data["error"] = "not_back_id"
                    return back_data
                
                image = np.array(processed_back_id)
                # blur_test = is_image_blur(image)
                # if blur_test == True:
                #     print(f"Back ID Document is blurry, marking as covered photo")
                #     back_data['error'] = 'covered_photo'
                #     return back_data

                ## TODO: template matching for Lebanon ID's
                # image_data = base64.b64decode(back_id)
                # template_result = detect_logo(self.client, image_data, country, compare_type='template', side='back')
                # if template_result == 'consider':
                #     back_data["error"] = "not_back_id"
                #     return back_data

                ## TODO: tampering result for Lebanon ID's
                # tampered_result_back = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(back_id, "utf-8"))))))

                st = time.time()
                back_extraction_result = sdn_back_id_extraction(text)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction back: {time.time() - st} seconds\n')

                if back_extraction_result.get('expiry_date'):
                    try:
                        expiry_date = back_extraction_result['expiry_date']
                        expiry_date = datetime.strptime(expiry_date, "%d/%m/%Y")
                        current_date = datetime.now()

                        if expiry_date < current_date:
                            back_data['error'] = 'expired_id'
                            return back_data
                    except:
                        pass

                if back_extraction_result.get('dob_back'):
                    try:
                        dob_date = back_extraction_result['dob_back']
                        dob_date = datetime.strptime(dob_date, "%d/%m/%Y")
                        current_date = datetime.now()
                        if dob_date > current_date:
                            back_data['error'] = 'expired_id'
                            return back_data
                    except:
                        pass

                back_data.update(back_extraction_result)

                if back_data.get('issue_date'):
                    back_data['issuance_date'] = back_data['issue_date']

                image = np.array(processed_back_id)

                st = time.time()
                ## TODO: doc_on_pp and detect_photo_on_screen for LBN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                screenshot_result = detect_screenshot(self.client, back_id)
                # photo_on_screen_result = detect_photo_on_screen(self.client, image)
                photo_on_screen_result = 'clear'
                back_blurred, back_glare = self.get_blurred_and_glared_for_doc(image)
                logging.info(
                    f'----------------Time taken for fraud detection attributes back: {time.time() - st} seconds\n')

                back_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'back_extracted_data': text,
                    'translated_back_id_text': translated_id_text,
                    'back_coloured': True,
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'back_blurred': back_blurred,
                    'back_glare': back_glare
                }

                back_data.update(back_data_update)

                non_optional_keys = ["gender", "expiry_date"]
                empty_string_keys = [key for key, value in back_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    back_data['error'] = 'missing_key_fields'

            except Exception as e:
                back_data['error'] = 'Something went wrong'
                print(f"-------------->> Something went wrong error trace:: {e}")
                back_data['error_details'] = e


            return back_data

        
    def exract_passport_info(self, passport, country, nationality, step_data=None):
        if (nationality and nationality == 'RUS') or (not nationality and country == 'RUS'):
            logging.info("-------------Working on RUS Passport \n")
            processed_passport = self.image_conversion(passport)
            passport_text = self.get_ocr_results(processed_passport)
            passport_text = passport_text[0].description

            passport_details = {}

            patterns = {
                'passport_given_name': (r'Имя Given names\n(.*?)/',
                                        lambda match: self.translator.translate(match.group(1), src='ru',
                                                                                dest='en').text if match else ''),
                'passport_surname': (r'RUS(.*?)<<(.*?)<.*', lambda match: match.group(1) if match else ''),
                'passport_number': (r"(\d{7})", lambda match: match.group(1) if match else ''),
                'passport_date_of_birth': (
                r'(\d+)[MF]', lambda match: self.convert_dob(match.group(1)) if match else ''),
                'passport_date_of_expiry': (
                r'[MF](\d+)', lambda match: self.convert_expiry_date(match.group(1)) if match else ''),
                'passport_gender': (r'(\d)([A-Za-z])(\d)', lambda match: match.group(2) if match else '')
            }

            mrz1_pattern = r'([A-Z<]+)<<([A-Z<]+)<<([\dA-Z<]+)'
            mrz2_pattern = r'(\d{10}[A-Z]{3}\d{7}[\dA-Z<]+)'

            mrz1_matches = re.findall(mrz1_pattern, passport_text)
            mrz2_matches = re.findall(mrz2_pattern, passport_text)

            if mrz1_matches:
                mrz1 = ' '.join(mrz1_matches[0])
            else:
                mrz1 = ''

            if mrz2_matches:
                mrz2 = mrz2_matches[0]
            else:
                mrz2 = ''

            mrz1_keys = ['passport_surname']
            mrz2_keys = ['passport_date_of_birth', 'passport_date_of_expiry', 'passport_gender']

            for key, value in patterns.items():
                pattern = value[0]
                transform_func = value[1]

                text = passport_text
                if key in mrz1_keys:
                    text = mrz1
                if key in mrz2_keys:
                    text = mrz2

                match = re.search(pattern, text)
                passport_details[key] = transform_func(match) if match else ''

            passport_details['doc_type'] = 'passport'
            passport_details['nationality_received'] = nationality

            return passport_details

        if (nationality and nationality == 'IRQ') or (not nationality and country == 'IRQ'):
            logging.info("-------------Working on IRQ Passport \n")
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.iraq_passport_extraction import iraq_passport_extraction, extract_mother_name_and_surname
            from idvpackage.common import load_and_process_image_deepface

            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }

            try:
                processed_passport = self.image_conversion(passport)
                id_infos = self.get_ocr_results(processed_passport)
                passport_text = id_infos[0].description
                print(passport_text)
                pattern4 = r'(Republic of Iraq|Iraq)'  # |Passport
                k = re.search(pattern4, passport_text, re.IGNORECASE)

                if not k:
                    passport_data["error"] = "not_passport"
                    return passport_data

                original_text = passport_text

                passport_details = iraq_passport_extraction(passport_text)

                passport_details['id_number'] = passport_details.get('passport_number',
                                                                     passport_details.get('passport_number_mrz'))
                if passport_details.get('passport_number_mrz') and passport_details['id_number'] != passport_details[
                    'passport_number_mrz']:
                    passport_details['id_number'] = passport_details['passport_number_mrz']

                if not passport_details.get('passport_date_of_birth_generic') and passport_details.get('dob_mrz'):
                    passport_details['dob'] = passport_details['dob_mrz']
                else:
                    passport_details['dob'] = passport_details['passport_date_of_birth_generic']

                if (not passport_details.get('full_name') and passport_details.get('full_name_generic')) or (
                        len(passport_details.get('full_name')) < len(passport_details.get('full_name_generic'))):
                    if passport_details['full_name_generic'].startswith('IRQ'):
                        passport_details['full_name'] = passport_details['full_name_generic'][3:].strip()
                    else:
                        passport_details['full_name'] = passport_details['full_name_generic']

                # if len(passport_details.get('full_name')) < len(passport_details.get('full_name_generic')):
                #     passport_details['full_name'] = passport_details['full_name_generic']

                if not passport_details.get('last_name') and passport_details.get('surname_generic'):
                    if passport_details['surname_generic'].startswith('IRQ'):
                        passport_details['last_name'] = passport_details['surname_generic'][3:].strip()
                    else:
                        passport_details['last_name'] = passport_details['surname_generic']

                if not passport_details.get('passport_date_of_expiry_generic') and passport_details.get(
                        'expiry_date_mrz'):
                    passport_details['expiry_date'] = passport_details['expiry_date_mrz']
                else:
                    passport_details['expiry_date'] = passport_details['passport_date_of_expiry_generic']

                keys_to_delete = ['expiry_date_mrz', 'passport_date_of_expiry_generic', 'dob_mrz',
                                  'passport_date_of_birth_generic',
                                  'passport_number', 'passport_number_mrz', 'full_name_generic', 'surname_generic']

                for key in keys_to_delete:
                    if key in passport_details.keys():
                        del passport_details[key]

                passport_data.update(passport_details)

                image = np.array(processed_passport)
                doc_on_pp_result = document_on_printed_paper(image)
                screenshot_result = detect_screenshot(self.client, passport)
                photo_on_screen_result = detect_photo_on_screen(self.client, passport)
                blurred, glare = self.get_blurred_and_glared_for_doc(image)
                valid_nationality_result = self.check_nationality_in_iso_list(passport_details.get('nationality'))

                front_face_locations, front_face_encodings = load_and_process_image_deepface(passport)

                if step_data:
                    try:
                        print(f"Matching face from Passport with National ID")
                        national_id_front_face_locations = step_data.get("front_face_locations")
                        national_id_front_face_encodings = json.loads(step_data.get("front_face_encodings"))
                        national_id_front_face_encodings = np.array(national_id_front_face_encodings[0], dtype=np.float32)
                        similarity = self.calculate_similarity(national_id_front_face_encodings, front_face_encodings[0])
                        passport_data["similarity_score"] = similarity
                        if similarity <= 0.65:
                            passport_data["error"] = 'face_mismatch'
                    except Exception as e:
                        passport_data["error"] = 'National ID Image Not Found'
                        passport_data["error_details"] = e

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                passport_data_update = {
                        # 'back_tampered_result': tampered_result_back,
                        'passport_data': original_text,
                        'front_coloured': True,
                        'back_coloured': True,
                        'front_logo_result': 'clear',
                        'front_doc_on_pp': doc_on_pp_result,
                        'front_screenshot_result': screenshot_result,
                        'front_photo_on_screen_result': photo_on_screen_result,
                        'doc_on_pp': doc_on_pp_result,
                        'screenshot_result': screenshot_result,
                        'photo_on_screen_result': photo_on_screen_result,
                        'front_blurred': blurred, 
                        'front_glare': glare,
                        'back_blurred': blurred, 
                        'back_glare': glare,
                        'front_face_locations': front_face_locations_str,
                        'front_face_encodings': front_face_encodings_str,
                        'valid_nationality': valid_nationality_result,
                        'issuing_country': 'IRQ',
                        'nationality_received': nationality
                    }

                passport_data.update(passport_data_update)

                non_optional_keys = ["gender", "passport_date_of_birth", "id_number", "passport_date_of_expiry"]
                empty_string_keys = [key for key, value in passport_data.items() if key in non_optional_keys and value == '']
                    
                if empty_string_keys:
                    passport_data['error'] = 'covered_photo'

            except Exception as e:
                passport_data['error'] = 'bad_image'
                passport_data['error_details'] = e

            try:
                new_dict = extract_mother_name_and_surname(passport_text)
                new_dict['mother_first_name_en'] = new_dict.get('mother_first_name', '')
                new_dict['mother_last_name_en'] = new_dict.get('mother_last_name', '')

                from deep_translator import GoogleTranslator
                new_dict['mother_first_name'] = GoogleTranslator('en', 'ar').translate(
                    new_dict.get('mother_first_name', ''))
                new_dict['mother_last_name'] = GoogleTranslator('en', 'ar').translate(
                    new_dict.get('mother_last_name', ''))
                passport_data.update(new_dict)
            except Exception as e:
                passport_data['mother_first_name'], passport_data['mother_first_name_en'] = '', ''
                passport_data['mother_last_name'], passport_data['mother_last_name_en'] = '', ''
                print("error:", e)

            return passport_data

        if (nationality and nationality == 'LBN') or (not nationality and country == 'LBN'):
            logging.info("-------------Working on LBN Passport \n")
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.lebanon_passport_extraction import lebanon_passport_extraction
            from idvpackage.common import load_and_process_image_deepface

            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }

            try:
                st = time.time()
                processed_passport = self.image_conversion(passport)
                logging.info(f'----------------Time taken for image conversion passport: {time.time() - st} seconds\n')

                st = time.time()
                id_infos = self.get_ocr_results(processed_passport)
                passport_text = id_infos[0].description
                logging.info(f'----------------Time taken for vision passport: {time.time() - st} seconds\n')

                pattern4 = r'(Republic of Lebanon|Républeue Libanaise)'  # Passport
                k = re.search(pattern4, passport_text, re.IGNORECASE)

                if not k:
                    passport_data["error"] = "not_passport"
                    return passport_data

                st = time.time()
                passport_details = lebanon_passport_extraction(passport_text)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction passport: {time.time() - st} seconds\n')

                passport_data.update(passport_details)

                image = np.array(processed_passport)

                st = time.time()
                ## TODO: doc_on_pp and detect_photo_on_screen for LBN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                screenshot_result = detect_screenshot(self.client, passport)
                # photo_on_screen_result = detect_photo_on_screen(self.client, passport)
                photo_on_screen_result = 'clear'
                blurred, glare = self.get_blurred_and_glared_for_doc(image)
                print(f"Nationality: {passport_details.get('nationality')}")
                valid_nationality_result = self.check_nationality_in_iso_list(passport_details.get('nationality'))
                logging.info(
                    f'----------------Time taken for fraud detection attributes passport: {time.time() - st} seconds\n')

                st = time.time()
                front_face_locations, front_face_encodings = load_and_process_image_deepface(passport)
                logging.info(f'----------------Time taken for face extraction passport: {time.time() - st} seconds\n')

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                passport_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'passport_data': passport_text,
                    'front_coloured': True,
                    'back_coloured': True,
                    'front_logo_result': 'clear',
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': blurred,
                    'front_glare': glare,
                    'back_blurred': blurred,
                    'back_glare': glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str,
                    'valid_nationality': valid_nationality_result,
                    'nationality_received': nationality,
                    'issuing_country': 'LBN',
                }

                passport_data.update(passport_data_update)

                if not passport_data.get('id_number') or not passport_data.get('dob') or not passport_data.get(
                        'first_name') or not passport_data.get('last_name') or not passport_data.get('expiry_date'):
                    passport_data['error'] = 'covered_photo'

                non_optional_keys = ["front_face_locations", "id_number", "dob", "first_name", "last_name",
                                     "expiry_date"]
                empty_string_keys = [key for key, value in passport_data.items() if
                                     key in non_optional_keys and (value == '' or value == [] or value == '[]')]

                if empty_string_keys:
                    passport_data['error'] = 'covered_photo'

            except Exception as e:
                passport_data['error'] = 'bad_image'
                passport_data['error_details'] = e

            return passport_data

        if (nationality and nationality == 'SDN') or (not nationality and country == 'SDN'):
            logging.info("-------------Working on SDN Passport \n")
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.sudan_passport_extraction import sdn_passport_extraction
            from idvpackage.common import load_and_process_image_deepface
            from idvpackage.blur_detection import is_image_blur

            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }

            try:
                st = time.time()
                processed_passport = self.image_conversion(passport)
                logging.info(f'----------------Time taken for image conversion passport: {time.time() - st} seconds\n')

                st = time.time()
                compressed_image = BytesIO()
                #TODO

                #processed_passport=self.preprocess_image(processed_passport, sharpness=2.0, contrast=1.5, radius=3, percent=180, threshold=5)
                #Enhance image sharpness and contrast.
                processed_passport.save(compressed_image, format="JPEG", quality=95, optimize=True)
                compressed_image_data = compressed_image.getvalue()
                id_infos = self.get_ocr_results(compressed_image_data, country='SDN')
                passport_text = id_infos[0].description
                logging.info(f'----------------Time taken for vision passport: {time.time() - st} seconds\n')

                pattern4 = r'(Republic of Sudan|Republic of the Sudan|PCSDN|SDN)'
                k = re.search(pattern4, passport_text, re.IGNORECASE)

                if k:
                    print(f"Keyword feature matches: {k.group()}\n")

                if not k:
                    passport_data["error"] = "not_passport"
                    return passport_data
                
                image = np.array(processed_passport)
                if is_image_blur(
                            image,
                            laplace_threshold=20,
                            canny_threshold=1500,
                            fft_threshold=100,
                            bright_reflection_threshold=100,
                            bright_reflection_min_area=1.0
                    ):
                    print(f"Passport Document is blurry, marking as covered photo")
                    passport_data['error'] = 'blur_photo'
                    return passport_data
                
                st = time.time()
                passport_details = sdn_passport_extraction(passport_text)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction passport: {time.time() - st} seconds\n')

                if passport_details.get('dob'):
                    try:
                        dob = passport_details['dob']
                        dob_date = datetime.strptime(dob, "%d/%m/%Y")
                        current_date = datetime.now()

                        age = current_date.year - dob_date.year - (
                                    (current_date.month, current_date.day) < (dob_date.month, dob_date.day))

                        if age < 18:
                            passport_data['error'] = 'under_age'
                            return passport_data
                    except:
                        pass

                if passport_details.get('expiry_date'):
                    try:
                        expiry_date = passport_details['expiry_date']
                        expiry_date = datetime.strptime(expiry_date, "%d/%m/%Y")
                        current_date = datetime.now()

                        if expiry_date < current_date:
                            passport_data['error'] = 'expired_id'
                            return passport_data
                    except:
                        pass

                passport_data.update(passport_details)

                if passport_data.get('issue_date'):
                    passport_data['issuance_date'] = passport_details['issue_date']

                image = np.array(processed_passport)

                st = time.time()
                ## TODO: doc_on_pp and detect_photo_on_screen for LBN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                screenshot_result = detect_screenshot(self.client, passport)
                # photo_on_screen_result = detect_photo_on_screen(self.client, passport)
                photo_on_screen_result = 'clear'
                blurred, glare = self.get_blurred_and_glared_for_doc(image)
                valid_nationality_result = self.check_nationality_in_iso_list(passport_details.get('nationality'))
                logging.info(
                    f'----------------Time taken for fraud detection attributes passport: {time.time() - st} seconds\n')

                st = time.time()
                front_face_locations, front_face_encodings = load_and_process_image_deepface(passport, country='SDN')
                logging.info(f'----------------Time taken for face extraction passport: {time.time() - st} seconds\n')

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                passport_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'passport_data': passport_text,
                    'front_coloured': True,
                    'back_coloured': True,
                    'front_logo_result': 'clear',
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': blurred,
                    'front_glare': glare,
                    'back_blurred': blurred,
                    'back_glare': glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str,
                    'valid_nationality': valid_nationality_result,
                    'nationality_received': nationality
                }

                passport_data.update(passport_data_update)

                non_optional_keys = ["passport_number_mrz", "dob_mrz", "expiry_date_mrz", "gender"]
                empty_string_keys = [key for key, value in passport_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    passport_data['error'] = 'missing_key_fields'

            except Exception as e:
                passport_data['error'] = 'Something went wrong'
                print(f"-------------->> Something went wrong error trace:: {e}")
                passport_data['error_details'] = e

            return passport_data

        if (nationality and nationality == 'SYR') or (not nationality and country == 'SYR'):
            logging.info("-------------Working on SYR Passport \n")
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.syr_passport_extraction import syr_passport_extraction_front, syr_passport_extraction_back
            from idvpackage.common import load_and_process_image_deepface

            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }

            try:

                st = time.time()
                processed_passport = self.image_conversion(passport)
                logging.info(f'----------------Time taken for image conversion passport: {time.time() - st} seconds\n')

                st = time.time()
                id_infos = self.get_ocr_results(processed_passport)
                passport_text = id_infos[0].description
                logging.info(f'----------------Time taken for vision passport: {time.time() - st} seconds\n')

                # print(f"\nPassport text: {passport_text}\n")

                pattern4 = r'(Syrian Arab Republic|REPUBLIQUE ARABE SYRIEH|Syrian|Syrienne|SYR)'
                k = re.search(pattern4, passport_text, re.IGNORECASE)

                if not k:
                    passport_data["error"] = "not_passport"
                    return passport_data

                st = time.time()
                passport_details = syr_passport_extraction_front(passport_text, self.api_key)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction passport: {time.time() - st} seconds\n')

                passport_data.update(passport_details)

                image = np.array(processed_passport)

                st = time.time()
                ## TODO: doc_on_pp and detect_photo_on_screen for LBN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                screenshot_result = detect_screenshot(self.client, passport)
                # photo_on_screen_result = detect_photo_on_screen(self.client, passport)
                photo_on_screen_result = 'clear'
                blurred, glare = self.get_blurred_and_glared_for_doc(image)
                valid_nationality_result = self.check_nationality_in_iso_list(passport_details.get('nationality'))
                logging.info(
                    f'----------------Time taken for fraud detection attributes passport: {time.time() - st} seconds\n')

                st = time.time()
                front_face_locations, front_face_encodings = load_and_process_image_deepface(passport)
                logging.info(f'----------------Time taken for face extraction passport: {time.time() - st} seconds\n')

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                passport_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'passport_data': passport_text,
                    'front_coloured': True,
                    'back_coloured': True,
                    'front_logo_result': 'clear',
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': blurred,
                    'front_glare': glare,
                    'back_blurred': blurred,
                    'back_glare': glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str,
                    'valid_nationality': valid_nationality_result,
                    'nationality_received': nationality,
                    'issuing_country': nationality
                }

                passport_data.update(passport_data_update)

                non_optional_keys = ["passport_number", "dob", "gender"]
                empty_string_keys = [key for key, value in passport_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    passport_data['error'] = 'covered_photo'

            except Exception as e:
                passport_data['error'] = 'bad_image'
                passport_data['error_details'] = e

            return passport_data

        if (nationality and nationality == 'JOR') or (not nationality and country == 'JOR'):
            logging.info("-------------Working on JOR Passport \n")
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.jor_passport_extraction import jordan_passport_extraction
            from idvpackage.common import load_and_process_image_deepface

            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }

            try:
                st = time.time()
                processed_passport = self.image_conversion(passport)
                logging.info(f'----------------Time taken for image conversion passport: {time.time() - st} seconds\n')

                st = time.time()
                id_infos = self.get_ocr_results(processed_passport)
                passport_text = id_infos[0].description
                logging.info(f'----------------Time taken for vision passport: {time.time() - st} seconds\n')

                pattern4 = r'(Hashemite Kingdom of Jordan|Hashemite Kingdom|Jordan)'
                k = re.search(pattern4, passport_text, re.IGNORECASE)

                if not k:
                    passport_data["error"] = "not_passport"
                    return passport_data

                st = time.time()
                passport_details = jordan_passport_extraction(passport_text, self.api_key)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction passport: {time.time() - st} seconds\n')

                passport_data.update(passport_details)

                image = np.array(processed_passport)

                st = time.time()
                ## TODO: doc_on_pp and detect_photo_on_screen for LBN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                screenshot_result = detect_screenshot(self.client, passport)
                # photo_on_screen_result = detect_photo_on_screen(self.client, passport)
                photo_on_screen_result = 'clear'
                blurred, glare = self.get_blurred_and_glared_for_doc(image)
                valid_nationality_result = self.check_nationality_in_iso_list(passport_details.get('nationality'))
                logging.info(
                    f'----------------Time taken for fraud detection attributes passport: {time.time() - st} seconds\n')

                st = time.time()
                front_face_locations, front_face_encodings = load_and_process_image_deepface(passport)
                logging.info(f'----------------Time taken for face extraction passport: {time.time() - st} seconds\n')

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                passport_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'passport_data': passport_text,
                    'front_coloured': True,
                    'back_coloured': True,
                    'front_logo_result': 'clear',
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': blurred,
                    'front_glare': glare,
                    'back_blurred': blurred,
                    'back_glare': glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str,
                    'valid_nationality': valid_nationality_result,
                    'nationality_received': nationality,
                    'issuing_country': nationality
                }

                passport_data.update(passport_data_update)

                non_optional_keys = ["passport_number", "dob", "expiry_date", "gender"]
                empty_string_keys = [key for key, value in passport_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    passport_data['error'] = 'covered_photo'

            except Exception as e:
                passport_data['error'] = 'bad_image'
                passport_data['error_details'] = e

            return passport_data

        if (nationality and nationality == 'PSE') or (not nationality and country == 'PSE'):
            logging.info("-------------Working on PSE Passport \n")
            from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
            from idvpackage.pse_passport_extraction import palestine_passport_extraction
            from idvpackage.common import load_and_process_image_deepface

            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }

            try:
                st = time.time()
                processed_passport = self.image_conversion(passport)
                logging.info(f'----------------Time taken for image conversion passport: {time.time() - st} seconds\n')

                st = time.time()
                id_infos = self.get_ocr_results(processed_passport)
                passport_text = id_infos[0].description
                logging.info(f'----------------Time taken for vision passport: {time.time() - st} seconds\n')

                pattern4 = r'(PALESTINIAN AUTHORITY|PALESTINE|P<PSE|PSE)'  # PASSPORT
                k = re.search(pattern4, passport_text, re.IGNORECASE)

                if not k:
                    passport_data["error"] = "not_passport"
                    return passport_data

                st = time.time()
                passport_details = palestine_passport_extraction(passport_text, self.api_key)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction passport: {time.time() - st} seconds\n')

                passport_data.update(passport_details)

                image = np.array(processed_passport)

                st = time.time()
                ## TODO: doc_on_pp and detect_photo_on_screen for LBN
                # doc_on_pp_result = document_on_printed_paper(image)
                doc_on_pp_result = 'clear'
                screenshot_result = detect_screenshot(self.client, passport)
                # photo_on_screen_result = detect_photo_on_screen(self.client, passport)
                photo_on_screen_result = 'clear'
                blurred, glare = self.get_blurred_and_glared_for_doc(image)
                valid_nationality_result = self.check_nationality_in_iso_list(passport_details.get('nationality'))
                logging.info(
                    f'----------------Time taken for fraud detection attributes passport: {time.time() - st} seconds\n')

                st = time.time()
                front_face_locations, front_face_encodings = load_and_process_image_deepface(passport)
                logging.info(f'----------------Time taken for face extraction passport: {time.time() - st} seconds\n')

                front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                passport_data_update = {
                    # 'back_tampered_result': tampered_result_back,
                    'passport_data': passport_text,
                    'front_coloured': True,
                    'back_coloured': True,
                    'front_logo_result': 'clear',
                    'front_doc_on_pp': doc_on_pp_result,
                    'front_screenshot_result': screenshot_result,
                    'front_photo_on_screen_result': photo_on_screen_result,
                    'doc_on_pp': doc_on_pp_result,
                    'screenshot_result': screenshot_result,
                    'photo_on_screen_result': photo_on_screen_result,
                    'front_blurred': blurred,
                    'front_glare': glare,
                    'back_blurred': blurred,
                    'back_glare': glare,
                    'front_face_locations': front_face_locations_str,
                    'front_face_encodings': front_face_encodings_str,
                    'valid_nationality': valid_nationality_result,
                    'nationality_received': nationality,
                    'issuing_country': nationality
                }

                passport_data.update(passport_data_update)

                non_optional_keys = ["passport_number", "dob", "expiry_date", "gender"]
                empty_string_keys = [key for key, value in passport_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    passport_data['error'] = 'covered_photo'

            except Exception as e:
                passport_data['error'] = 'bad_image'
                passport_data['error_details'] = e

            return passport_data

    def exract_passport_info_back(self, passport, country, nationality):
        if (nationality and nationality == 'SYR') or (not nationality and country == 'SYR'):
            from idvpackage.syr_passport_extraction import syr_passport_extraction_back

            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }

            try:
                st = time.time()
                processed_passport = self.image_conversion(passport)
                logging.info(f'----------------Time taken for image conversion passport: {time.time() - st} seconds\n')

                st = time.time()
                id_infos = self.get_ocr_results(processed_passport)
                passport_text = id_infos[0].description
                logging.info(f'----------------Time taken for vision passport: {time.time() - st} seconds\n')

                # print(f"\nPassport text: {passport_text}\n")

                st = time.time()
                passport_details = syr_passport_extraction_back(passport_text, self.api_key)
                logging.info(
                    f'----------------Time taken for data formatting and final extraction passport: {time.time() - st} seconds\n')

                passport_data.update(passport_details)

                non_optional_keys = ["issuing_date", "expiry_date"]
                empty_string_keys = [key for key, value in passport_data.items() if
                                     key in non_optional_keys and value == '']

                if empty_string_keys:
                    passport_data['error'] = 'covered_photo'

            except Exception as e:
                passport_data['error'] = 'bad_image'
                passport_data['error_details'] = e

        return passport_data

    def replace_keywords(self, report, target='consider', replacement='clear'):
        if isinstance(report, dict):
            # Iterate through dictionary items
            for key, value in report.items():
                # If the value matches the target, replace it
                if value == target:
                    report[key] = replacement
                else:
                    # Recursively call for nested dictionaries or lists
                    self.replace_keywords(value, target, replacement)
        elif isinstance(report, list):
            # If the report is a list, iterate through elements
            for index, item in enumerate(report):
                # Recursively call for each element
                self.replace_keywords(item, target, replacement)

    def extract_ocr_info(self, data, video, country, report_names, back_img=None):
        try:
            if data.get('uae_pass_data', ''):
                uae_pass_data = data.get('uae_pass_data', {})
                if uae_pass_data:
                    dob = uae_pass_data.get('DateOfBirth', '')
                    if dob:
                        data['dob'] = dob
                    
                    expiry_date = uae_pass_data.get('expiryDate', '')
                    if expiry_date:
                        data['expiry_date'] = expiry_date
                    
                    gender = uae_pass_data.get('genderCode', '')
                    if gender:
                        data['gender'] = gender
                    
                    nationality = uae_pass_data.get('nationalityCode', '')
                    if nationality:
                        data['nationality_received'] = nationality

            st = time.time()
            from idvpackage.ocr_utils import form_final_data_document_report, form_final_facial_similarity_report
            face_match_threshold = 0.59
            document_report = {}
            facial_report = {}

            if country == 'IRQ':
                face_match_threshold = 0.30

            if country=='SDN':
                face_match_threshold=0.40

            tampering_result = 'clear'
            data['tampering_result'] = tampering_result

            if data.get('front_tampered_result') == 'Tampered' or data.get('back_tampered_result') == 'Tampered':
                tampering_result = 'consider'
                data['tampering_result'] = tampering_result

            if country == 'IRQ' and data.get('doc_type') == 'national_identity_card':
                if not data.get("gender") and data.get("gender_back"):
                    data['gender'] = data.get("gender_back")

                # validation_result = self.validate_fields_id(data, country)
                # if not validation_result:
                #     tampering_result = 'consider'
                #     data['tampering_result'] = tampering_result

            colour_picture = 'consider'
            if data.get('front_coloured') and data.get('back_coloured'):
                colour_picture = 'clear'

            blurred = 'clear'
            if data.get('front_blurred') == 'consider' or data.get('back_blurred') == 'consider':
                blurred = 'consider'

            glare = 'clear'
            if data.get('front_glare') == 'consider' or data.get('back_glare') == 'consider':
                glare = 'consider'

            missing_fields = 'clear'
            if data.get('front_missing_fields') or data.get('back_missing_fields'):
                missing_fields = 'consider'

            if video and data.get('front_face_locations', ''):
                face_loc = json.loads(data.get('front_face_locations'))
                front_face_locations = tuple(face_loc)
                front_face_encodings = np.array(json.loads(data.get('front_face_encodings')))

                data['front_face_locations'] = front_face_locations
                data['front_face_encodings'] = front_face_encodings

                selfie_str = data.get('selfie')
                if isinstance(selfie_str, str):
                    selfie = np.array(json.loads(selfie_str))
                else:
                    selfie = selfie_str

                try:
                    if country=='IRQ':
                         from idvpackage.common import extract_face_and_compute_cosine_similarity
                         similarity = extract_face_and_compute_cosine_similarity(selfie, front_face_locations, front_face_encodings)

                    else:
                         similarity = self.extract_face_and_compute_similarity(selfie, front_face_locations,
                                                                           front_face_encodings)
                except Exception as e:
                    print("issue in extracting face and computing similarity")
                    selfie = None
                    similarity = 0

            else:
                selfie = None
                similarity = 0

            # front_face_locations, front_face_encodings = data.get('front_face_locations'), data.get('front_face_encodings')
            # processed_selfie = self.process_image(selfie)
            if country == 'SAU' or data.get('doc_type') == 'passport':
                back_id_text = ''
            else:
                back_id_text = data.get('back_extracted_data')

            if data.get('doc_type') == 'national_identity_card':
                front_id_text = data.get('front_extracted_data')
            else:
                front_id_text = ''

            nationality = data.get('nationality_received', '')

            if 'document' in report_names:
                if nationality and not data.get('uae_pass_data', ''):
                    print(f"\nNationality present, picking  {nationality} for generating Document Report")
                    document_report = form_final_data_document_report(data, front_id_text, back_id_text, nationality,
                                                                      colour_picture, selfie, similarity, blurred,
                                                                      glare, missing_fields, face_match_threshold,
                                                                      back_img)
                else:
                    print(f"\nNationality not present, picking country: {country} for generating Document Report")
                    document_report = form_final_data_document_report(data, front_id_text, back_id_text, country,
                                                                      colour_picture, selfie, similarity, blurred,
                                                                      glare, missing_fields, face_match_threshold,
                                                                      back_img)

                if document_report:
                    if country=='IRQ' and nationality in ['LBN','PSE']:
                        document_report['properties'].pop('id_number', None)

                    if country=='IRQ' and nationality in ['JOR','SYR']:
                        document_report['properties'].pop('passport_number',None)

                    if country=='IRQ' and nationality in ['SDN']:
                        document_report['properties'].pop('passport_number_mrz', None)

            if 'facial_similarity_video' in report_names:
                if video:
                    liveness_result = self.check_for_liveness(similarity, video, face_match_threshold)
                    if country=='IRQ':
                        liveness_result = 'clear'
                    # print(f"LIVE RES: {liveness_result}")
                else:
                    liveness_result = None, None

                if nationality:
                    print(f"\nNationality present, pikcing nationality: {nationality} for generating Video Report")
                    facial_report = form_final_facial_similarity_report(data, selfie, similarity, liveness_result,
                                                                        face_match_threshold, nationality)
                else:
                    print(f"\nNationality not present, pikcing country: {country} for generating Document Report")
                    facial_report = form_final_facial_similarity_report(data, selfie, similarity, liveness_result,
                                                                        face_match_threshold, country)

            logging.info(
                f"--------------Time taken for Extract Ocr Function in IDV package: {time.time() - st} seconds\n")

            return document_report, facial_report

        except Exception as e:
            logging.info(f"--------------Error occurred in extract_ocr_info: {e}\n")
            raise Exception("Error occurred in extract_ocr_info")

    def generate_facial_report_portal(self, data, latest_portal_video):
        from idvpackage.ocr_utils import form_final_facial_similarity_report

        try:
            if latest_portal_video:
                latest_vid_liveness_result = self.check_for_liveness(0, latest_portal_video)

            initial_selfie_str = data.get('initial_selfie', '')
            latest_selfie_str = data.get('latest_selfie', '')

            if isinstance(initial_selfie_str, str):
                initial_selfie = np.array(json.loads(initial_selfie_str))
            else:
                initial_selfie = initial_selfie_str

            if isinstance(latest_selfie_str, str):
                latest_selfie = np.array(json.loads(latest_selfie_str))
            else:
                latest_selfie = latest_selfie_str

            face_locations1, face_encodings1 = self.load_and_process_image_fr(initial_selfie, arr=True)
            face_locations2, face_encodings2 = self.load_and_process_image_fr(latest_selfie, arr=True)

            if not face_encodings1 or not face_encodings2:
                print('No face detected in selfie or front ID')
                similarity_score = 0
            else:
                largest_face_index1 = face_locations1.index(
                    max(face_locations1, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))
                largest_face_index2 = face_locations2.index(
                    max(face_locations2, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))

                face_encoding1 = face_encodings1[largest_face_index1]
                face_encoding2 = face_encodings2[largest_face_index2]

                similarity_score = self.calculate_similarity(face_encoding1, face_encoding2)

                similarity_score = min(1, similarity_score)

            facial_report = form_final_facial_similarity_report(data, latest_selfie, similarity_score,
                                                                latest_vid_liveness_result, 0.70, 'IRQ')

            return facial_report

        except Exception as e:
            logging.info(f"--------------Error occurred in generate_facial_report_portal: {e}\n")
            raise Exception("Error occurred in generate_facial_report for portal")

