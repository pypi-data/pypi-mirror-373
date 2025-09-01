import cv2
import numpy as np
from google.cloud import vision_v1
from googletrans import Translator
import re
from idvpackage.common import *
import io
import os
from PIL import Image
from deep_translator import GoogleTranslator
import imghdr
import tempfile

translator = Translator()

def crop_second_part(img):
    width, height = img.size
    half_width = width // 2
    second_part = img.crop((half_width, 0, width, height))
    return second_part


def crop_third_part(img):
    width, height = img.size
    part_height = height // 3
    third_part = img.crop((0, 2 * part_height, width, height))
    return third_part


def extract_text_from_image_data(client, image):
    """Detects text in the file."""

    with io.BytesIO() as output:
        image.save(output, format="PNG")
        content = output.getvalue()

    image = vision_v1.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    return texts[0].description


def detect_image_format(image_data):
    image_format = imghdr.what(None, image_data)
    return image_format
    
  
def create_temporary_file(image_data, image_format):
    with tempfile.NamedTemporaryFile(suffix='.' + image_format, delete=False) as temp_file:
        temp_file.write(image_data)
        temp_file_path = temp_file.name

    return temp_file_path

def detect_image_format(pil_img):
    image_format = pil_img.format.lower() if pil_img.format else 'jpg'  # Default to 'jpg' if format is not recognized

    open_cv_image = np.array(pil_img)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    with tempfile.NamedTemporaryFile(suffix='.' + image_format, delete=False) as temp_file:
        cv2.imwrite(temp_file.name, open_cv_image)
        temp_file_path = temp_file.name

    return temp_file_path

def extract_family_number(arabic_text):
    # Attempt different patterns to handle different exceptional cases
    
    # Pattern 1: Generalized pattern that covers most cases (like the first and third one)
    pattern_1 = r'(\d{4,6})?\s*(?:الرقم|العائلي|زماره|زمارة|ژماردی|ژماره|از)\s*(?:العاملي|العائلي|خيزانى|خبرائی|خيرالي|خیزانی|خیزاني|خیزانی)?\s*[:：]?\s*([A-Za-z0-9]+)'
    family_number_match = re.search(pattern_1, arabic_text)
    
    if family_number_match:
        part1 = family_number_match.group(1) if family_number_match.group(1) else ''
        part2 = family_number_match.group(2)
        dict_1 = {"family_number": part1 + part2}
        return dict_1

    # Pattern 2: Handles family numbers directly after the family keyword, with no leading digits
    pattern_2 = r'(?:الرقم العائلي|ژماردی خیزانی|ژماره ی خیزانی|العائلى از|العائلي)\s*[:：]?\s*([A-Za-z0-9]+)'
    family_number_match = re.search(pattern_2, arabic_text)

    if family_number_match:
        dict_1 = {"family_number": family_number_match.group(1)}
        return dict_1

    # Pattern 3: Handles numbers appearing on a new line, separated from family labels
    pattern_3 = r'(?:الرقم العائلي|ژماردی خیزانی|العائلي|العائلى از)\s*[:：]?\s*\n*([A-Za-z0-9]+)'
    family_number_match = re.search(pattern_3, arabic_text)

    if family_number_match:
        dict_1 = {"family_number": family_number_match.group(1)}
        return dict_1

    # Pattern 4: Specific case handling for labels ending without a colon
    pattern_4 = r'(?:الرقم العائلي|ژماردی خیزانی|العائلي|العائلى از)\s*\n*([A-Za-z0-9]+)'
    family_number_match = re.search(pattern_4, arabic_text)

    if family_number_match:
        dict_1 = {"family_number": family_number_match.group(1)}
        return dict_1

    # Pattern 5: Handles family numbers followed by extra symbols or unusual formatting (2nd case)
    pattern_5 = r'(\d{4,6}[A-Za-z0-9]+)\s*[:ˋˋˋˋˋˋˋˋ]'
    family_number_match = re.search(pattern_5, arabic_text)

    if family_number_match:
        dict_1 = {"family_number": family_number_match.group(1)}
        return dict_1

    # Pattern 6: Handles family numbers without clear delimiter or labels ending without a colon (4th case)
    pattern_6 = r'(\d{4,6}[A-Za-z0-9]+)\s*[:P]?\s*'
    family_number_match = re.search(pattern_6, arabic_text)

    if family_number_match:
        dict_1 = {"family_number": family_number_match.group(1)}
        return dict_1
    
    # Return None if no patterns match
    return {"family_number": None}




