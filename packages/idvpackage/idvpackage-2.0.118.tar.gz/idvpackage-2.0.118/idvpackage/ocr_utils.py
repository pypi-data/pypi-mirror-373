from datetime import datetime
import re
import cv2
import numpy as np
from google.cloud import vision_v1
from idvpackage.constants import *
import pkg_resources
import base64
from googletrans import Translator
from rapidfuzz import fuzz

translator = Translator()

def create_final_result(dictionary):
    result = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            sub_result = create_final_result(value)
            if sub_result == 'consider':
                return 'consider'
            elif sub_result == 'clear':
                result = 'clear'
        elif value in ['clear', 'consider', ""]:
            if value == 'consider':
                return 'consider'
            elif result != 'clear':
                result = value
    return result

def create_sub_result(document_report):
    sub_result = 'clear'

    digital_document = document_report["breakdown"]["image_integrity"]["breakdown"]["conclusive_document_quality"]["properties"].get("digital_document")
    corner_removed = document_report["breakdown"]["image_integrity"]["breakdown"]["conclusive_document_quality"]["properties"].get("corner_removed")
    watermarks_digital_text_overlay = document_report["breakdown"]["image_integrity"]["breakdown"]["conclusive_document_quality"]["properties"].get("watermarks_digital_text_overlay")
    obscured_security_features = document_report["breakdown"]["image_integrity"]["breakdown"]["conclusive_document_quality"]["properties"].get("obscured_security_features")
    screenshot = document_report["breakdown"]["visual_authenticity"]["breakdown"]["original_document_present"]["properties"].get("screenshot")
    document_on_printed_paper = document_report["breakdown"]["visual_authenticity"]["breakdown"]["original_document_present"]["properties"].get("document_on_printed_paper")
    photo_of_screen = document_report["breakdown"]["visual_authenticity"]["breakdown"]["original_document_present"]["properties"].get("photo_of_screen")
    scan = document_report["breakdown"]["visual_authenticity"]["breakdown"]["original_document_present"]["properties"].get("scan")

    consider_caution_count = sum(value == 'consider' for value in [digital_document, corner_removed, watermarks_digital_text_overlay, obscured_security_features, screenshot, document_on_printed_paper, photo_of_screen, scan])
    
    data_consistency = document_report["breakdown"]["data_consistency"]["result"]
    data_comparison = document_report["breakdown"]["data_comparison"]["result"]

    if data_consistency == 'consider' or data_comparison == 'consider':
        sub_result = 'caution'

    if consider_caution_count > 2:
        sub_result = 'suspected'

    return sub_result


def mark_clear(data, keys):
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if key in keys:
                data[key] = mark_nested_result(value, 'clear')
            else:
                data[key] = mark_clear(value, keys)
        return data
    elif isinstance(data, list):
        return [mark_clear(item, keys) for item in data]
    else:
        return data


def mark_nested_result(data, value):
    if isinstance(data, dict):
        if 'result' in data:
            data['result'] = value
        for key, val in data.items():
            if key != 'result':
                data[key] = mark_nested_result(val, value)
        return data
    elif isinstance(data, list):
        return [mark_nested_result(item, value) for item in data]
    else:
        return data
    

def age_validation(dob, age_threshold=18):
    age_val = {
        "breakdown": {
            "minimum_accepted_age": {
            "properties": {},
            "result": ""
            }
        },
        "result": ""
        }
        
    dob = get_dates_to_generic_format(dob)
    try:
        dob_date = datetime.strptime(dob, "%d/%m/%Y")
    except:
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d")
        except:
            dob_date = ''

    if dob_date:
        current_date = datetime.now()

        age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))

        if age>=age_threshold:
            age_val["breakdown"]["minimum_accepted_age"]["result"] = "clear"
            age_val["result"] = "clear"
        else:
            age_val["breakdown"]["minimum_accepted_age"]["result"] = "consider"
            age_val["result"] = "consider"
    else:
        age_val["breakdown"]["minimum_accepted_age"]["result"] = "consider"
        age_val["result"] = "consider"

    return age_val
    
def created_at():
    current_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    return current_datetime

