import re
from datetime import datetime
from itertools import permutations
import cv2
import numpy as np
from PIL import Image
import io
from google.cloud import vision_v1
import tempfile
import os
from io import BytesIO
import logging
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.spatial.distance import cosine

# Global variables to store lazily loaded modules
_deepface = None
_face_recognition = None

def get_deepface():
    """Lazy loading of DeepFace"""
    global _deepface
    if _deepface is None:
        from deepface import DeepFace
        _deepface = DeepFace
    return _deepface

def get_face_recognition():
    """Lazy loading of face_recognition"""
    global _face_recognition
    if _face_recognition is None:
        import face_recognition
        _face_recognition = face_recognition
    return _face_recognition

def func_common_dates(  extract_no_space):
    dob = ''
    expiry_date = ''
    try:
        matches = re.findall(r'\d{2}/\d{2}/\d{4}', extract_no_space)
        y1 = matches[0][-4:]
        y2 = matches[1][-4:]
        if int(y1) < int(y2):
            dob = matches[0]
            expiry_date = matches[1]
        else:
            dob = matches[1]
            expiry_date = matches[0]
    except:
        dob = ''
        expiry_date = ''

    return dob, expiry_date

def convert_dob(input_date):
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

def func_dob(  extract):
    extract_no_space = extract.replace(' ','')
    dob, expiry_date = func_common_dates(extract_no_space)
    if dob == '':  
        match_dob = re.findall(r'\d{7}(?:M|F)\d', extract_no_space)
        for i in match_dob:
            # print(i)
            raw_dob = i[0:6]
            # print(raw_dob)
            year = str(datetime.today().year)[2:4]
            temp = '19'
            if int(raw_dob[0:2]) > int(year):
                temp = '19'
            else:
                temp = '20'      
            dob = raw_dob[4:6]+'/'+raw_dob[2:4]+'/'+temp+raw_dob[0:2]
            try:
                dt_obj = datetime.strptime(dob, '%d/%m/%Y')
                break
            except:
                # print(f'invalid date {dob}')
                dob = ''
        else:
            pattern = r"\b(\d{14}).*?\b"

            new_dob_match = re.search(pattern, extract_no_space)

            if new_dob_match:
                new_dob = new_dob_match.group(1)
                new_dob = new_dob[:7]
                dob = convert_dob(new_dob)

    return dob

def func_expiry_date(  extract):
    extract_no_space = extract.replace(' ','')
    dob, expiry_date = func_common_dates(extract_no_space)
    if expiry_date == '':
        match_doe = re.findall(r'\d{7}[A-Z]{2,3}', extract_no_space) 
        for i in match_doe:
         
            raw_doe = i[0:6]
            # print(raw_doe)
            expiry_date = raw_doe[4:6]+'/'+raw_doe[2:4]+'/20'+raw_doe[0:2]
            try:
                dt_obj = datetime.strptime(expiry_date, '%d/%m/%Y')
                break
            except:
   
                expiry_date = ''

    return expiry_date

def convert_expiry_date(input_date):
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

def extract_first_9_digits(string_input):
    match = re.search(r'\b\d{9}\b', string_input)
    if match:
        sequence = match.group(0)
        return sequence
    else:
        return ""

def func_card_number(  extract):
    extract_no_space = extract.replace(' ','')
    try:
        card_number = re.search(r'\d{9}', extract_no_space).group()
    except:
        card_number=  extract_first_9_digits(extract_no_space)

    return card_number


def count_digits_after_pattern(s):
    """
    Counts the number of digits that come after a specified pattern in a string.

    Parameters:
    s (str): The input string.
    pattern (str): The pattern to search for.

    Returns:
    int: The count of digits that come after the pattern.
    """
    # Construct the regex pattern to find the specified pattern followed by digits
    pattern = "<<<<"
    regex_pattern = re.compile(f"{re.escape(pattern)}(\d+)")
    
    # Search for the pattern in the string
    match = regex_pattern.search(s)
    
    # If a match is found, count the digits
    if match:
        digits_after_pattern = match.group(1)
        return len(digits_after_pattern)
    else:
        return 0  # Pattern not found