def extract_mother_surname(text):
    # Initialize variables to avoid UnboundLocalError
    cleaned_text = None
    
    pattern_mother_name = r"(?:الأم|دايك|اديك|دایك)\s*[:：]?\s*(\S+)?(?:\n.*?)*(?:الجد|باپير|بابير|بايير|باپیر)\s*[:：]?\s*([^\n]*)"
    match = re.search(pattern_mother_name, text, re.DOTALL)

    if match:
        mother_name = match.group(1).strip() if match.group(1) else "Not Available"
        grandfather_name = match.group(2).strip() if match.group(2) else ""

        pattern = r"[/:\s]*(بابير|ابير|باپير)[:/\s]*" #r"[/:\s]*(بابير|ابير)[:/\s]*"
        cleaned_text = re.sub(pattern, "", grandfather_name).strip()
        
        
        if not cleaned_text:
            cleaned_text = None

    # If no match or cleaned_text is empty, return None for mother_last_name
    if cleaned_text is None:
        return {"mother_last_name": None}

    return {"mother_last_name": cleaned_text}




def extract_mother_name(text):
   
    pattern_mother_name = r"(?:الأم|دايك|دایك)\s*[:：]?\s*(?:[\n\s]*(\d{4}-\d{2}-\d{2}))?\s*([\u0621-\u064A\s]+)"
    
    matches = re.finditer(pattern_mother_name, text)

    
    mother_names = []
    eng_name = []
    for match in matches:
        mother_name = match.group(2).strip()
        if mother_name:
            
            cleaned_name = re.sub(r"(الجد|الام|با|بابير|فصيل|الدم)", "", mother_name).strip()
            if cleaned_name:
                parts = cleaned_name.split('\n')
                name_ = parts[0]
    try:
        dict_1 = {"mother_first_name": name_} 
    except Exception as e:
        name_ = None
        dict_1 = {"mother_first_name": name_} 

    

    return dict_1

def extract_paternal_grandfather_name(text):
    pattern_paternal_grandfather = r"(?:الجد|باپير|بابير|بايير|باپیر)\s*[:：]?\s*([^\n/:]*)"

    matches = re.findall(pattern_paternal_grandfather, text)
    grandfather_names = [match.strip() for match in matches if match.strip()]
    try:
       dict_1 = {"third_name":grandfather_names[0]}
    except Exception as e:
       dict_1 = {'third_name': None}
       print("error:", e)

    return dict_1

def update_family_number_cases(dictt, text_back):
    try:
        if len(dictt["family_number"]) < 11:
            pattern = r'(?:الرقم العائلي|رقم العائلة)\s*/?\s*(?:زمارهی خیزانی)?\s*:\s*([\dA-Z\s]+)'
            #pattern = r'(?:الرقم العائلي|رقم العائلة)\s*/?\s*(?:زمارهی خیزانی)?\s*:\s*(\d+\s+\d+[A-Z]\d+B)'
            match = re.search(pattern, text_back)
            if match:
                family_number = match.group(1)
                list_modify = family_number.split(" ")
                last_value = list_modify[1]+list_modify[0]
                dictt['family_number'] = last_value

            else:
                print("Family number not found.")
        else:
            print("value greater than 11")
    except Exception as e:
        print("None!")
    return dictt

def detect_id_card(client, image_data, id_texts, image_format, part=None, country=None):
    
    if id_texts:
        id_text = id_texts[0]
        vertices = id_text.bounding_poly.vertices
        left = vertices[0].x
        top = vertices[0].y
        right = vertices[2].x
        bottom = vertices[2].y

        padding = 30
        padded_left = max(0, left - padding)
        padded_top = max(0, top - padding)
        padded_right = right + padding
        padded_bottom = bottom + padding

        with Image.open(io.BytesIO(image_data)) as img:
            id_card = img.crop((padded_left, padded_top, padded_right, padded_bottom))
        
            temp_dir = tempfile.mkdtemp()
            id_card_path = os.path.join(temp_dir, f"cropped_img_original.{image_format}")
            id_card.save(id_card_path)

            width, height = id_card.size
            if width < height:
                id_card = id_card.rotate(90, expand=True)
            
            # Read the temporary image with OpenCV for further processing
            # if id_card_path:
            #     orig_img = cv2.imread(id_card_path)
            # else:
            #     orig_img = None

            # tampered_result = calculate_error_difference(orig_img, country)
            tampered_result = 'clear'

            if os.path.exists(id_card_path):
                os.remove(id_card_path)

            if part:
                if part=='second':
                    part_img = crop_second_part(id_card)

                if part=='third':
                    part_img = crop_third_part(id_card)
                
                # 2nd call to vision AI
                try:
                    part_text = extract_text_from_image_data(client, part_img)
                except: 
                    part_text = id_texts[0].description

                return id_card, part_img, part_text, tampered_result
            else:
                return id_card, tampered_result
    else:
        print('No text found in the image.')