def is_valid_and_not_expired(expiry_date, country):
    if country == 'LBN':    
        return 'clear'
        
    try:
        parsed_date = datetime.strptime(expiry_date, "%d/%m/%Y")
        current_date = datetime.now()
        
        if parsed_date < current_date:
            return 'consider'
        return 'clear'
    
    except:
        try:
            parsed_date = datetime.strptime(expiry_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            if parsed_date < current_date:
                return 'consider'
            return 'clear'

        except:
            return 'consider'

def identify_document_type(text, country, origial_text=None):
    text = text.upper()
    emirates_id_pattern = r'\b(ILARE\w*|IDARE\w*|RESIDENT IDENTITY)\b'
    iqama_id_pattern = r'KINGDOM OF SAUDI ARABIA|RESIDENT IDENTITY|MINISTRY OF INTERIOR'
    iraq_id_pattern = r'Register|Signature|Family Number|The Directorate of Nationality|IDIRQ|The Republic of Iraq|Ministry of|National Card|Iraq'
    lbn_id_pattern = r'Marital status|Family|Lebanon Republic|Republic of Lebanon'
    qtr_id_pattern = r'State of Qatar|Residency Permit|Director General of the General Department|Directorate of Passports|Passport number'
    passport_pattern = r'\b(PASSPORT|PPT)\b'
    driver_license_pattern = r'\b(DRIVER|LICENSE|DL)\b'
    
    if re.search(emirates_id_pattern, text, re.IGNORECASE):
        return "EID"

    if country == 'IRQ' and (re.search(iraq_id_pattern, text, re.IGNORECASE) or re.search(iraq_id_pattern, origial_text, re.IGNORECASE)):
        return "INC"
    
    if country == 'LBN' and re.search(lbn_id_pattern, text, re.IGNORECASE):
        return "LBN"
    
    if country == 'QAT' and re.search(qtr_id_pattern, text, re.IGNORECASE):
        return "QAT"
        
    if re.search(passport_pattern, text, re.IGNORECASE):
        return "PASSPORT"

    if re.search(driver_license_pattern, text, re.IGNORECASE):
        return "DL"

    return "Unknown"

def identify_front_id(text):
    front_id_keywords = ['Resident Identity', 'United arab emirates', 'federal authority for identity', 'ID Number', 'Kingdom of saudi arabia', 'ministry of']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id(text):
    back_id_keywords = ['ILARE', 'IDARE', 'Signature']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_front_id_iraq(text):
    front_id_keywords = ['The Republic of Iraq', 'Ministry of', 'National Card', 'Passports and Residence', 'Republic', 'Ministry', 'Iraq']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id_iraq(back_id_text, text):
    back_id_keywords = ['IDIRQ', 'Signature', 'Register', 'Family Number', 'The Directorate of Nationality', 'IDIR']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        if re.search(pattern, back_id_text, re.IGNORECASE):
            return True
        else:
            return False

def identify_front_id_lebanon(text):
    front_id_keywords = ['Lebanon Republic', 'Ministry of', 'Republic of Lebanon']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id_lebanon(text):
    back_id_keywords = ['Marital status', 'Family']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_front_id_qatar(text):
    front_id_keywords = ['State of Qatar', 'Residency Permit']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id_qatar(text):
    back_id_keywords = ['Director General of the General Department', 'Directorate of Passports', 'Passport number']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def document_on_printed_paper(image, block_size=11, c_value=2, texture_threshold=0.4, contour_area_threshold=5000):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_thresh = cv2.adaptiveThreshold(image_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, c_value)
    image_contours, _ = cv2.findContours(image_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out small noise contours
    image_paper_edges = [contour for contour in image_contours if cv2.contourArea(contour) > contour_area_threshold]

    # Calculate the percentage of paper texture in the image
    texture_ratio = len(image_paper_edges) / max(len(image_contours), 1)

    # Determine if the image contains a printed paper texture
    if texture_ratio >= texture_threshold:
        return 'consider'
    else:
        return 'clear'


def check_logo_existence_iraq(logo_content, id_card_content, threshold=3, good_mathces_filter=0.6):
    nparr_logo = np.frombuffer(logo_content, np.uint8)
    logo = cv2.imdecode(nparr_logo, cv2.IMREAD_GRAYSCALE)

    nparr_id_card = np.frombuffer(id_card_content, np.uint8)
    id_card = cv2.imdecode(nparr_id_card, cv2.IMREAD_COLOR)
    id_card_gray = cv2.cvtColor(id_card, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()

    kp1, des1 = sift.detectAndCompute(logo, None)
    kp2, des2 = sift.detectAndCompute(id_card_gray, None)

    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(des1, des2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < good_mathces_filter * n.distance:
            good_matches.append(m)

    # 40
    min_good_matches = threshold
    # min_good_matches = 3

    if len(good_matches) >= min_good_matches:
        return True
    else:
        return False


def detect_logo(client, input_image_content, country, compare_type=None, side=None):
    if country == 'UAE':
        reference_logo_path = pkg_resources.resource_filename('idvpackage', 'template_images/emirates_id_logo.jpeg')

        with open(reference_logo_path, 'rb') as logo_file:
            reference_image_content = logo_file.read()

        reference_image = vision_v1.types.Image(content=reference_image_content)
        input_image = vision_v1.types.Image(content=input_image_content)

        reference_response = client.logo_detection(image=reference_image)
        input_response = client.logo_detection(image=input_image)

        reference_logos = reference_response.logo_annotations
        input_logos = input_response.logo_annotations

        for reference_logo in reference_logos:
            for input_logo in input_logos:
                if reference_logo.description.lower() == input_logo.description.lower():
                    return 'clear'

        return 'consider'

    if country in ['IRQ', 'LBN', 'QAT'] and compare_type != 'template':
        if country == 'IRQ':
            logo_path = 'template_images/iraq_id_logo.png'
            good_mathces_filter = 0.6
        elif country == 'QAT':
            logo_path = 'template_images/qatar_id_logo.jpeg'
            good_mathces_filter = 0.7

        reference_logo_path = pkg_resources.resource_filename('idvpackage', logo_path)
        with open(reference_logo_path, 'rb') as logo_file:
            reference_image_content = logo_file.read()
        result = check_logo_existence_iraq(reference_image_content, input_image_content, 3, good_mathces_filter)

        if result:
            return 'clear'
        else:
            return 'consider'
    
    if country in ['IRQ', 'LBN', 'QAT'] and compare_type == 'template':
        if side == 'front':
            if country == 'QAT':
                threshold = 300
                front_template_path = 'template_images/qatar_front_standard_template.jpeg'
            elif country == 'IRQ':
                threshold = 40
                front_template_path = 'template_images/iraq_standard_template.png'
            else:  # LBN
                threshold = 60
                front_template_path = 'template_images/lbn_front_standard_template.png'
            reference_logo_path = pkg_resources.resource_filename('idvpackage', front_template_path)
        if side == 'back':
            if country == 'QAT':
                threshold = 235
                back_template_path = 'template_images/qatar_back_standard_template.jpeg'
            elif country == 'IRQ':
                threshold = 140
                back_template_path = 'template_images/iraq_back_standard_template.jpg'
            else:  # LBN
                threshold = 120
                back_template_path = 'template_images/lbn_back_standard_template.png'
            reference_logo_path = pkg_resources.resource_filename('idvpackage', back_template_path)

        with open(reference_logo_path, 'rb') as logo_file:
            reference_image_content = logo_file.read()

        result = check_logo_existence_iraq(reference_image_content, input_image_content, threshold)

        if result:
            return 'clear'
        else:
            return 'consider'


# def detect_logo(client, input_image_content, country):
#     if country == 'UAE':
#         reference_logo_path = pkg_resources.resource_filename('idvpackage', 'emirates_id_logo.jpeg')
    
        
#         with open(reference_logo_path, 'rb') as logo_file:
#             reference_image_content = logo_file.read()

#         reference_image = vision_v1.types.Image(content=reference_image_content)
#         input_image = vision_v1.types.Image(content=input_image_content)

#         reference_response = client.logo_detection(image=reference_image)
#         input_response = client.logo_detection(image=input_image)

#         reference_logos = reference_response.logo_annotations
#         input_logos = input_response.logo_annotations

#         for reference_logo in reference_logos:
#             for input_logo in input_logos:
#                 if reference_logo.description.lower() == input_logo.description.lower():
#                     return 'clear'

#         return 'consider'

#     if country == 'IRQ':
#         reference_logo_path = pkg_resources.resource_filename('idvpackage', 'iraq_id_logo.png')
#         result = check_logo_existence_iraq(reference_logo_path, input_image_content)

#         if result:
#             return 'clear'
#         else:
#             return 'consider'


def detect_logo_saudi(client, input_image):
    reference_logo_path = pkg_resources.resource_filename('idvpackage', 'template_images/sau_id_logo.png')
    
    with open(reference_logo_path, 'rb') as logo_file:
        reference_image_content = logo_file.read()

    reference_image = vision_v1.types.Image(content=reference_image_content)
    input_image = vision_v1.types.Image(content=input_image)

    reference_response = client.logo_detection(image=reference_image)
    input_response = client.logo_detection(image=input_image)

    reference_logos = reference_response.logo_annotations
    input_logos = input_response.logo_annotations

    for reference_logo in reference_logos:
        for input_logo in input_logos:
            if reference_logo.description.lower() == input_logo.description.lower():
                return 'clear'

    return 'consider'


def perform_feature_matching(image, template_image_path):
    template_image = cv2.imread(template_image_path, cv2.IMREAD_COLOR)

    sift = cv2.SIFT_create()

    kp1, des1 = sift.detectAndCompute(template_image, None)
    kp2, des2 = sift.detectAndCompute(image, None)

    if len(kp1) == 0 or len(kp2) == 0:
        return 0.0 
    
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    similarity_score = len(good_matches) / len(kp1)

    return similarity_score


# part of detecting screenshot - checks for time values seen on phone
def extract_time_values(text_annotations):
    time_values = []
    for annotation in text_annotations:
        text = annotation.description
        time_matches = re.findall(r'\d{1,2}:\d{2}', text)
        time_values.extend(time_matches)
    return time_values


def detect_screenshot(client, image):
    icons = 0
    battery_value_and_time = 0

    similarity_threshold = 0.45

    for filename in pkg_resources.resource_listdir('idvpackage', 'icons'):
        if filename.endswith('.png'):
            icon_path = pkg_resources.resource_filename('idvpackage', f'icons/{filename}')
            image_data = np.frombuffer(base64.b64decode(image), dtype=np.uint8)

            front_similarity_score = perform_feature_matching(image_data, icon_path)
            if front_similarity_score >= similarity_threshold:
                icons+=1

    image_data = vision_v1.Image(content=base64.b64decode(image))

    image_response = client.text_detection(image=image_data)

    image_text_annotations = image_response.text_annotations

    image_time_values = extract_time_values(image_text_annotations)

    if image_time_values:
        battery_value_and_time+=1

    if icons or battery_value_and_time:
        return 'consider'
    else:
        return 'clear'


def detect_photo_on_screen(client, image):
    flag = 'clear'

    image_data = vision_v1.Image(content=base64.b64decode(image))
    
    image_response = client.label_detection(image=image_data)
    image_labels = image_response.label_annotations

    confidence_threshold = 0.58  

    # 'display device'

    keywords = ['mobile phone', 'mobile device', 'portable communications device', 'communication device', 'smartphone', 'cell phone', 'touchscreen', 'laptop', 'notebook', 'computer', 'screen', 'gadget']

    for label in image_labels:
        description = label.description.lower()
        confidence = label.score
        # print(f"Description: {description}")
        # print(f"Confidence: {confidence}")
        if confidence >= confidence_threshold:
            match = any(fuzz.ratio(description, keyword.lower()) >= 90 for keyword in keywords)
            if match:
                return 'consider'

    return flag

def fuzzy_match_fields(field1, field2, threshold=55):
    similarity = fuzz.partial_ratio(field1, field2)
    # print(f"similarity: {similarity}")
    return similarity >= threshold

def standardize_date(input_date):
        input_formats = [
            "%Y-%m-%d", "%m-%d-%Y", "%Y%m%d",
            "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
            "%Y.%m.%d", "%d.%m.%Y", "%m.%d.%Y",
            "%Y %m %d", "%d %m %Y", "%m %d %Y",
        ]

        for format in input_formats:
            try:
                parsed_date = datetime.strptime(input_date, format)
                standardized_date = parsed_date.strftime("%d/%m/%Y")
                print(f"\n\n---------------Standardized date: { standardized_date}")
                return standardized_date
            except ValueError:
                pass

        return None

def compare_dates(date_str1, date_str2):
    date_format = "%d/%m/%Y"

    date1 = datetime.strptime(date_str1, date_format)
    date2 = datetime.strptime(date_str2, date_format)

    if date1 == date2:
        return True
    else:
        return False

def standardize_gender(gender):
    if gender == 'male' or gender == 'm':
        return 'Male'

    elif gender == 'female' or gender == 'f':
        return 'Female'

## for data comparison, accept data from dev and match with data extracted from id
def data_comparison_check(data, country):
    data_comparison = DATA_COMPARISON
    data_comparison = mark_clear(data_comparison, ['breakdown', 'result'])

    user_data = data.get('manual_input', '')

    if user_data and country not in ['IRQ', 'LBN', 'SDN', 'SYR', 'JOR', 'PSE', 'UAE']:
        if user_data.get('dob', '') and data.get('dob', ''):
            if compare_dates(get_dates_to_generic_format(data.get('dob', '')), get_dates_to_generic_format(user_data.get('dob', ''))):
                data_comparison['breakdown']['date_of_birth']['result'] = 'clear'
            else:
                data_comparison['breakdown']['date_of_birth']['result'] = 'consider'
        
        if user_data.get('gender', '') and data.get('gender', ''):    
            user_gender = standardize_gender(user_data.get('gender', '').lower())
            id_gender = standardize_gender(data.get('gender', '').lower())

            if user_gender == id_gender:
                data_comparison['breakdown']['gender']['result'] = 'clear'
            else:
                data_comparison['breakdown']['gender']['result'] = 'consider'

        # if not fuzzy_match_fields(data.get('gender', '').lower(),user_data.get('gender', '').lower()):
        #     data_comparison['breakdown']['gender']['result'] = 'consider'
    
        if country == 'IRQ':
            if data.get('doc_type') == 'national_identity_card':
                name_parts = data.get('name_en', '').split()
                if len(name_parts) >= 1:
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                else:
                    first_name, last_name = '',''

            elif data.get('doc_type') == 'passport':
                first_name = data.get('full_name', '').split()[0]
                last_name = data.get('last_name', '')

            else:
                name_parts = data.get('full_name', '').split()
                if len(name_parts) >= 1:
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                else:
                    first_name, last_name = '',''

        elif country == 'LBN':
            if data.get('doc_type') == 'passport':
                first_name = data.get('first_name', '')
                last_name = data.get('last_name', '')
            else:
                first_name = data.get('first_name_en', '')
                last_name = data.get('last_name_en', '')

        else:
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')

        if user_data.get('first_name', ''):
            # print(f'\n\n--------------------------- Extracted first name: {first_name}')
            # print(f"--------------------------- User first name: {user_data.get('first_name', '')}")

            if fuzzy_match_fields(first_name.lower(), user_data.get('first_name', '').lower()):
                data_comparison['breakdown']['first_name']['result'] = 'clear'
            else:
                data_comparison['breakdown']['first_name']['result'] = 'consider'

        if user_data.get('last_name', ''):
            # print(f"\n--------------------------- Extracted last name: {last_name}")
            # print(f"--------------------------- User last name: {user_data.get('last_name', '')}")

            if fuzzy_match_fields(last_name.lower().replace('-', '').replace('_', ''), user_data.get('last_name', '').lower().replace('-', '').replace('_', '')):
                data_comparison['breakdown']['last_name']['result'] = 'clear'
            else:
                data_comparison['breakdown']['last_name']['result'] = 'consider'
        
        if country == 'QAT':
            data_comparison['breakdown']['date_of_birth']['result'] = 'clear'
            data_comparison['breakdown']['gender']['result'] = 'clear'
            data_comparison['breakdown']['first_name']['result'] = 'clear'
            data_comparison['breakdown']['last_name']['result'] = 'clear'

    ## set default to avoid any problems of cache
    data_comparison['result'] = 'clear'

    result = create_final_result(data_comparison)    
    data_comparison['result'] = result

    # print(f"\n\n---------------------------- DATA COMPARISON: {data_comparison}")

    return data_comparison






def data_consistency_check(data, front_id_text, back_id_text, country, back_img):
    print(f"Country here: {country}")
    from deep_translator import GoogleTranslator

    data_consistency = DATA_CONSISTENCY
    data_consistency = mark_clear(data_consistency, ['breakdown', 'result'])

    if country == 'UAE' and data.get('uae_pass_data'):
        return data_consistency

    passport_data = data.get('passport')
    if passport_data:
        if not data.get('dob') == passport_data.get('passport_date_of_birth'):
            data_consistency['breakdown']['date_of_birth']['result'] = 'consider'
        
        if not fuzzy_match_fields(data.get('first_name').lower(),passport_data.get('passport_given_name').lower()):
            data_consistency['breakdown']['first_name']['result'] = 'consider'
        
        if not fuzzy_match_fields(data.get('gender').lower(),passport_data.get('passport_gender').lower()):
            data_consistency['breakdown']['gender']['result'] = 'consider'

        if not fuzzy_match_fields(data.get('last_name').lower(),passport_data.get('passport_surname').lower()):
            data_consistency['breakdown']['last_name']['result'] = 'consider'

    #### For data consistency compare data from different sources, like id and passport. 
    #### so the dob from id should match with dob extracted from passport

    if country == 'UAE':
        doc_type1 = identify_document_type(front_id_text, country)
        doc_type2 = identify_document_type(back_id_text, country)
        if doc_type1 == 'EID' or doc_type2=='EID':
            data_consistency['breakdown']['document_type']['result'] = 'clear'
        else:
            data_consistency['breakdown']['document_type']['result'] = 'consider'

    if country == 'SAU':
        doc_type1 = identify_front_id(front_id_text)
        if doc_type1:
            data_consistency['breakdown']['document_type']['result'] = 'clear'
        else:
            data_consistency['breakdown']['document_type']['result'] = 'consider'
    
    if country == 'IRQ':
        if data.get('doc_type') == 'passport':
            if 'passport' and ('iraq' or 'republic of iraq') in data.get('passport_data').lower():
                data_consistency['breakdown']['document_type']['result'] = 'clear'
            else:
                data_consistency['breakdown']['document_type']['result'] = 'clear'
        else:
            ## TODO: either completely remove this or make it efficient so we don't do the keyword checks everytime
            # try:
            #     translated_front_id_text = data['translated_front_id_text']
            #     translated_back_id_text = data['translated_back_id_text']
            # except:
            #     translated_front_id_text = GoogleTranslator('ar', 'en').translate(front_id_text)
            #     translated_back_id_text = GoogleTranslator('ar', 'en').translate(back_id_text)

            # doc_type1 = identify_document_type(translated_front_id_text, country, front_id_text)
            # doc_type2 = identify_document_type(translated_back_id_text, country, back_id_text)
            # if doc_type1 == 'INC' or doc_type2=='INC':
            #     data_consistency['breakdown']['document_type']['result'] = 'clear'
            # else:
            #     data_consistency['breakdown']['document_type']['result'] = 'consider'
            data_consistency['breakdown']['document_type']['result'] = 'clear'

        front_id_number = data.get('id_number_front', '')
        back_id_number = data.get('id_number', '')

        if front_id_number and back_id_number:
            if front_id_number != back_id_number:
                data_consistency['breakdown']['multiple_data_sources_present']['result'] = 'consider'

    if country == 'QAT':
        data_consistency['breakdown']['gender']['result'] = 'clear'
        data_consistency['breakdown']['last_name']['result'] = 'clear'
        data_consistency['breakdown']['first_name']['result'] = 'clear'
        data_consistency['breakdown']['nationality']['result'] = 'clear'
        data_consistency['breakdown']['date_of_birth']['result'] = 'clear'
        data_consistency['breakdown']['document_type']['result'] = 'clear'
        data_consistency['breakdown']['date_of_expiry']['result'] = 'clear'
        data_consistency['breakdown']['issuing_country']['result'] = 'clear'
        data_consistency['breakdown']['document_numbers']['result'] = 'clear'
        data_consistency['breakdown']['multiple_data_sources_present']['result'] = 'clear'

        id_number = data.get('id_number', '')
        serial_number = data.get('card_number', '')

        if id_number and serial_number:
            id_number_from_sr_no = serial_number[-11:]

            if id_number == id_number_from_sr_no:
                data_consistency['breakdown']['multiple_data_sources_present']['result'] = 'clear'
            else:
                print(f'Matching face from front and back')
                ## match faces from front and back
                from idvpackage.common import load_and_process_image_deepface, extract_face_and_compute_similarity
                front_face_locations, front_face_encodings = data.get('front_face_locations', []), data.get('front_face_encodings', [])
                try:
                    back_face_locations, back_face_encodings = load_and_process_image_deepface(back_img)
                    similarity = extract_face_and_compute_similarity(front_face_locations, front_face_encodings, back_face_locations, back_face_encodings)
                    print(f'\n\nSimilarity - front back: {similarity}\n')
                except Exception as e:
                    print(f'\n\nError: {e}\n')
                    similarity = 0.0
                    
                face_match = True if similarity >= 0.65 else False

                if face_match:
                    data_consistency['breakdown']['multiple_data_sources_present']['result'] = 'clear'
                else:
                    data_consistency['breakdown']['multiple_data_sources_present']['result'] = 'consider'

        else:
            data_consistency['breakdown']['multiple_data_sources_present']['result'] = 'consider'
            
        # translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        # doc_type1 = identify_document_type(front_id_text, country)
        # doc_type2 = identify_document_type(translated_back_id_text, country)
        # if doc_type1 == 'QAT' or doc_type2=='QAT':
        #     data_consistency['breakdown']['document_type']['result'] = 'clear'
        # else:
        #     data_consistency['breakdown']['document_type']['result'] = 'consider'

    if country in ['LBN', 'SDN', 'SYR', 'JOR', 'PSE']:
        data_consistency['breakdown']['document_type']['result'] = 'clear'

    ## set default to avoid any problems of cache
    data_consistency['result'] = 'clear'

    result = create_final_result(data_consistency)    
    data_consistency['result'] = result

    if country == 'QAT' and data_consistency['breakdown']['multiple_data_sources_present']['result'] != 'consider':
        data_consistency['result'] = 'clear'

    return data_consistency

def get_dates_to_generic_format(date):
    formats = ["%d/%m/%Y", "%Y/%m/%d", "%Y-%m-%d", "%d-%m-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return date

def onfido_date_format(date):
    formats = ["%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date

def data_validation_check(data, country):
    data_validation = DATA_VALIDATION
    data_validation = mark_clear(data_validation, ['breakdown', 'result'])

    try:
        dob = data.get('dob')
        # print(f"DOB: {dob}")
        dob = get_dates_to_generic_format(dob)
        parsed_date = datetime.strptime(dob, "%d/%m/%Y")
        data_validation["breakdown"]['date_of_birth']["result"] = 'clear'
    except:
        try:
            dob = data.get('dob')
            parsed_date = datetime.strptime(dob, "%Y-%m-%d")
            data_validation["breakdown"]['date_of_birth']["result"] = 'clear'
        except:
            data_validation["breakdown"]['date_of_birth']["result"] = 'consider'

    try:
        doe = data.get('expiry_date')
        doe = get_dates_to_generic_format(doe)
        parsed_date = datetime.strptime(doe, "%d/%m/%Y")
        data_validation["breakdown"]['expiry_date']["result"] = 'clear'
    except:
        try:
            doe = data.get('expiry_date')
            parsed_date = datetime.strptime(doe, "%Y-%m-%d")
            data_validation["breakdown"]['expiry_date']["result"] = 'clear'
        except:
            data_validation["breakdown"]['expiry_date']["result"] = 'consider'

    gender = data.get('gender', '')
    
    if gender.isalpha() and (gender.lower()=='male' or gender.lower()=='female' or gender.lower()=='m' or gender.lower()=='f'):
        data_validation["breakdown"]['gender']["result"] = 'clear'
    else:
        data_validation["breakdown"]['gender']["result"] = 'consider'
    
    if country == 'LBN' and data.get('doc_type') == 'national_identity_card':
        data_validation["breakdown"]['expiry_date']["result"] = 'clear'
        data_validation['breakdown']['valid_nationality']["result"] = 'clear'
        data_validation['breakdown']['document_expiration']["result"] = 'clear'
    else:
        data_validation['breakdown']['valid_nationality']["result"] = data.get('valid_nationality')

    if country in ['SDN', 'SYR', 'JOR', 'PSE']:
        data_validation['breakdown']['valid_nationality']["result"] = data.get('valid_nationality')
        data_validation["breakdown"]['document_numbers']["result"] = 'clear'

    if country == 'UAE' or country == 'IRQ':
        if data.get('doc_type') == 'national_identity_card':
            doc_no = data.get('card_number', '')
            if len(doc_no)==9:
                data_validation["breakdown"]['document_numbers']["result"] = 'clear'
            else:
                data_validation["breakdown"]['document_numbers']["result"] = 'consider'
        else:
            data_validation["breakdown"]['document_numbers']["result"] = 'clear'

    doe = data.get('expiry_date', '')
    expiry_result = is_valid_and_not_expired(get_dates_to_generic_format(doe), country)
    data_validation['breakdown']['document_expiration']["result"] = expiry_result

    mrz = data.get('mrz', '')
    mrz1 = data.get('mrz1', '')
    mrz2 = data.get('mrz2', '')
    mrz3 = data.get('mrz3', '')

    if data.get('doc_type') == 'passport':
        if mrz and mrz1 and mrz2:
            data_validation["breakdown"]['mrz']["result"] = 'clear'
        else:
            data_validation["breakdown"]['mrz']["result"] = 'consider'
    else:
        if not data.get('uae_pass_data', ''):
            if len(mrz) == 1 and mrz1 and mrz2 and mrz3:
                data_validation["breakdown"]['mrz']["result"] = 'clear'
            else:
                data_validation["breakdown"]['mrz']["result"] = 'consider'
        else:
            data_validation["breakdown"]['mrz']["result"] = 'clear'

    if country == 'LBN' and data.get('doc_type') == 'national_identity_card':
        doc_no = data.get('id_number', '')
        if len(doc_no)>=10 and len(doc_no)<13:
            data_validation["breakdown"]['document_numbers']["result"] = 'clear'
        else:
            data_validation["breakdown"]['document_numbers']["result"] = 'consider'
        
        data_validation["breakdown"]['mrz']["result"] = 'clear'

    if country == 'QAT':
        data_validation["breakdown"]['document_numbers']["result"] = 'clear'
        data_validation["breakdown"]['gender']["result"] = 'clear'
        data_validation["breakdown"]['mrz']["result"] = 'clear'
        data_validation["breakdown"]['document_expiration']["result"] = 'clear'
        data_validation['breakdown']['valid_nationality']["result"] = 'clear'
        data_validation["breakdown"]['date_of_birth']["result"] = 'clear'
        data_validation["breakdown"]['expiry_date']["result"] = 'clear'

    if country == 'IRQ' and data.get('doc_type') == 'national_identity_card' and not data.get('card_number'):
        doc_no = data.get('card_number_front', '')
        if len(doc_no)==9:
            data_validation["breakdown"]['document_numbers']["result"] = 'clear'
        else:
            data_validation["breakdown"]['document_numbers']["result"] = 'consider'

    # print(f"\n\n------------------------- DATA VAL: {data_validation}")
    
    ## set default to avoid any problems of cache
    data_validation['result'] = 'clear'

    result = create_final_result(data_validation)
    data_validation['result'] = result

    # if data_validation["breakdown"]['date_of_birth']["result"]=='clear' and data_validation["breakdown"]['expiry_date']["result"]=='clear' and data_validation["breakdown"]['gender']["result"]=='clear' and data_validation["breakdown"]['mrz']["result"]=='clear':
    #     data_validation['result'] = 'clear'

    return data_validation

## pending
def image_integrity_check(data, front_id_text, back_id_text, coloured, blurred, glare, missing_fields, country):
    from deep_translator import GoogleTranslator
    image_integrity = IMAGE_INTEGRITY
    image_integrity = mark_clear(image_integrity, ['breakdown', 'result'])


    image_integrity['breakdown']['colour_picture']['result'] = coloured
    image_integrity['breakdown']['conclusive_document_quality']['properties']['corner_removed'] = is_valid_and_not_expired(get_dates_to_generic_format(data.get('expiry_date', '')), country)
    image_integrity['breakdown']['conclusive_document_quality']['properties']['abnormal_document_features'] = blurred
    image_integrity['breakdown']['image_quality']['properties']['blurred_photo'] = blurred
    image_integrity['breakdown']['image_quality']['properties']['covered_photo'] = missing_fields
    image_integrity['breakdown']['image_quality']['properties']['cut_off_document'] = missing_fields
    image_integrity['breakdown']['image_quality']['properties']['glare_on_photo'] = glare
    image_integrity['breakdown']['image_quality']['properties']['other_photo_issue'] =  missing_fields
    
    ## set default to avoid any problems of cache
    image_integrity['breakdown']['image_quality']['result'] = 'clear'

    image_quality_result = create_final_result(image_integrity['breakdown']['image_quality'])
    image_integrity['breakdown']['image_quality']['result'] = image_quality_result

    f_result = 'clear'
    if data.get('doc_type') == 'national_identity_card':
        f_result = identify_front_id(front_id_text)
    
    front_doc_on_pp = data.get('front_doc_on_pp')

    if country == 'UAE' and not data.get('uae_pass_data', ''):
        b_result = identify_back_id(back_id_text)

        if back_id_text and b_result:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        else:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'

        if f_result and b_result:
            image_integrity['breakdown']['supported_document']['result'] = 'clear'
        else:
            image_integrity['breakdown']['supported_document']['result'] = 'consider'
    
    if country == 'SAU':
        if f_result:
            image_integrity['breakdown']['supported_document']['result'] = 'clear'
        else:
            image_integrity['breakdown']['supported_document']['result'] = 'consider'
        
        image_integrity['breakdown']['conclusive_document_quality']['properties']['digital_document'] = front_doc_on_pp

    if country == 'IRQ' and data.get('doc_type') == 'national_identity_card':
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        image_integrity['breakdown']['supported_document']['result'] = 'clear'
        
        ## TODO: either completely remove this or make it efficient so we don't do the keyword checks everytime
        # try:
        #     translated_back_id_text = data['translated_back_id_text']
        # except:
        #     translated_back_id_text = GoogleTranslator('ar', 'en').translate(back_id_text)

        # b_result = identify_back_id_iraq(back_id_text, translated_back_id_text)

        # if back_id_text and b_result:
        #     image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        # else:
        #     image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'
        
        # try:
        #     translated_front_id_text = translator.translate(front_id_text, src='ar', dest='en').text 
        # except:
        #     translated_front_id_text = GoogleTranslator('ar', 'en').translate(front_id_text)

        # f_result = identify_front_id_iraq(translated_front_id_text)

        # if f_result and b_result:
        #     image_integrity['breakdown']['supported_document']['result'] = 'clear'
        # else:
        #     image_integrity['breakdown']['supported_document']['result'] = 'consider'

    elif country == 'IRQ' and data.get('doc_type') == 'passport':
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        if 'passport' and ('iraq' or 'republic of iraq') in data.get('passport_data').lower():
            image_integrity['breakdown']['supported_document']['result'] = 'clear'

    if country == 'LBN' and data.get('doc_type') == 'national_identity_card':
        try:
            translated_back_id_text = data['translated_back_id_text']
        except:
            translated_back_id_text = GoogleTranslator('ar', 'en').translate(back_id_text)

        b_result = identify_back_id_lebanon(translated_back_id_text)

        if back_id_text and b_result:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        else:
            image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'
        
        try:
            translated_front_id_text = data['translated_front_id_text']
        except:
            translated_front_id_text = GoogleTranslator('ar', 'en').translate(front_id_text)
            
        f_result = identify_front_id_lebanon(translated_front_id_text)

        if f_result and b_result:
            image_integrity['breakdown']['supported_document']['result'] = 'clear'
        else:
            image_integrity['breakdown']['supported_document']['result'] = 'consider'

    elif country == 'LBN' and data.get('doc_type') == 'passport':
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        if 'passport' and ('lebanon' or 'republic of lebanon') in data.get('passport_data').lower():
            image_integrity['breakdown']['supported_document']['result'] = 'clear'

    image_integrity['breakdown']['conclusive_document_quality']['properties']['watermarks_digital_text_overlay'] = data.get('front_logo_result')
    # image_integrity['breakdown']['image_quality']['properties']['blurred_photo'] = blurred
    # image_integrity['breakdown']['image_quality']['properties']['glare_on_photo'] = glare

    if country == 'QAT':
        image_integrity['breakdown']['image_quality']['properties']['blurred_photo'] = 'clear'
        image_integrity['breakdown']['image_quality']['properties']['covered_photo'] = 'clear'
        image_integrity['breakdown']['image_quality']['properties']['cut_off_document'] = 'clear'
        image_integrity['breakdown']['image_quality']['properties']['glare_on_photo'] = 'clear'
        image_integrity['breakdown']['image_quality']['properties']['other_photo_issue'] =  'clear'

        image_integrity['breakdown']['colour_picture']['result'] = 'clear'

        image_integrity['breakdown']['supported_document']['result'] = 'clear'

        image_integrity['breakdown']['conclusive_document_quality']['properties']['watermarks_digital_text_overlay'] = 'clear'
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        image_integrity['breakdown']['conclusive_document_quality']['properties']['corner_removed'] = 'clear'
        image_integrity['breakdown']['conclusive_document_quality']['properties']['abnormal_document_features'] = 'clear'
        image_integrity['breakdown']['conclusive_document_quality']['properties']['digital_document'] = 'clear'
        image_integrity['breakdown']['conclusive_document_quality']['properties']['punctured_document'] = 'clear'
        image_integrity['breakdown']['conclusive_document_quality']['properties']['obscured_data_points'] = 'clear'
        image_integrity['breakdown']['conclusive_document_quality']['properties']['obscured_security_features'] = 'clear'

    image_quality_result = create_final_result(image_integrity['breakdown']['image_quality'])
    conclusive_document_quality_result = create_final_result(image_integrity['breakdown']['conclusive_document_quality'])

    ## set default to avoid any problems of cache
    image_integrity['breakdown']['conclusive_document_quality']["result"] = 'clear'

    image_integrity['breakdown']['conclusive_document_quality']["result"] = conclusive_document_quality_result

    colour_picture_result = image_integrity['breakdown']['colour_picture']['result']
    supported_documents_result = image_integrity['breakdown']['supported_document']['result']

    back_doc_on_pp = data.get('doc_on_pp')
    if front_doc_on_pp == 'consider' or back_doc_on_pp == 'consider':
        image_integrity['breakdown']['conclusive_document_quality']['properties']['digital_document'] = 'consider'

    if country == 'QAT' or country == 'IRQ' or country == 'LBN':
        image_integrity['breakdown']['conclusive_document_quality']['properties']['digital_document'] = 'clear'

        # translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        # b_result = identify_back_id_qatar(translated_back_id_text)

        # if back_id_text and b_result:
            # image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        # else:
        #     image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'
        
        # f_result = identify_front_id_qatar(front_id_text)

        # if f_result and b_result:
        #     image_integrity['breakdown']['supported_document']['result'] = 'clear'
        # else:
        #     image_integrity['breakdown']['supported_document']['result'] = 'consider'


    if country in ['SDN', 'SYR', 'JOR', 'PSE']:
        image_integrity['breakdown']['supported_document']['result'] = 'clear'
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
        image_integrity['breakdown']['image_quality']['properties']['cut_off_document'] = 'clear'
        image_integrity['breakdown']['image_quality']['properties']['other_photo_issue'] =  'clear'
        image_integrity['breakdown']['image_quality']['properties']['blurred_photo'] = blurred
        image_integrity['breakdown']['conclusive_document_quality']['properties']['digital_document'] = 'clear'

    ## set default to avoid any problems of cache
    image_integrity['result'] = 'clear'

    if image_quality_result == 'consider' or conclusive_document_quality_result == 'consider' or supported_documents_result == 'consider':
        image_integrity['result'] = 'consider'

    #since we do not have image integrity attributes extracted from front/back/passports of IRQ IDs, we can bypass this check here.
    if country=='IRQ':
        image_integrity['result']='clear'

    return image_integrity

def visual_authenticity_check(data, front_id_text, back_id_text, selfie, facial_similarity, face_match_threshold, country):
    from deep_translator import GoogleTranslator
    visual_authenticity = VISUAL_AUTHENTICITY
    visual_authenticity = mark_clear(visual_authenticity, ['breakdown', 'result'])

    if np.any(selfie):
        ## if facial similarity is matching the threshold or even if facial similarity comes above 40 then we say face was detected - approach can be changed
        if facial_similarity > face_match_threshold:
            visual_authenticity['breakdown']['face_detection'] = 'clear'
            visual_authenticity['breakdown']['security_features'] = 'clear'
        else:
            visual_authenticity['breakdown']['face_detection'] = 'consider'
            visual_authenticity['breakdown']['security_features'] = 'consider'
    else:
        visual_authenticity['breakdown']['face_detection'] = ''
        visual_authenticity['breakdown']['security_features'] = ''
    
    if data.get('doc_type') == 'national_identity_card':
        doc_type1 = identify_document_type(front_id_text, country, front_id_text)

    front_doc_on_pp = data.get('front_doc_on_pp')
    front_screenshot = data.get('front_screenshot_result')
    front_photo_on_screen_result = data.get('front_photo_on_screen_result')

    if country != 'SAU':
        back_screenshot = data.get('screenshot_result')
        if front_screenshot == 'consider' or back_screenshot == 'consider':
            visual_authenticity['breakdown']['original_document_present']['properties']['screenshot'] = 'consider'

        back_photo_on_screen_result = data.get('photo_on_screen_result')
        if front_photo_on_screen_result == 'consider' or back_photo_on_screen_result == 'consider':
            visual_authenticity['breakdown']['original_document_present']['properties']['photo_of_screen'] = 'consider'

    if country == 'UAE' and not data.get('uae_pass_data', ''):
        doc_type2 = identify_document_type(back_id_text, country)
        if doc_type1 == 'EID' and doc_type2 == 'EID':
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        else:
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'

    if country == 'SAU':
        if identify_front_id(front_id_text):
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        else:
            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'
    
        visual_authenticity['breakdown']['original_document_present']['properties']['document_on_printed_paper'] = front_doc_on_pp
        visual_authenticity['breakdown']['original_document_present']['properties']['screenshot'] = front_screenshot
        visual_authenticity['breakdown']['original_document_present']['properties']['photo_of_screen'] = front_photo_on_screen_result

    if country == 'IRQ':
        if data.get('doc_type') == 'passport':
            if 'passport' and ('iraq' or 'republic of iraq') in data.get('passport_data').lower():
                visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
            else:
                visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        else:
            ## TODO: either completely remove this or make it efficient so we don't do the keyword checks everytime
            # try:
            #     translated_front_id_text = data['translated_front_id_text']
            #     translated_back_id_text = data['translated_back_id_text']
            # except:
            #     translated_front_id_text = GoogleTranslator('ar', 'en').translate(front_id_text)
            #     translated_back_id_text = GoogleTranslator('ar', 'en').translate(back_id_text)

            # doc_type1 = identify_document_type(translated_front_id_text, country, front_id_text)
            # doc_type2 = identify_document_type(translated_back_id_text, country, back_id_text)
            # if doc_type1 == 'INC' and doc_type2 == 'INC':
            #     visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
            # else:
            #     visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'

            visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
            visual_authenticity['breakdown']['template']['result'] = data.get('front_template_result')
            visual_authenticity['breakdown']['digital_tampering']['result'] = data.get('tampering_result')

    if country == 'LBN':
        if data.get('doc_type') == 'passport':
            if 'passport' and ('lebanon' or 'republic of lebanon') in data.get('passport_data').lower():
                visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
            else:
                visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'
        else:
            try:
                translated_front_id_text = translator.translate(front_id_text, src='ar', dest='en').text 
                translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
            except:
                translated_front_id_text = GoogleTranslator('ar', 'en').translate(front_id_text)
                translated_back_id_text = GoogleTranslator('ar', 'en').translate(back_id_text)

            doc_type1 = identify_document_type(translated_front_id_text, country, front_id_text)
            doc_type2 = identify_document_type(translated_back_id_text, country, back_id_text)
            if doc_type1 == 'INC' and doc_type2 == 'INC':
                visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
            else:
                visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'

            visual_authenticity['breakdown']['template']['result'] = data.get('front_template_result')
            visual_authenticity['breakdown']['digital_tampering']['result'] = data.get('tampering_result')

    if country == 'LBN':
        visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        visual_authenticity['breakdown']['original_document_present']['properties']['screenshot'] = 'clear'
        visual_authenticity['breakdown']['digital_tampering']['result'] = 'clear'
        visual_authenticity['breakdown']['template']['result'] = 'clear'

    if country == 'QAT':
        visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        visual_authenticity['breakdown']['original_document_present']['properties']['screenshot'] = 'clear'
        visual_authenticity['breakdown']['original_document_present']['properties']['photo_of_screen'] = 'clear'
        visual_authenticity['breakdown']['original_document_present']['properties']['document_on_printed_paper'] = 'clear'
        visual_authenticity['breakdown']['digital_tampering']['result'] = 'clear'
        visual_authenticity['breakdown']['template']['result'] = 'clear'

        # translated_back_id_text = translator.translate(back_id_text, src='ar', dest='en').text 
        
        # doc_type1 = identify_document_type(front_id_text, country)
        # doc_type2 = identify_document_type(translated_back_id_text, country)
        # if doc_type1 == 'QAT' and doc_type2 == 'QAT':
            # visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        # else:
            # visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'

    if country in ['SDN', 'SYR', 'JOR', 'PSE']:
        visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
        visual_authenticity['breakdown']['original_document_present']['properties']['screenshot'] = 'clear'
        visual_authenticity['breakdown']['digital_tampering']['result'] = 'clear'
        visual_authenticity['breakdown']['template']['result'] = 'clear'

    original_document_present_result  = create_final_result(visual_authenticity['breakdown']['original_document_present'])
    visual_authenticity['breakdown']['original_document_present']['result'] = original_document_present_result

    ## set default to avoid any problems of cache
    visual_authenticity['result'] = 'clear'

    final_result = create_final_result(visual_authenticity)
    visual_authenticity['result'] = final_result

    # print(f"\n\n------------------------- VISUAL AUTHENTICITY DOC: {visual_authenticity}")

    back_doc_on_pp = data.get('doc_on_pp')
    if front_doc_on_pp == 'consider' or back_doc_on_pp == 'consider':
        visual_authenticity['breakdown']['original_document_present']['properties']['document_on_printed_paper'] = 'consider'

    if country == 'QAT':
        visual_authenticity['breakdown']['original_document_present']['result'] = 'clear'
        visual_authenticity['breakdown']['original_document_present']['properties']['document_on_printed_paper'] = 'clear'
        visual_authenticity['result'] = 'clear'

    return visual_authenticity

def main_details(data, country):
    main_properties = {}
    
    main_properties['document_numbers']= []

    try:
        # Add handling for UAE Pass data
        uae_pass_data = data.get('uae_pass_data', {})
        if uae_pass_data and country == 'UAE':
            # Handle Emirates ID data
            if uae_pass_data.get('IDN'):
                id_data_t = {
                    "type": "type",
                    "value": "personal_number"
                }
                id_data_v = {
                    "type": "value",
                    "value": uae_pass_data['IDN']
                }
                main_properties['document_numbers'].append(id_data_t)
                main_properties['document_numbers'].append(id_data_v)
                main_properties['id_number'] = uae_pass_data['IDN']

            # Handle name fields
            if uae_pass_data.get('nameEn'):
                name_parts = uae_pass_data['nameEn'].split()
                # print(f"NAME PARTS: {name_parts}")
                if len(name_parts) >= 1:
                    main_properties['first_name'] = name_parts[0]
                    main_properties['last_name'] = name_parts[-1] if len(name_parts) > 1 else ''
                main_properties['name'] = uae_pass_data['nameEn']
                main_properties['name_ar'] = uae_pass_data.get('nameAr', '')

            # Handle other Emirates ID fields
            if uae_pass_data.get('nationalityEn'):
                main_properties['nationality'] = uae_pass_data['nationalityEn']
                main_properties['nationality_ar'] = uae_pass_data.get('nationalityAr', '')
                main_properties['nationality_code'] = uae_pass_data.get('nationalityCode', '')
            
            if uae_pass_data.get('genderEn'):
                main_properties['gender'] = uae_pass_data['genderEn']
                main_properties['gender_code'] = uae_pass_data.get('genderCode', '')

            if uae_pass_data.get('DateOfBirth'):
                main_properties['date_of_birth'] = onfido_date_format(get_dates_to_generic_format(uae_pass_data['DateOfBirth']))

            if uae_pass_data.get('expiryDate'):
                main_properties['date_of_expiry'] = onfido_date_format(get_dates_to_generic_format(uae_pass_data['expiryDate']))

            # Handle Resident Visa data
            if uae_pass_data.get('fileNumber'):
                file_number_t = {
                    "type": "type",
                    "value": "file_number"
                }
                file_number_v = {
                    "type": "value",
                    "value": str(uae_pass_data['fileNumber'])
                }
                main_properties['document_numbers'].append(file_number_t)
                main_properties['document_numbers'].append(file_number_v)
                main_properties['file_number'] = str(uae_pass_data['fileNumber'])

            if uae_pass_data.get('passportNumber'):
                passport_data_t = {
                    "type": "type",
                    "value": "passport_number"
                }
                passport_data_v = {
                    "type": "value",
                    "value": uae_pass_data['passportNumber']
                }
                main_properties['document_numbers'].append(passport_data_t)
                main_properties['document_numbers'].append(passport_data_v)
                main_properties['passport_number'] = uae_pass_data['passportNumber']

            # Additional Visa fields
            if uae_pass_data.get('professionEn'):
                main_properties['occupation'] = uae_pass_data['professionEn']
                main_properties['occupation_ar'] = uae_pass_data.get('professionAr', '')
                main_properties['profession_code'] = uae_pass_data.get('professionCode', '')

            if uae_pass_data.get('sponsorEn'):
                main_properties['family_sponsor'] = uae_pass_data['sponsorEn']
                main_properties['sponsor_ar'] = uae_pass_data.get('sponsorAr', '')
                main_properties['sponsor_number'] = uae_pass_data.get('sponsorNo', '')

            if uae_pass_data.get('issuePlaceEn'):
                main_properties['issuing_place'] = uae_pass_data['issuePlaceEn']
                main_properties['issuing_place_ar'] = uae_pass_data.get('issuePlaceAr', '')

            if uae_pass_data.get('dateOfIssue'):
                main_properties['issue_date'] = onfido_date_format(get_dates_to_generic_format(uae_pass_data['dateOfIssue']))

            # Additional fields
            main_properties['accompanied_by'] = uae_pass_data.get('AccompaniedBy', '')
            main_properties['document_type_code'] = uae_pass_data.get('documentTypeCode', '')
            main_properties['document_name_en'] = uae_pass_data.get('nameOfDocEn', '')
            main_properties['document_name_ar'] = uae_pass_data.get('nameOfDocAr', '')

            # Set document type based on available data
            if uae_pass_data.get('nameOfDocEn'):
                main_properties['document_type'] = uae_pass_data['nameOfDocEn'].lower().replace(' ', '_')
            else:
                main_properties['document_type'] = 'national_identity_card'

            return main_properties

        dob = get_dates_to_generic_format(data.get('dob'))
        doe = get_dates_to_generic_format(data.get('expiry_date', ''))
        main_properties['date_of_birth'] = onfido_date_format(dob)
        main_properties['date_of_expiry'] = onfido_date_format(doe)

        if data.get('card_number'):
            card_data_t = {
            "type": "type",
            "value": "document_number"
            }

            card_data_v = {
                "type": "value",
                "value": data['card_number']
            }

            main_properties['document_numbers'].append(card_data_t)
            main_properties['document_numbers'].append(card_data_v)

        if data.get('id_number'):
            id_data_t = {
                        "type": "type",
                        "value": "personal_number"
                    }
            id_data_v = {
                        "type": "value",
                        "value": data['id_number']
                    }
                
            main_properties['document_numbers'].append(id_data_t) 
            main_properties['document_numbers'].append(id_data_v)

        elif data.get('passport_number', None):
            id_data_t = {
                "type": "type",
                "value": "personal_number"
            }
            id_data_v = {
                "type": "value",
                "value": data['passport_number']
            }

            main_properties['document_numbers'].append(id_data_t)
            main_properties['document_numbers'].append(id_data_v)


        else:
            id_data_t = {
                        "type": "type",
                        "value": "personal_number"
                    }
            id_data_v = {
                        "type": "value",
                        "value": ""
                    }
                
            main_properties['document_numbers'].append(id_data_t) 
            main_properties['document_numbers'].append(id_data_v)
        
        # main_properties['document_type'] = 'national_identity_card'
        # main_properties['name'] = data.get('name')
        # main_properties['first_name'] = data.get('first_name', '')
        # main_properties['gender'] = data.get('gender', '')
        # main_properties['issuing_country'] = data.get('issuing_place', '')
        # main_properties['last_name'] = data.get('last_name', '')
        # main_properties['mrz_line1'] = data.get('mrz1', '')
        # main_properties['mrz_line2'] = data.get('mrz2', '')
        # main_properties['mrz_line3'] = data.get('mrz3', '')
        # main_properties['nationality'] = data.get('nationality')

        keys = ['name', 'first_name', 'gender', 'issuing_place', 'last_name', 'nationality', 'issuing_country', 'occupation', 'employer', 'family_sponsor']

        main_properties['document_type'] = data.get('doc_type', '')
        main_properties['mrz_line1'] = data.get('mrz1', '')
        main_properties['mrz_line2'] = data.get('mrz2', '')
        main_properties['mrz_line3'] = data.get('mrz3', '')

        for key in keys:
            main_properties[key] = data.get(key, '')
        
        if country in ['IRQ', 'LBN', 'QAT', 'SDN', 'SYR', 'JOR', 'PSE']:
            if country == 'IRQ':
                main_prop_data = {}
                if data.get('doc_type') == 'passport':
                    keys_to_remove = ['issuing_place', 'occupation', 'employer', 'mrz_line3', 'family_sponsor', 'issuing_authority_en', 'place_of_birth_en', 'gender_ar', 'name_en', 'name', 'first_name']
                    keys = ['full_name', 'id_number', 'mrz', 'issue_date','issuing_authority', 'mother_name', 'place_of_birth', 'mother_first_name', 'mother_first_name_en', 'mother_last_name', 'mother_last_name_en']
                else:
                    keys_to_remove = ['occupation', 'employer', 'family_sponsor', 'issuing_place']
                    keys = ['name_en', 'name', 'first_name', 'father_name', 'third_name', 'mother_first_name', 'mother_last_name', 'last_name', 'first_name_en', 'father_name_en', 'last_name_en', 'third_name_en', 'mother_first_name_en', 'mother_last_name_en', 'issuing_authority', 'nationality', 'gender', 'issuing_country', 'gender_ar', 'mrz', 'place_of_birth', 'issuing_authority_en', 'place_of_birth_en', "issue_date", "id_number", "card_number", 'family_number', 'family_number_en']

            if country == 'LBN':
                main_prop_data = {}
                keys_to_remove = ['name', 'issuing_place', 'occupation', 'employer', 'mrz_line3', 'family_sponsor']
                if data.get('doc_type') == 'passport':
                    keys = ['first_name', 'father_name', 'mother_name', 'last_name', 'id_number', 'issue_date', 'mrz', 'issuing_country', 'registry_place_and_number', 'place_of_birth']
                else:
                    # keys = ['father_name', 'last_name', 'name_en', 'first_name_en', 'fathers_name_en', 'last_name_en', 'gender_ar', 'place_of_birth', 'issue_date', 'issue_date_ar', 'card_number_ar', 'id_number_ar']
                    keys = ['name', 'name_en', 'first_name', 'father_name', 'last_name', 'first_name_en', 'father_name_en', 'last_name_en', 'mother_name_en', 'gender_ar', 'place_of_birth', 'place_of_birth_en', 'issue_date', 'issue_date_ar', 'card_number_ar', 'id_number_ar', 'issuing_country', 'nationality']
                    keys_to_remove = ['issuing_place', 'mrz_line1', 'mrz_line2', 'mrz_line3', 'family_sponsor', 'nationality', 'occupation', 'employer']

            if country == 'QAT':
                main_prop_data = {}
                keys_to_remove = ['gender', 'issuing_place', 'mrz_line1', 'mrz_line2', 'mrz_line3', 'name_en', 'family_sponsor']
                keys = ['passport_number', 'name_ar', 'passport_expiry', 'occupation', 'employer', 'employer_en', 'occupation_en']
            
            if country == 'SDN':
                main_prop_data = {}
                keys_to_remove = ['name', 'issuing_place', 'employer','mrz_line3', 'family_sponsor', 'first_name', 'last_name', 'father_name', 'mother_name']
                if data.get('doc_type') == 'passport':
                    keys = ['full_name_generic', 'name_ar', 'first_name', 'last_name', 'middle_name', 'first_name_ar', 'last_name_ar', 'middle_name_ar', 'gender', 'place_of_birth', 'place_of_issue', 'passport_number_mrz', 'national_number', 'issuance_date', 'issue_date', 'mrz', 'nationality', 'issuing_country']
                else:
                    # keys = ['father_name', 'last_name', 'name_en', 'first_name_en', 'fathers_name_en', 'last_name_en', 'gender_ar', 'place_of_birth', 'issue_date', 'issue_date_ar', 'card_number_ar', 'id_number_ar']
                    keys = ['full_name_generic', 'name_ar', 'nationality', 'gender', 'place_of_birth', 'place_of_birth_en', 'id_number', 'first_name_ar','last_name_ar','middle_name_ar','occupation', 'occupation_en', 'occupation_ar','issue_date', 'issuance_date', 'first_name', 'middle_name', 'last_name', 'issuing_country']
                    keys_to_remove = ['issuing_place', 'family_sponsor', 'employer', 'first_name', 'last_name', 'father_name', 'mother_name', 'place_of_issue']

            if country == 'SYR':
                main_prop_data = {}
                keys_to_remove = ['name', 'issuing_place', 'occupation', 'employer', 'mrz_line3', 'family_sponsor', 'issuing_country']
                if data.get('doc_type') == 'passport':
                    keys = ['full_name', 'first_name', 'last_name', 'father_name', 'mother_name', 'place_of_birth', 'place_of_issue', 'dob', 'nationality', 'gender', 'passport_number', 'issue_number', 'issuing_date', 'national_number', 'mrz1', 'mrz2', 'mrz', 'issuing_country']

            if country == 'JOR':
                main_prop_data = {}
                keys_to_remove = ['name', 'occupation', 'employer', 'mrz_line3', 'family_sponsor']
                if data.get('doc_type') == 'passport':
                    keys = ['full_name', 'first_name', 'last_name', 'father_name', 'mother_name', 'place_of_birth', 'dob', 'issuing_date', 'nationality', 'gender', 'place_of_issue', 'passport_number', 'mrz1', 'mrz2', 'mrz', 'issuing_country']

            if country == 'PSE':
                main_prop_data = {}
                keys_to_remove = ['name', 'issuing_place', 'occupation', 'employer', 'mrz_line3', 'family_sponsor']
                if data.get('doc_type') == 'passport':
                    keys = ['full_name', 'first_name', 'last_name', 'mother_name', 'place_of_birth', 'dob', 'issuing_date', 'nationality', 'gender', 'place_of_issue', 'passport_number', 'id_number', 'mrz1', 'mrz2', 'mrz', 'issuing_country']

            for key in keys:
                main_prop_data[key] =  data.get(key, '')

            if keys_to_remove:
                for key in keys_to_remove:
                    if key in main_properties:
                        del main_properties[key]

            main_properties.update(main_prop_data)

            if main_properties.get('issue_date', ''):
                main_properties['issue_date'] = onfido_date_format(get_dates_to_generic_format(main_properties['issue_date']))

            if not data.get('card_number') and data.get('card_number_front'):
                card_data_t = {
                "type": "type",
                "value": "document_number"
                }

                card_data_v = {
                    "type": "value",
                    "value": data['card_number_front']
                }

                main_properties['document_numbers'].append(card_data_t)
                main_properties['document_numbers'].append(card_data_v)

            if not data.get('id_number') and data.get('id_number_front'):
                id_data_t = {
                            "type": "type",
                            "value": "personal_number"
                        }
                id_data_v = {
                            "type": "value",
                            "value": data['id_number_front']
                        }
                    
                main_properties['document_numbers'].append(id_data_t) 
                main_properties['document_numbers'].append(id_data_v) 
            
            if country == 'IRQ' and data.get('id_number', '') and data.get('id_number_front', ''):
                if len(data['id_number']) < len(data['id_number_front']):
                    main_properties['document_numbers'][3]['value'] = data['id_number_front']
                    main_properties['id_number'] = data['id_number_front']

            ## Override NFC DATA FOR IRQ
            # if country == 'IRQ' and data.get('nfc_data', ''):
            #     nfc_data = data['nfc_data']

            #     print(f'\nNFC DATA received inside IDV package: {nfc_data}\n')
            #     ## ID NUMBER FROM NFC DATA
            #     try:
            #         if len(main_properties['document_numbers']) == 4:
            #             if nfc_data.get('serialNumber', ''):
            #                 main_properties['document_numbers'][1]['value'] = nfc_data['serialNumber']
            #                 main_properties['card_number'] = nfc_data['serialNumber']
            #             if nfc_data.get('personalNumber', ''):
            #                 main_properties['document_numbers'][3]['value'] = nfc_data['personalNumber']
            #                 main_properties['id_number'] = nfc_data['personalNumber']

            #         elif len(main_properties['document_numbers']) < 4:
            #             main_properties['document_numbers'].append({
            #                 "type": "type",
            #                 "value": "personal_number"
            #             })
            #             main_properties['document_numbers'].append({
            #                 "type": "value",
            #                 "value": nfc_data['personalNumber']
            #             })

            #     except:
            #         pass
                
            #     if nfc_data.get('gender', ''):
            #         main_properties['gender'] = nfc_data['gender']
                
            #     if nfc_data.get('name', ''):
            #         main_properties['first_name'] = nfc_data['name'].strip()

            #     if nfc_data.get('surname', ''):
            #         main_properties['last_name'] = nfc_data['surname'].strip()
                
            #     if nfc_data.get('issuerAuthority', ''):
            #         main_properties['issuing_authority'] = nfc_data['issuerAuthority']
                
            #     if nfc_data.get('birthDate', ''):
            #         try:
            #             main_properties['date_of_birth'] = datetime.strptime(nfc_data['birthDate'].strip(), "%y%m%d").strftime("%Y-%m-%d")
            #         except:
            #             pass
                
            #     if nfc_data.get('expiryDate', ''):
            #         try:
            #             main_properties['date_of_expiry'] = datetime.strptime(nfc_data['expiryDate'].strip(), "%y%m%d").strftime("%Y-%m-%d")
            #         except:
            #             pass
                    
            return main_properties

    except:
        main_properties

    return main_properties    


def form_final_data_document_report(data, front_id_text, back_id_text, country, coloured, selfie, facial_similarity, blurred, glare, missing_fields, face_match_threshold, back_img):
    try:
        if data.get('uae_pass_data', ''):
            dob = data.get('uae_pass_data', '').get('DateOfBirth', '')
        else:
            dob = data.get('dob', '')

        document_report = {
            ## pending - to be filled by dev
            "_id": "",
            "breakdown": {
                "age_validation": age_validation(dob),
                "compromised_document": {
                    "result": "clear"
                    },
                "data_comparison": data_comparison_check(data, country),
                "data_consistency": data_consistency_check(data, front_id_text, back_id_text, country, back_img),
                "data_validation": data_validation_check(data, country),
                "image_integrity": image_integrity_check(data, front_id_text, back_id_text, coloured, blurred, glare, missing_fields, country),
                "issuing_authority": {
                "breakdown": {
                    "nfc_active_authentication": {
                    "properties": {}
                    },
                    "nfc_passive_authentication": {
                    "properties": {}
                    }
                }
                },
                "police_record": {},
                "visual_authenticity": visual_authenticity_check(data, front_id_text, back_id_text, selfie, facial_similarity, face_match_threshold, country)
            },
            ## pending - to be filled by dev
            "check_id": "", 
            "created_at": created_at(),
            "documents": [
                {
                ## pending - id value in table stored in db for front id - to be filled by dev
                "id": ""
                },
                {
                ## pending - id value in table stored in db for front id - to be filled by dev
                "id": ""
                }
            ],
            # to be filled by dev
            "href": "",
            "name": "document",
            "properties": main_details(data, country),
            "result": "",
            "status": "complete",
            "sub_result": ""
        }
        
        final_result = create_final_result(document_report)
        document_report['result'] = final_result

        sub_result = create_sub_result(document_report)
        document_report['sub_result'] = sub_result

        #For ATA Testing phase
        if country == 'UAE':
            keys_to_mark = ['original_document_present','conclusive_document_quality','image_quality','data_consistency', 'data_comparison', 'image_integrity', 'data_validation', 'visual_authenticity']
            document_report = mark_clear(document_report, keys_to_mark)
            document_report['result'] = 'clear'
            document_report['sub_result'] = 'clear'

        if country == 'QAT' and(document_report['breakdown']['visual_authenticity']['result'] == 'clear' and document_report['breakdown']['visual_authenticity']['breakdown']['face_detection'] == 'clear' and document_report['breakdown']['data_consistency']['breakdown']['multiple_data_sources_present']['result'] == 'clear'):
            keys_to_mark = ['data_consistency', 'data_comparison', 'image_integrity', 'data_validation', 'visual_authenticity']
            document_report = mark_clear(document_report, keys_to_mark)
            document_report['result'] = 'clear'

        if country == 'IRQ' and data.get('nfc_data', ''):
            document_report["type"] = "NFC"
        else:
            document_report["type"] = "OCR"

        return document_report
    
    except Exception as e:
        print(f"\n--------------Error occurred while forming Document Report: {str(e)}")
        raise Exception("Error occurred while creating document_report")
        # return {}

def form_final_facial_similarity_report(data, selfie, facial_similarity, liveness_result, face_match_threshold, country):
    try:
        facial_report = FACIAL_REPORT
        facial_report = mark_clear(facial_report, ['breakdown'])
        
        facial_report['created_at'] = created_at()
        
        facial_report['breakdown']['face_comparison']['breakdown']['face_match']['properties']['score'] = facial_similarity

        if not np.any(selfie):
            facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result'] = ''
            facial_report['breakdown']['face_comparison']['result'] = ''
            facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = ''
            facial_report['breakdown']['image_integrity']['breakdown']['source_integrity']['result'] = ''

        if np.any(selfie) and facial_similarity > face_match_threshold:
            facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result'] = 'clear'
            facial_report['breakdown']['face_comparison']['result'] = 'clear'
            facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = 'clear'
        elif facial_similarity != 0 and facial_similarity <= face_match_threshold:
            facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result']  = 'consider'
            facial_report['breakdown']['face_comparison']['result'] = 'consider'
            facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = 'clear'
        else:
            facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result']  = 'consider'
            facial_report['breakdown']['face_comparison']['result'] = 'consider'
            facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = 'consider'

        front_photo_on_screen_result = data.get('front_photo_on_screen_result')

        if country == 'UAE':
            photo_on_screen_result = data.get('photo_on_screen_result')
            if front_photo_on_screen_result == 'consider' or photo_on_screen_result == 'consider':
                facial_report['breakdown']['image_integrity']['breakdown']['source_integrity']['result'] = 'consider'

        if country == 'SAU':
            facial_report['breakdown']['image_integrity']['breakdown']['source_integrity']['result'] = front_photo_on_screen_result

        facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['properties']['score'] = round(1-facial_similarity,2)

        facial_report['breakdown']['visual_authenticity']['breakdown']['liveness_detected']['result'] = 'clear'
        facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['result'] = 'clear'
        facial_report['breakdown']['visual_authenticity']['result'] = 'clear'

        if liveness_result == 'consider':
            facial_report['breakdown']['visual_authenticity']['breakdown']['liveness_detected']['result'] = 'consider'
            facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['result'] = 'consider'
            facial_report['breakdown']['visual_authenticity']['result'] = 'consider'
        elif liveness_result == 'clear' and facial_similarity <= face_match_threshold:
            facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['result'] = 'consider'
            facial_report['breakdown']['visual_authenticity']['result'] = 'consider'
        elif liveness_result == None:
            facial_report['breakdown']['visual_authenticity']['breakdown']['liveness_detected']['result'] = ''
            facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['properties']['score'] = ''
            facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['result'] = ''

        # if np.any(selfie) and liveness_result:
        visual_authenticity_final_result = create_final_result(facial_report['breakdown']['visual_authenticity'])
        facial_report['breakdown']['visual_authenticity']['result'] = visual_authenticity_final_result

        # print(f"\n\n---------------- IMAGE INTEGRITY: {facial_report['breakdown']['image_integrity']}")
        # print(f"\n\n---------------- VISUAL AUTHENTICTY: {facial_report['breakdown']['visual_authenticity']}")
        # print(f"\n\n---------------- VISUAL AUTHENTICITY FINAL RESULT: {visual_authenticity_final_result}")

        image_integrity_final_result = create_final_result(facial_report['breakdown']['image_integrity'])
        facial_report['breakdown']['image_integrity']['result'] = image_integrity_final_result

        complete_final_result = create_final_result(facial_report['breakdown'])
        facial_report['result'] = complete_final_result
        facial_report['sub_result'] = complete_final_result

        return facial_report
    
    except Exception as e:
        print(f"\n--------------Error occurred while forming Facial Report: {str(e)}")
        raise Exception("Error occurred while creating facial_report")