def remove_special_characters1(string):
    # This pattern matches any character that is not a letter, digit, or space
    #pattern = r'[^a-zA-Z0-9<\s]'
    pattern = r'[^a-zA-Z0-9<>]'
    return re.sub(pattern, '', string)

def remove_special_characters_mrz2(string):
    # This pattern matches any character that is not a letter, digit, or space
    pattern = r'[^a-zA-Z0-9\s]'
    return re.sub(pattern, '', string)

def validate_string(s):
    """
    Validates if the string follows the specific structure.

    Structure: 7 digits, followed by 'M' or 'F', then 7 digits again,
    then 3 uppercase letters, and ending with 1 digit.

    Parameters:
    s (str): The string to be validated.

    Returns:
    bool: True if the string follows the structure, False otherwise.
    """
    pattern = r'^\d{7}[MF]\d{7}[A-Z]{3}\d$'
    return bool(re.match(pattern, s))


def remove_special_characters2(string):
    # This pattern matches any character that is not a letter, digit, or space
    pattern = r'[^a-zA-Z0-9\s]'
    return re.sub(pattern, ' ', string)

def func_name(extract):
    bio_data = extract[-40:]
    breakup = bio_data.split('\n')
    if len(breakup) == 2:
        name_extract = breakup.pop(0)
    else:
        country_extract = breakup.pop(0).replace(" ","")
        name_extract = breakup.pop(0)

# Check the alphanumeric nature of name_extract
    if not name_extract.isupper():
        name_extract = breakup.pop(0)
    
    try:
        name = name_extract.replace("<", " ").replace(">", " ").replace(".", " ").replace(":", " ").replace('«','').strip()
        name = ' '.join(name.split())
        name = name.replace("0", "O") # special case fix
    except:
        name = ""

    return name

def func_nationality(  extract):
    extract_no_space = extract.replace(' ','')
    try:
        pattern = r'\d{5}[A-Z]{3}|\d{5}[A-Z]{2}'

        m = re.findall(pattern, extract_no_space)
        country = m[len(m)-1].replace("<", "")[5:]
    except:
        country = ""

    if country == '':
        try:
            pattern = r'\d{2}[a-z][A-Z]{2}'

            m = re.findall(pattern, extract_no_space)
            country = m[len(m)-1].replace("<", "")[2:].upper()
        except:
            country = ""

    return country

def clean_string(input_string):
        cleaned_string = re.sub(r'[^\w\s]', ' ', input_string)
        return cleaned_string.strip()

def count_digits(element):
    digits = [char for char in element if char.isdigit()]
    return len(digits)
    
def find_and_slice_number(input_number, digits):
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
    
def func_id_number(extract,dob):
        
    try:
        p = "784" + "\d{12}"
        id_re = re.search(p, clean_string(extract).replace(' ',''))
        id_number = id_re.group()
    except:
        
        try:
            pattern = r'\d{15,}'
            digits = '784'
            matches = re.findall(pattern, clean_string(extract).replace(' ',''))
            input_number = matches[0]
            dob=dob[-4:]
            id_number='784'+dob+find_and_slice_number(input_number, digits)[:8]
            
        except:
            id_number = ''

    return id_number


# #year = dob[-4:]
# p = "784" + "\d{12}"
# id_re = re.search(p, clean_string(data).replace(' ',''))
# id_number = id_re.group()



def convert_to_date(date_str):
    year = '19' + date_str[:2] if int(date_str[:2]) >= 50 else '20' + date_str[:2]
    month = date_str[2:4]
    day = date_str[4:6]
    return f"{day}/{month}/{year}"

def check_valid_date(date_str, format="%d/%m/%Y"):
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False
    