def extract_name_fields_from_raw(text):
    try:
        generic_field_match_pattern = r':\s*([^:\n]*)'
        
        generic_field_matches = re.findall(generic_field_match_pattern, text)
        generic_fields_result = []
        for item in generic_field_matches:
            no_digits = ''.join([char for char in item if not char.isdigit()])
            if no_digits.strip():
                generic_fields_result.append(no_digits)

        generic_fields_result = [word for word in generic_fields_result if len(word.split()) <= 3 and '/' not in word and '|' not in word]

        # print(f"DATA LIST: {generic_fields_result}")

        if len(generic_fields_result[0].split()) <= 2 and len(generic_fields_result) <= 8:
            given_name = generic_fields_result[0]
        else:
            given_name = ''
        
        if len(generic_fields_result[1].split()) <= 2:
            fathers_name = generic_fields_result[1]
        else:
            fathers_name = ''
            
        if len(generic_fields_result[3].split()) <= 2:
            surname = generic_fields_result[3].replace("الأم", "").replace("دايك", "").replace("مديرية ال", "").replace("/", "").replace("البطاقة الو", "").replace("ذكر", "").replace("الام", "").replace("]", "")
        else:
            surname = ''

        try: 
            gender = ''
            gender_ar = generic_fields_result[-2]
            try:
                gender = translator.translate(gender_ar, src='ar', dest='en').text
            except:
                gender = GoogleTranslator('ar', 'en').translate(gender_ar)

            if str(gender).lower() == 'feminine':
                gender = 'female'
            
            if gender.lower() != 'male' or gender.lower() != 'female':
                if 'ذكر' in generic_fields_result:
                    gender = 'male'
                elif 'انثى' in generic_fields_result:
                    gender = 'female'
                else:
                    gender = ''
        except:
            gender_ar, gender = '', None

        name = f"{given_name} {fathers_name} {surname}"
        
        first_name_en, fathers_name_en, last_name_en = '', '', ''

        if name:
            name_en = GoogleTranslator('ar', 'en').translate(name).upper()
            if name_en:
                name_list = name_en.split(' ')
                if len(name_list) >=2:
                    first_name_en = name_list[0]
                    fathers_name_en = name_list[1]
                    last_name_en = name_list[-1]

                    #For edge cases where surnames have prefixes like Al- Bin- Abu-.
                    if last_name_en.startswith('-'):
                        last_name_en = name_list[-2]+name_list[-1]


            # name_en = translator.translate(name, src='ar', dest='en').text.upper()

        names_data  = {
            "gender": gender,
            "gender_ar": gender_ar,
            "name": name,
            "first_name": given_name,
            "father_name": fathers_name,
            "last_name": surname,
            "first_name_en": first_name_en,
            "father_name_en": fathers_name_en,
            "last_name_en": last_name_en,
            "name_en": name_en,
        }

        return names_data
    
    except:
        return {}


def identify_front(text):
    front_id_keywords = ["The Republic of Iraq", "The Ministry of Interior", "National Card"]
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    try:
        if re.search(pattern, text, re.IGNORECASE):
            return True
        else:
            return False
    except:
        return 'error'

def extract_numeric_fields_from_raw(ar_front_data, front_data):
    # try:
    #     front_data = translator.translate(ar_front_data, src='ar', dest='en').text 
    # except:
    #     front_data = GoogleTranslator('ar', 'en').translate(ar_front_data)
        
    gender_pattern = r"Sex.*?:\s*(\w+)"
    id_number_pattern = r"\b\d{12}\b"
    rfid_number_pattern = r"\b[A-Za-z]{2}\d{7}\b|\b[A-Za-z]\d{8}\b"
        
    gender_match = re.search(gender_pattern, front_data, re.IGNORECASE)
    if gender_match:
        gender = gender_match.group(1)
    else:
         gender = ''
        
    id_number_match = re.search(id_number_pattern, front_data.replace(" ",""), re.IGNORECASE)
    if id_number_match:
        id_number = id_number_match.group(0)
    else:
        try:
            id_number_match = re.search(id_number_pattern, ar_front_data.replace(" ",""), re.IGNORECASE)
            id_number = id_number_match.group(0)
        except:
            id_number = ''
    
    rfid_number_match = re.search(rfid_number_pattern, ar_front_data.replace(" ","").replace(":","").replace("$", "S"), re.IGNORECASE)
    if rfid_number_match:
        rfid_number = rfid_number_match.group(0).upper()
    else:
        rfid_number = ''
    
    front_data = {
        "gender": gender,
        "id_number_front": id_number,
        "card_number_front": rfid_number
    }
    
    return front_data


def iraq_front_id_extraction(client, image_data, front_id_text, front_id_text_description, front_translated_data, image_format):
    front_data_final = {
        'first_name': '',
        'last_name': '',
        'name': ''
    }

    cropped_id_card, second_part, second_part_text, tampered_result_front = detect_id_card(client, image_data, front_id_text, image_format, part='second')
    front_data = extract_name_fields_from_raw(second_part_text)
    numeric_fields = extract_numeric_fields_from_raw(front_id_text_description, front_translated_data)
    
    if not front_data:
        front_data = extract_name_fields_from_raw(front_id_text_description)

    gender_front_data = front_data.get('gender', '')
    gender_numeric_fields = numeric_fields.get('gender', '')

    gender = ''
    if gender_front_data and (gender_front_data.lower()=='male' or gender_front_data.lower()=='female'):
        gender = gender_front_data
    elif gender_numeric_fields and (gender_numeric_fields.lower()=='male' or gender_numeric_fields.lower()=='female'):
        gender = gender_numeric_fields

    front_data.update(numeric_fields)
    front_data['gender'] = gender
    if gender:
        try:
            front_data['gender_ar'] = translator.translate(gender, src='en', dest='ar').text
        except:
            front_data['gender_ar'] = GoogleTranslator('en', 'ar').translate(gender)

    front_data['front_tampered_result'] = tampered_result_front

    front_data_final.update(front_data)

    if "gender" in front_data_final:
        gender = front_data_final["gender"].strip().upper()
        if gender == "F":
            front_data_final["gender"] = "FEMALE"
        elif gender == "M":
            front_data_final["gender"] = "MALE"

    if 'gender' in front_data_final:
        front_data_final["gender"] = front_data_final["gender"].strip().upper()

    return front_data_final


def find_mrz2_from_original(back_data):
    mrz2 = re.search(r'\b\d{6,}.*?<{2,}|\b\d{6,}.*?く{2,}', back_data, re.MULTILINE)
    return mrz2.group(0) if mrz2 else None


def handle_name_extraction(third_part_text):
    mrz_pattern = r'(IDIRQ[\S].*\n*.*\n*.*\n*.*|IDIRQ[\S].*\n*.*\n*.*\n*.*)'

    try:
        mrz = re.findall(mrz_pattern, third_part_text.replace(" ","").strip(), re.MULTILINE)
        mrz_str = mrz[0].replace(" ", "")
        mrz3 = re.search(r'[\n](?:[a-zA-Z<]{6,})', mrz_str)
        mrz3 = mrz3.group(0).replace("\n","") if mrz3 else None

        first_name, last_name = '', ''
        if mrz3:
            name_list = re.findall(r'\b[^<\s]+\b', mrz3)

            if name_list:
                if len(name_list)>1:
                    first_name = name_list[1].upper().replace("X", "")
                    last_name = name_list[0].upper().replace("X", "")
                else:
                    first_name = name_list[0].upper().replace("X", "")

                return {
                    "first_name_back": first_name,
                    "last_name_back": last_name,
                }
            else:
                return {}
        
    except:
       return {}
    