def find_expiry_date(original_text,mrz2):
    
    dates = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', original_text)
    expiry_date = ''

    if len(dates) == 2:
        
        date1 = datetime.strptime(dates[0], '%d/%m/%Y')
        date2 = datetime.strptime(dates[1], '%d/%m/%Y')
        
        if date2 < date1:
            expiry_date = dates[0]
        elif date2 > date1:
            expiry_date = dates[1]
            
    elif mrz2:
        match_expiry_date = re.search(r'[A-Za-z](\d+)', mrz2)
        if match_expiry_date:
            expiry_date = match_expiry_date.group(1)[:6]
            expiry_date = convert_to_date(expiry_date)
    
            
    if not check_valid_date(expiry_date):
            expiry_date=''
    return expiry_date

def find_dob(original_text,mrz2):
    
     dates = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', original_text)
     dob = ''
  
     if len(dates) == 2:
            date1 = datetime.strptime(dates[0], '%d/%m/%Y')
            date2 = datetime.strptime(dates[1], '%d/%m/%Y')

            if date2 < date1:
                dob = dates[1]
            elif date2 > date1:
                dob = dates[0] 
                
     elif mrz2:
        match_dob = re.search(r'(\d+)[A-Za-z]', mrz2)
        if match_dob:
            dob = match_dob.group(1)[:6] 
            dob=convert_to_date(dob)
    
     if not check_valid_date(dob):
            dob=''
     return dob


def convert_date_format(date_str):
    # Parse the date from DD/MM/YYYY format
    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    # Convert it to YYYY-MM-DD format
    formatted_date = date_obj.strftime('%Y-%m-%d')
    return formatted_date


def convert_gender(gender_char):
    if gender_char.lower() == 'm':
        return 'Male'
    elif gender_char.lower() == 'f': 
        return 'Female'
    else:  
        return ''