def handle_mrz_extraction(third_part_text, back_data, back_data_dict):
    mrz_pattern = r'(IDIRQ[\S].*\n*.*\n*.*\n*.*|IDIRC[\S].*\n*.*\n*.*\n*.*)'
    mrz1_data_pattern = r'(IDIRQ([\S]{2}\d{7}|[\S]\d{8}).*?(\d{13})|IDIRC([\S]{2}\d{7}|[\S]\d{8}).*?(\d{13}))'

    try:
        mrz = re.findall(mrz_pattern, third_part_text.replace(" ","").strip(), re.MULTILINE)
        mrz_str = mrz[0].replace(" ", "")
    except:
        mrz_str = ''

    mrz1 = re.search(r'(IDIRQ.*?<{2,}|IDIRC.*?<{2,})', mrz_str, re.DOTALL)
    mrz1 = mrz1.group(1) if mrz1 else None

    mrz2 = re.search(r'\b\d{6,}.*?<{2,}', mrz_str, re.MULTILINE)
    mrz2 = mrz2.group(0) if mrz2 else None

    mrz3 = re.search(r'[\n](?:[a-zA-Z<]{6,})', mrz_str)
    mrz3 = mrz3.group(0).replace("\n","") if mrz3 else None

    rfid_number = ''
    id_number = ''

    mrz1_data_match = re.search(mrz1_data_pattern, mrz_str)
    if mrz1_data_match:
        rfid_number = mrz1_data_match.group(1)
        id_number = mrz1_data_match.group(2)

    rfid_number = rfid_number.upper()
    id_number = id_number[1:14] 
    
    try:
        pattern = r'(?<=[\S]\d{7})[A-Z]{3}'

        national = re.search(pattern, mrz[0].replace(" ", ""))
        if national:
            nationality = national.group()
        else:
            national2 = re.search(pattern, mrz[0].replace(" ", "").replace("\n", ""))
            if national2:
                nationality = national2.group()
            else:
                nationality = ''
    except:
        nationality = ''

    try:
        dob_pattern = r'(\d+)[MF]'
        dob_match = re.search(dob_pattern, mrz2)
        dob_mrz = convert_dob(dob_match.group(1)) if dob_match else ''

        doe_pattern = r'[MF](\d+)'
        doe_match = re.search(doe_pattern, mrz2)
        expiry_date_mrz = convert_expiry_date(doe_match.group(1)) if doe_match else ''
    except:
        dob_mrz, expiry_date_mrz = '', ''

    if back_data_dict.get('id_number'):
        id_number = back_data_dict['id_number']
    
    if back_data_dict.get('card_number'):
        rfid_number = back_data_dict['card_number']

    if back_data_dict.get('mrz1'):
        mrz1 = back_data_dict['mrz1']

    back_data_new = {
        "id_number": id_number,
        "card_number": rfid_number,
        "nationality": nationality,
        "mrz": [mrz_str],
        "mrz1": mrz1,
        "mrz2": mrz2,
        "mrz3": mrz3,
        "dob_mrz": dob_mrz,
        "expiry_date_mrz": expiry_date_mrz
    }

    ## HANDLING EDGE CASES FOR ID NUMBER AND CARD NUMBER
    if not (back_data_new.get('id_number') or back_data_new.get('card_number')):
        mrz_pattern = r'(IDI[\S]{2}.*\n*.*\n*.*\n*.*|IDIRQ[\S].*\n*.*\n*.*\n*.*|IDIRC[\S].*\n*.*\n*.*\n*.*)'
        mrz1_data_pattern = r'IDI[\S]{2}([\S]{2}\d{7}|[\S]\d{8}).*?(\d{13})'

        try:
            mrz = re.findall(mrz_pattern, back_data.replace(" ","").strip(), re.MULTILINE)
            mrz_str = mrz[0].replace(" ", "")
        except:
            mrz_str = ''

        back_data_new['mrz'] = [mrz_str]

        mrz1 = re.search(r'(IDI[\S]{2}.*?<{2,})', mrz_str, re.DOTALL)
        mrz1 = mrz1.group(1) if mrz1 else None
        back_data_new['mrz1'] = mrz1

        mrz2 = re.search(r'\b\d{7}.*?(?:<<\d|<<\n)', mrz_str)
        mrz2 = mrz2.group(0) if mrz2 else None
        back_data_new['mrz2'] = mrz2

        mrz3 = re.search(r'[\n](?:[a-zA-Z<]{6,})', mrz_str)
        mrz3 = mrz3.group(0).replace("\n","") if mrz3 else None
        back_data_new['mrz3'] = mrz3

        rfid_number = ''
        id_number = ''

        mrz1_data_match = re.search(mrz1_data_pattern, mrz_str)
        if mrz1_data_match:
            rfid_number = mrz1_data_match.group(1)
            id_number = mrz1_data_match.group(2)

        rfid_number = rfid_number.upper()
        id_number = id_number[1:14] 
        back_data_new['id_number'] = id_number
        back_data_new['card_number'] = rfid_number

    ## HANDLE DOB AND DOE FROM MRZ
    if not (back_data_new.get('dob_mrz') or back_data_new.get('expiry_date_mrz')):
        if not mrz2:
            mrz2 = re.search(r'\b\d{6,}.*?<{2,}|\b\d{6,}.*?く{2,}', mrz_str, re.MULTILINE)
            mrz2 = mrz2.group(0) if mrz2 else find_mrz2_from_original(back_data.replace(" ","").strip())

        if mrz2:
            dob_pattern = r"(\d{7})[MF]"
            dob_match = re.search(dob_pattern, mrz2)
            if dob_match:
                dob = dob_match.group(1)
                back_data_new['dob_mrz'] = convert_dob(dob)
            else:
                dob_pattern = r'(\d{12,})[\S]R[\S]\b'
                dob_match = re.search(dob_pattern, mrz2)

                if dob_match:
                    dob = dob_match.group(1)[:7]
                    back_data_new['dob_mrz'] = convert_dob(dob)
        
            doe_pattern = r"[MF](\d+)"
            doe_match = re.search(doe_pattern, mrz2)
            if doe_match:
                expiry = doe_match.group(1)
                back_data_new['expiry_date_mrz'] = convert_expiry_date(expiry)
            else:
                doe_pattern = r'(\d{12,})[\S]R[\S]\b'
                doe_match = re.search(doe_pattern, mrz2)
                
                if doe_match:
                    expiry = doe_match.group(1)[8:]
                    if len(expiry)<7:
                        expiry = doe_match.group(1)[7:]
                    back_data_new['expiry_date_mrz'] = convert_expiry_date(expiry)

    if not back_data_new.get('nationality'):
        mrz_pattern = r'(IDI[\S]{2}.*\n*.*\n*.*\n*.*|IDIRQ[\S].*\n*.*\n*.*\n*.*||IDIRC[\S].*\n*.*\n*.*\n*.*)'
        try:
            mrz = re.findall(mrz_pattern, back_data.replace(" ","").strip(), re.MULTILINE)
        except:
            mrz = ''

        if mrz:
            national = re.search(pattern, mrz[0].replace(" ", "").replace("\n", ""))
            if national:
                nationality = national.group()
            else:
                nationality = ''
        
            back_data_new['nationality'] = nationality

    if not back_data_new.get('nationality'):
        nationality_pattern = r'\d{6,}([\S]{3})\b'
        nationality_match = re.search(nationality_pattern, mrz2)
        if nationality_match:
            nationality = nationality_match.group(1)
            back_data_new['nationality'] = nationality

    return back_data_new

def count_digits(text):
    return len(re.findall(r'\d', text))

def find_gender_from_back(text):
    gender = ''
    gender_pattern = r'(\d)([A-Za-z])(\d)'
    gender_match = re.search(gender_pattern, text)
    if gender_match:
        gender = gender_match.group(2)
        
    if not gender:
        gender_pattern = r'(\d)([MFmf])(\d)'
        gender_match = re.search(gender_pattern, text)
        if gender_match:
            gender = gender_match.group(2)

     

    return gender

def iraq_back_id_extraction(client, image_data, back_id_text, back_data, image_format):
    mrz_pattern = r'(IDIRQA.*\n*.*\n*.*\n*.*|IDIRQC.*\n*.*\n*.*\n*.*|IDIR.*\n*.*\n*.*\n*.*)'
    mrz1_data_pattern = r'IDIRQ([A-Za-z]{2}\d{7}|[A-Za-z]\d{8}).*?(\d{13})|IDIRC([A-Za-z]{2}\d{7}|[A-Za-z]\d{8}).*?(\d{13})'
    nationality_pattern = r'([A-Z]+)<<'
    place_of_birth_pattern = r'(?:محل|الولادة)[^:]*:\s*(.*?)\n'
    issuing_authority_pattern_1 = r"مديرية الجنسية والمعلومات المدنية"
    issuing_authority_pattern_2 = r"دائرة احوال -.*?(?=\n|\r|$)"

    mrz1, mrz2, mrz3 = '', '', ''

    try:
        mrz = re.findall(mrz_pattern, back_data.replace(" ","").strip(), re.MULTILINE)
        mrz_str = mrz[0].replace(" ", "")
    except:
        mrz_str = ''
    
    # mrz1 = re.search(r'(IDIRQ.*?<<<)', mrz_str, re.DOTALL)
    # mrz1 = mrz1.group(1) if mrz1 else None

    # mrz2 = re.search(r'\b\d{6,}.*?<{2,}', mrz_str, re.MULTILINE)
    # mrz2 = mrz2.group(0) if mrz2 else None

    # mrz3 = re.search(r'[\n](?:[a-zA-Z<]{6,})', mrz_str)
    # mrz3 = mrz3.group(0).replace("\n","") if mrz3 else None
    
    if mrz_str:
        mrz_list=mrz_str.replace(" ", "").split("\n")
        try: 
            mrz1=mrz_list[0]
        except:
            mrz1=''
        try:
            mrz3=[s.replace('>','<')  for s in [remove_special_characters1(ele).replace(' ','') for ele in back_data.split('\n')] if len(re.findall(r'<', s)) >= 2 and re.fullmatch(r'[A-Za-z<>]+', s)][0]
        except: 
            mrz3=''
        try:
            mrz2=[ele for ele in [ele for ele in mrz_list if ele not in [mrz1,mrz3] ] if remove_special_characters_mrz2(ele) !='']
            if len(mrz2)>1:
                mrz2=max(mrz2, key=count_digits)+[ele for ele in mrz2 if ele!=max(mrz2, key=count_digits)][0]

                pattern = r'\d{7}[MF]\d{7}[\S]{3}<+?\d'
                mrz2_temp = re.search(pattern, mrz2.replace(">", ""))
                if mrz2_temp:
                    mrz2 = mrz2_temp.group(0)

                mrz2=mrz2.split('<')[0]+'<<<<<<<<<<'+mrz2.split('<')[-1]

                # mrz2=mrz2[0].split('<')[0]+'<<<<<<<<<<'+mrz2[-1][-1]
            else :
                mrz2=mrz2[0].split('<')[0]+'<<<<<<<<<<'+mrz2[0][-1]
        except:
            mrz2=''
    
    ## condition to replace O with 0
    try:
        pattern = r'(IDIRQ[A-Z]{1,2})O(?=[0-9])'
        replacement = lambda m: m.group(1) + '0'
        mrz1 = re.sub(pattern, replacement, mrz1)
    except:
        pass

    ## condition to replace '>' with 7
    if mrz2 and mrz2.endswith('>'):
        mrz2 = mrz2.split('<')[0]+'<<<<<<<<<<'+'7'

    ## condition to add filler to mrz3, making it total length of 30 chars
    if len(mrz3) < 30:
        mrz3 = mrz3.ljust(30, '<')
    
    # mrz1_data_match = re.search(mrz1_data_pattern, mrz_str)
    # if mrz1_data_match:
    #     rfid_number = mrz1_data_match.group(1)
    #     id_number = mrz1_data_match.group(2)

    # rfid_number = rfid_number.upper()
    # id_number = id_number[1:14] 
    try:
        rfid_number=mrz1.split('IDIR')[-1][1:10]
    except: 
        rfid_number = ''
    try:
        id_number=mrz1.split('IDIR')[-1][11:23]
    except:
        id_number = ''
    
    dob = func_dob(mrz_str)

    if not dob:
        matches = re.findall(r'\d{4}/\d{2}/\d{2}', back_data)
        sorted_dates = sorted(matches)
        dob = sorted_dates[0]
    
    expiry = func_expiry_date(mrz_str)
    if not expiry:
        matches = re.findall(r'\d{4}/\d{2}/\d{2}', back_data)
        sorted_dates = sorted(matches)
        expiry = sorted_dates[-1]
    
    ## handle issue date
    try:
        matches = re.findall(r'\d{4}/\d{2}/\d{2}', back_data)
        sorted_dates = sorted(matches)
        issue_date = sorted_dates[1]
    except:
        issue_date = ''
    
    # nationality_matches = re.search(nationality_pattern, mrz[0])
    # if nationality_matches:
    #     nationality = nationality_matches.group(1)
    # else:
    # try:
    #     pattern = r'(?<=[A-Z]\d{7})[A-Z]{3}'
    #     national = re.search(pattern, back_data)
    #     if national:
    #         nationality = national.group()
    #     else:
    #         nationality = ''
    # except:
    #     nationality = ''
    
    # if len(nationality)>3:
    #     pattern = r'(?<=[A-Z]\d{7})[A-Z]{3}'
    #     national = re.search(pattern, back_data)
    #     if national:
    #         nationality = national.group()
    
    try:
        nationality=mrz2.split('<')[0][-3:]
    except: 
        nationality='IRQ'
    first_name, last_name = '', ''
    
    if mrz3:
        name_list = re.findall(r'\b[^<\s]+\b', mrz3)

        if len(name_list)>1:
            first_name = name_list[1].upper().replace("X", "")
            last_name = name_list[0].upper().replace("X", "")
        else:
            first_name = name_list[0].upper().replace("X", "")
    
    else:
        mrz3 = ''