def compute_ela_cv(orig_img, quality):
    SCALE = 15
    orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        temp_filename = temp_file.name

        cv2.imwrite(temp_filename, orig_img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        # read compressed image
        compressed_img = cv2.imread(temp_filename)

        # get absolute difference between img1 and img2 and multiply by scale
        diff = SCALE * cv2.absdiff(orig_img, compressed_img)
    
    # delete the temporary file
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    return diff


def calculate_error_difference(orig_img, country=None):
    if isinstance(orig_img, Image.Image):
        orig_img = np.array(orig_img)
        
    if np.any(orig_img):
        ela_val = compute_ela_cv(orig_img, quality=94)
        diff_avg = ela_val.mean()

        print(f"DIFFERENCE: {diff_avg}")
        if country == 'UAE':
            if diff_avg <= 25:
                label = 'Genuine'
            else:
                label = 'Tampered'
        else:
            if diff_avg <= 10.5:
                label = 'Genuine'
            else:
                label = 'Tampered'
                
        return label
    else:
        print(f"ISSUE")
        return 'Genuine'


def eastern_arabic_to_english(eastern_numeral):
    try:
        arabic_to_english_map = {
            '٠': '0', '۰': '0',
            '١': '1', '۱': '1',
            '٢': '2', '۲': '2',
            '٣': '3', '۳': '3',
            '٤': '4', '۴': '4',
            '٥': '5', '۵': '5',
            '٦': '6', '۶': '6',
            '٧': '7', '۷': '7',
            '٨': '8', '۸': '8',
            '٩': '9', '۹': '9',
            '/': '/'
        }

        english_numeral = ''.join([arabic_to_english_map[char] if char in arabic_to_english_map else char for char in eastern_numeral])
        
        return english_numeral

    except:
        return eastern_numeral

def english_to_eastern_arabic(english_numeral):
    try:
        english_to_arabic_map = {
            '0': '٠', 
            '1': '١', 
            '2': '٢', 
            '3': '٣', 
            '4': '٤', 
            '5': '٥', 
            '6': '٦', 
            '7': '٧', 
            '8': '٨', 
            '9': '٩'
        }

        eastern_arabic_numeral = ''.join([english_to_arabic_map[char] if char in english_to_arabic_map else char for char in english_numeral])
        
        return eastern_arabic_numeral

    except Exception as e:
        return str(e)  

def crop_third_part(img):
    width, height = img.size
    part_height = height // 3
    third_part = img.crop((0, 2 * part_height, width, height))
    # third_part.save("/Users/fahadpatel/Pictures/thirdpart.jpg")
    return third_part

def extract_text_from_image_data(client, image):
    """Detects text in the file."""

    # with io.BytesIO() as output:
    #     image.save(output, format="PNG")
    #     content = output.getvalue()

    compressed_image = BytesIO()
    image.save(compressed_image, format="JPEG", quality=100, optimize=True)
    content = compressed_image.getvalue()

    image = vision_v1.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    return texts[0].description

def detect_id_card_uae(client, image_data, id_text, part=None):
    if id_text:
        vertices = id_text[0].bounding_poly.vertices
        left = vertices[0].x
        top = vertices[0].y
        right = vertices[2].x
        bottom = vertices[2].y

        padding = 30
        left -= padding
        top -= padding
        right += padding
        bottom += padding

        # img = image_data

        with Image.open(io.BytesIO(image_data)) as img:
            id_card = img.crop((max(0, left), max(0, top), right, bottom))
            width, height = id_card.size
            if width < height:
                id_card = id_card.rotate(90, expand=True)
            
            tampered_result = calculate_error_difference(id_card, country = 'UAE')

            part_text = id_text[0].description
            if part == 'third':
                part_img = crop_third_part(id_card)
                part_text = extract_text_from_image_data(client, part_img)

            return  tampered_result, part_text

def rotate_image(img):
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

def load_and_process_image_deepface(image_input, country=None):
    DeepFace = get_deepface()  # Only load when needed
    face_recognition = get_face_recognition()  # Only load when needed
    def process_angle(img, angle):
        try:
            # Create a view instead of copy when possible
            if angle != 0:
                # Minimize memory usage during rotation
                with np.errstate(all='ignore'):
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    # Use existing buffer when possible
                    rotated = np.ascontiguousarray(img_pil.rotate(angle, expand=True))
                    img_to_process = cv2.cvtColor(rotated, cv2.COLOR_RGB2BGR)
                    # Clear references to intermediate arrays
                    del img_rgb, img_pil, rotated
            else:
                img_to_process = img

            # Extract faces with memory optimization
            face_objs = DeepFace.extract_faces(
                img_to_process,
                detector_backend='fastmtcnn',
                enforce_detection=False,
                align=True
            )

            if face_objs and len(face_objs) > 0:
                confidence = face_objs[0].get('confidence', 0)

                # print(f"Confidence: {confidence}")

                # Check face frame size only if confidence is less than 1
                if confidence < 1:
                    facial_area = face_objs[0]['facial_area']
                    # Sudanese Edge Case. They have smaller pictures.
                    if country == 'SDN' and (facial_area['w'] < 40 or facial_area['h'] < 50):
                        print(f"Rejecting face at {angle} degrees due to small size of Sudanese Document: {facial_area['w']}x{facial_area['h']} (minimum 40x50)")
                        return None, None, 0
                    elif country != 'SDN' and (facial_area['w'] < 80 or facial_area['h'] < 90):
                        print(f"Rejecting face at {angle} degrees due to small size: {facial_area['w']}x{facial_area['h']} (minimum 100x100)")
                        return None, None, 0

                # Immediately reject if confidence is below threshold
                if confidence < 0.95:
                    # print(f"Rejecting face at {angle} degrees due to low confidence: {confidence:.3f}")
                    return None, None, 0

                return face_objs, img_to_process, confidence

            # Clear memory if no face found
            del img_to_process
            return None, None, 0
        except Exception as e:
            print(f"Error processing angle {angle}: {e}")
            return None, None, 0
        finally:
            # Ensure memory is cleared
            if 'img_to_process' in locals():
                del img_to_process

    try:
        # Process input image efficiently
        if isinstance(image_input, np.ndarray):
            # Use view when possible
            image = np.ascontiguousarray(image_input)
            if image.dtype != np.uint8:
                image = image.astype(np.uint8, copy=False)
        elif isinstance(image_input, str):
            # Decode base64 directly to numpy array
            image_data = base64.b64decode(image_input)
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            del image_data  # Clear decoded data
        else:
            print(f"Unexpected input type: {type(image_input)}")
            return [], []

        if image is None or image.size == 0:
            print("Empty image")
            return [], []

        CONFIDENCE_THRESHOLD = 0.97

        # Try original orientation first to avoid unnecessary processing
        face_objs, processed_image, confidence = process_angle(image, 0)
        if face_objs is not None and confidence >= CONFIDENCE_THRESHOLD:
            try:
                biggest_face = max(face_objs, key=lambda face: face['facial_area']['w'] * face['facial_area']['h'])
                facial_area = biggest_face['facial_area']

                # Double check size requirements for biggest face
                if confidence < 1:
                    # print(f"Confidence less than 1: {confidence}")
                    if country == 'SDN' and (facial_area['w'] < 40 or facial_area['h'] < 50):
                        print(f"Face validation failed: Face frame too small {facial_area['w']}x{facial_area['h']} (minimum 40x50)")
                        return [], []
                    elif country != 'SDN' and (facial_area['w'] < 80 or facial_area['h'] < 90):
                        print(f"Face validation failed: Face frame too small {facial_area['w']}x{facial_area['h']} (minimum 100x100)")
                        return [], []

                x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']

                # Minimize memory usage during color conversion
                image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
                face_locations = [(y, x + w, y + h, x)]
                face_encodings = face_recognition.face_encodings(image_rgb, face_locations)

                if face_encodings:
                    # print(f"Found face in original orientation with confidence {confidence}")
                    return face_locations, face_encodings
            finally:
                # Clear memory
                del processed_image, image_rgb
                if 'face_objs' in locals():
                    del face_objs

        # Try other angles in parallel
        angles = [90, 180, 270]
        best_confidence = confidence if face_objs is not None else 0
        best_face_objs = face_objs
        best_image = processed_image

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(process_angle, image, angle): angle
                for angle in angles
            }

            try:
                for future in as_completed(futures):
                    face_objs, processed_image, confidence = future.result()
                    if face_objs is not None:
                        if confidence >= CONFIDENCE_THRESHOLD:
                            # Cancel remaining tasks
                            for f in futures:
                                if not f.done():
                                    f.cancel()
                            best_face_objs = face_objs
                            best_image = processed_image
                            best_confidence = confidence
                            break
            finally:
                for future in futures:
                    future.cancel()

        if best_face_objs is None or best_confidence < CONFIDENCE_THRESHOLD:
            print(f"No faces detected with confidence >= {CONFIDENCE_THRESHOLD}")
            return [], []

        try:
            biggest_face = max(best_face_objs, key=lambda face: face['facial_area']['w'] * face['facial_area']['h'])
            facial_area = biggest_face['facial_area']

            # Final size check for rotated face
            if confidence < 1:
                if facial_area['w'] < 80 or facial_area['h'] < 90:
                    print(f"Face validation failed: Face frame too small {facial_area['w']}x{facial_area['h']} (minimum 100x100)")
                    return [], []

            x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']

            # Minimize memory during final processing
            image_rgb = cv2.cvtColor(best_image, cv2.COLOR_BGR2RGB)
            face_locations = [(y, x + w, y + h, x)]
            face_encodings = face_recognition.face_encodings(image_rgb, face_locations)

            if face_encodings:
                return face_locations, face_encodings

            print("Failed to extract face encodings")
            return [], []
        finally:
            # Clear final processing memory
            del image_rgb, best_image, best_face_objs

    except Exception as e:
        print(f"Error in face detection: {e}")
        return [], []
    finally:
        # Ensure main image is cleared
        if 'image' in locals():
            del image


def calculate_similarity(face_encoding1, face_encoding2):
    face_recognition = get_face_recognition()
    similarity_score = 1 - face_recognition.face_distance([face_encoding1], face_encoding2)[0]

    return round(similarity_score + 0.25, 2)

def extract_face_and_compute_similarity(front_face_locations, front_face_encodings, back_face_locations, back_face_encodings):
    largest_face_index1 = front_face_locations.index(max(front_face_locations, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))
    largest_face_index2 = back_face_locations.index(max(back_face_locations, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))

    face_encoding1 = front_face_encodings[largest_face_index1]
    face_encoding2 = back_face_encodings[largest_face_index2]

    similarity_score = calculate_similarity(face_encoding1, face_encoding2)

    return min(1, similarity_score)

def load_and_process_image_deepface_all_orientations(image_input):
    """Similar to load_and_process_image_deepface but processes all orientations to find best confidence"""
    DeepFace = get_deepface()  # Only load when needed
    face_recognition = get_face_recognition()  # Only load when needed
    def process_angle(img, angle):
        try:
            # Create a view instead of copy when possible
            if angle != 0:
                # Minimize memory usage during rotation
                with np.errstate(all='ignore'):
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    # Use existing buffer when possible
                    rotated = np.ascontiguousarray(img_pil.rotate(angle, expand=True))
                    img_to_process = cv2.cvtColor(rotated, cv2.COLOR_RGB2BGR)
                    # Clear references to intermediate arrays
                    del img_rgb, img_pil, rotated
            else:
                img_to_process = img

            # Extract faces with memory optimization
            face_objs = DeepFace.extract_faces(
                img_to_process,
                detector_backend='fastmtcnn',
                enforce_detection=False,
                align=True
            )
            
            if face_objs and len(face_objs) > 0:
                confidence = face_objs[0].get('confidence', 0)
                # print(f"Face detected at {angle} degrees with confidence {confidence}")
                
                return face_objs, img_to_process, confidence
            
            # Clear memory if no face found
            del img_to_process
            return None, None, 0
        except Exception as e:
            print(f"Error processing angle {angle}: {e}")
            return None, None, 0
        finally:
            # Ensure memory is cleared
            if 'img_to_process' in locals():
                del img_to_process

    try:
        # Process input image efficiently
        if isinstance(image_input, np.ndarray):
            # Use view when possible
            image = np.ascontiguousarray(image_input)
            if image.dtype != np.uint8:
                image = image.astype(np.uint8, copy=False)
        elif isinstance(image_input, str):
            # Decode base64 directly to numpy array
            image_data = base64.b64decode(image_input)
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            del image_data  # Clear decoded data
        else:
            print(f"Unexpected input type: {type(image_input)}")
            return [], []

        if image is None or image.size == 0:
            print("Empty image")
            return [], []

        # Process all angles in parallel
        angles = [0, 90, 180, 270]
        best_confidence = 0
        best_face_objs = None
        best_image = None

        # Use context manager to ensure proper cleanup
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit tasks
            futures = {
                executor.submit(process_angle, image, angle): angle 
                for angle in angles
            }

            try:
                for future in as_completed(futures):
                    face_objs, processed_image, confidence = future.result()
                    if face_objs is not None and confidence > best_confidence:
                        best_confidence = confidence
                        best_face_objs = face_objs
                        best_image = processed_image
            finally:
                # Ensure all futures are cancelled
                for future in futures:
                    if not future.done():
                        future.cancel()

        if best_face_objs is None:
            print("No faces detected with fastmtcnn at any angle")
            return [], []

        # print(f"Using best detected face with confidence {best_confidence}")
        try:
            biggest_face = max(best_face_objs, key=lambda face: face['facial_area']['w'] * face['facial_area']['h'])
            facial_area = biggest_face['facial_area']
            x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
            
            # Minimize memory during final processing
            image_rgb = cv2.cvtColor(best_image, cv2.COLOR_BGR2RGB)
            face_locations = [(y, x + w, y + h, x)]
            face_encodings = face_recognition.face_encodings(image_rgb, face_locations)
            
            if face_encodings:
                return face_locations, face_encodings
            
            print("Failed to extract face encodings")
            return [], []
        finally:
            # Clear final processing memory
            del image_rgb, best_image, best_face_objs

    except Exception as e:
        print(f"Error in face detection: {e}")
        return [], []
    finally:
        # Ensure main image is cleared
        if 'image' in locals():
            del image