#     issuing_authority_matches = re.findall(issuing_authority_pattern, back_data)
#     if issuing_authority_matches:
#         issuing_authority = issuing_authority_matches[-1][1]
#     else:
#         issuing_authority = ''

    issuing_authority = ''
    issuing_authority_match_1 = re.search(issuing_authority_pattern_1, back_data)
    issuing_authority_match_2 = re.search(issuing_authority_pattern_2, back_data)
  
    if issuing_authority_match_1:
        issuing_authority = issuing_authority_match_1.group(0)

    if issuing_authority_match_2:
        issuing_authority = issuing_authority_match_2.group(0)
        
    place_of_birth_match = re.search(place_of_birth_pattern, back_data)
    if place_of_birth_match:
        place_of_birth = place_of_birth_match.group(1).strip()
        place_of_birth_list = place_of_birth.split(":")
        if len(place_of_birth_list)>=2:
            place_of_birth = place_of_birth_list[1].strip()
        elif len(place_of_birth_list)==1:
            place_of_birth = place_of_birth_list[0]
        else:
            place_of_birth = ''
    else:
        place_of_birth = ''

    issuing_authority_en=place_of_birth_en=''

    if issuing_authority:
        try:
            issuing_authority_en = translator.translate(issuing_authority, src='ar', dest='en').text.upper()
        except:
            issuing_authority_en = GoogleTranslator('ar', 'en').translate(issuing_authority)

    if place_of_birth:
        try:
            place_of_birth_en = translator.translate(place_of_birth, src='ar', dest='en').text.upper()
        except:
            place_of_birth_en = GoogleTranslator('ar', 'en').translate(place_of_birth)
    
    try:
        dob_pattern = r'(\d+)[MF]'
        dob_match = re.search(dob_pattern, mrz2)
        dob_mrz = convert_dob(dob_match.group(1)) if dob_match else ''

        doe_pattern = r'[MF](\d+)'
        doe_match = re.search(doe_pattern, mrz2)
        expiry_date_mrz = convert_expiry_date(doe_match.group(1)) if doe_match else ''
    except:
        dob_mrz, expiry_date_mrz = '', ''

    gender = ''
    try:
        gender = find_gender_from_back(mrz2)
    except:
        gender = find_gender_from_back(back_data)

    mrz_str = f"{mrz1}\n{mrz2}\n{mrz3}"

    if nationality and (nationality == '1RQ' or nationality == 'IRG'):
            nationality = 'IRQ'

    back_data_dict = {
        "mrz": [mrz_str],
        "mrz1": mrz1,
        "mrz2": mrz2,
        "mrz3": mrz3,
        "id_number": id_number,
        "card_number": rfid_number,
        "dob": dob,
        "issue_date": issue_date,
        "first_name_back": first_name,
        "last_name_back": last_name,
        "expiry_date": expiry,
        "nationality": nationality,
        "issuing_authority": issuing_authority,
        "place_of_birth": place_of_birth,
        "issuing_authority_en": issuing_authority_en,
        "place_of_birth_en": place_of_birth_en,
        "issuing_country": "IRQ",
        "dob_mrz": dob_mrz,
        "expiry_date_mrz": expiry_date_mrz,
        "gender_back": gender
    }

    if "gender_back" in back_data_dict:
        gender = back_data_dict["gender_back"].strip().upper()
        if gender == "F":
            back_data_dict["gender_back"] = "FEMALE"
        elif gender == "M":
            back_data_dict["gender_back"] = "MALE"

    if 'gender_back' in back_data_dict:
        back_data_dict["gender_back"] = back_data_dict["gender_back"].strip().upper()