def get_facial_encodings_deepface_irq(image, country: str, model_name="ArcFace", detector_backend="retinaface"):
    logging.info(f"Type: {type(image)} | Shape: {image.shape} | Dtype: {image.dtype}")

    from deepface import DeepFace
    import numpy as np

    if image.ndim == 3 and image.shape[2] == 4:
        # Convert RGBA to BGR (DeepFace expects BGR or RGB)
        # OpenCV uses BGR by default
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    elif image.ndim == 2:
        # grayscale to BGR
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if image.dtype != np.uint8:
        image = image.astype(np.uint8)


    # DeepFace doesnt accepts 4 channel images (RGBA), so we convert to RGB or BGR
    try:
        logging.info(f"[DeepFace] Starting face extraction for {country} with model {model_name} and detector {detector_backend}")

        face_objs = DeepFace.represent(
            img_path=image,
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=False,
            align=True
        )

        logging.info(f"[DeepFace] Face extraction successful: {len(face_objs)} faces detected.")
        # logging.info(f"[DeepFace] Face details: {face_objs}")
    except Exception as e:
        logging.error(f"[DeepFace] Face extraction failed: {e}")
        return [],[]

    if not face_objs:
        logging.warning("No faces detected.")
        return [], []

    # Normalize to list
    if isinstance(face_objs, dict):
        face_objs = [face_objs]

    # Select face with largest area
    def get_area(face):
        fa = face.get("facial_area", {})
        if "w" in fa and "h" in fa:
            return fa["w"] * fa["h"]
        elif {"x", "x2", "y", "y2"}.issubset(fa):
            return (fa["x2"] - fa["x"]) * (fa["y2"] - fa["y"])
        return 0

    largest_face = max(face_objs, key=get_area)
    facial_area = largest_face.get("facial_area", {})
    confidence = largest_face.get("face_confidence", 0.0)
    embedding = np.array(largest_face["embedding"], dtype=np.float32)

    # Compute w, h from bounding box
    w, h = 0, 0
    if "w" in facial_area and "h" in facial_area:
        w, h = facial_area["w"], facial_area["h"]
    elif {"x", "x2", "y", "y2"}.issubset(facial_area): #other libraries, models returns x2,y2 instead of w,h
        w = facial_area["x2"] - facial_area["x"]
        h = facial_area["y2"] - facial_area["y"]

    # Country-specific rejection
    if country.upper() == "SDN":
        if w < 40 or h < 50:
            logging.warning(f"Rejected: SDN face too small ({w}x{h}), minimum 40x50")
            return [], []

    if confidence < 0.95:
        logging.warning(f"Rejected: low face detection confidence ({confidence:.3f})")
        return [], []

    facial_area_filtered = {}
    x = facial_area.get("x", 0)
    y = facial_area.get("y", 0)
    w = facial_area.get("w", 0)
    h = facial_area.get("h", 0)

    facial_area_filtered = [(x,y,w,h)]
    return facial_area_filtered, [embedding]


def cosine_similarity(vec1, vec2):
    # vec1 = np.array(vec1)
    # vec2 = np.array(vec2)
    #
    # if vec1.shape != vec2.shape:
    #     raise ValueError(f"Shape mismatch: {vec1.shape} vs {vec2.shape}")
    #
    # similarity = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
    # return round(float(similarity), 4)
    similarity = 1 - cosine(vec1, vec2)
    similarity = round(similarity, 5)
    similarity = min(1, similarity)
    return similarity

def extract_face_and_compute_cosine_similarity(selfie, front_face_locations, front_face_encodings):
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
            face_locations1, face_encodings1 = get_facial_encodings_deepface_irq(selfie, country='IRQ')
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

            similarity_score = cosine_similarity(face_encoding1, face_encoding2)
            # print(f"Calculated similarity score: {similarity_score}")

            return similarity_score

        except Exception as e:
            print(f"Error in extract_face_and_compute_similarity: {e}")
            import traceback
            traceback.print_exc()
            return 0