#-----------------------------------
## I dont see the point of the below block (unacessary redudency)
    # ## HANDLE DOB DOE FROM MRZ
    # if not (back_data_dict.get('dob_mrz') or back_data_dict.get('expiry_date_mrz')):
    #     mrz_pattern = r'(IDIRQ[\S].*\n*.*\n*.*\n*.*|IDIRC[\S].*\n*.*\n*.*\n*.*)'
    #     try:
    #         mrz = re.findall(mrz_pattern, back_data.replace(" ","").strip(), re.MULTILINE)
    #         mrz_str = mrz[0].replace(" ", "")
            
    #         mrz2 = re.search(r'\b\d{6,}.*?<{2,}', mrz_str, re.MULTILINE)
    #         mrz2 = mrz2.group(0) if mrz2 else None
    #     except:
    #         mrz_str = ''
        
    #     if mrz2:
    #         dob_pattern = r"(\d{7})[MF]"
    #         dob_match = re.search(dob_pattern, mrz2)
    #         if dob_match:
    #             dob = dob_match.group(1)
    #             back_data_dict['dob_mrz'] = convert_dob(dob)
    #         else:
    #             dob_pattern = r'(\d{12,})[\S]R[\S]\b'
    #             dob_match = re.search(dob_pattern, mrz2)
    #             if dob_match:
    #                 dob = dob_match.group(1)[:7]
    #                 back_data_dict['dob_mrz'] = convert_dob(dob)
        
    #         doe_pattern = r"[MF](\d+)"
    #         doe_match = re.search(doe_pattern, mrz2)
    #         if doe_match:
    #             expiry = doe_match.group(1)
    #             back_data_dict['expiry_date_mrz'] = convert_expiry_date(expiry)
    #         else:
    #             doe_pattern = r'(\d{12,})[\S]R[\S]\b'
    #             doe_match = re.search(doe_pattern, mrz2)
    #             if doe_match:
    #                 expiry = doe_match.group(1)[8:]
    #                 if len(expiry)<7:
    #                     expiry = doe_match.group(1)[7:]
    #                 back_data_dict['expiry_date_mrz'] = convert_expiry_date(expiry)

    #         if not back_data_dict.get('nationality'):
    #             nationality_pattern = r'\d{6,}([\S]{3})\b'
    #             nationality_match = re.search(nationality_pattern, mrz2)
    #             if nationality_match:
    #                 nationality = nationality_match.group(1)
    #                 back_data_dict['nationality'] = nationality
#-----------------------------------

    non_optional_keys = ["id_number", "card_number", "nationality", "dob"]
    empty_string_keys = [key for key, value in back_data_dict.items() if key in non_optional_keys and value == '']
    cropped_id_card, tampered_result_back = detect_id_card(client, image_data, back_id_text, image_format)
    back_data_dict['back_tampered_result'] = tampered_result_back

    return back_data_dict
