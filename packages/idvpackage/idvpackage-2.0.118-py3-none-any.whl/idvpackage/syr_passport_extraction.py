import google.generativeai as genai
import base64
import json
import re
import io
from PIL import Image
from datetime import datetime

def configure_genai(api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    return model

def base64_to_image(base64_string):
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return image

def crop_image_in_half(image, offset=90):
    width, height = image.size
    split_line = (height // 2) - offset  # Make the first half smaller by 'offset' pixels
    
    first_half = image.crop((0, 0, width, split_line))  
    second_half = image.crop((0, split_line, width, height)) 

    return first_half, second_half


def is_valid_date(date_str):
    date_pattern = re.compile(r'^(\d{2}/\d{2}/\d{4}|\d{4}/\d{2}/\d{2}|\d{4}-\d{2}-\d{2})$')
    if date_str is None or date_pattern.match(date_str):
        return True
    else:
        return False


def genai_image_second_half(image, model):
    result = model.generate_content(
        [image, "\n\n", "give me issue_number, name, surname, father name, mother name, date_of_birth, place_of_birth, nationality, gender(M/F), and both lines of the MRZ from provided photo, please give me output as just dictionary - issue_number, full_name, first_name, last_name, father_name, mother_name, dob, place_of_birth, nationality,gender, mrz1, mrz2. Note that mrz1 is the line that starts with P"]
    )
    return  result.text


def genai_vision_first_half(detected_text, model):
    result = model.generate_content(
        [detected_text,"\n\n", "Give me No from {detected_text}, output must be just dictionary - No"]
    )#If the prompt includes the word "passport," it is flagged as harmful content.
    return  result.text


def genai_vision_second_half(detected_text, model):
    result = model.generate_content(
        [detected_text,"\n\n", "give me issue_number, passport_number, name, surname, father name, mother name, date_of_birth, place_of_birth, nationality, gender(M/F), and both lines of the MRZ from {detected_text}, please give me output as just dictionary - issue_number, passport_number, full_name, first_name, last_name, father_name, mother_name, dob, place_of_birth, nationality, gender, mrz1, mrz2. Note that mrz1 is the line that starts with P and contains name"]
    )
    return  result.text


def genai_vision_mrz(detected_text, model):
    result = model.generate_content(
        [detected_text,"\n\n", "give me 'document_number', 'nationality', 'birth_date'(dd/mm/yyyy format), 'gender', 'expiration_date'(dd/mm/yyyy format) as dictionary from provided mrz. Dont write anything just return dictionary"]
    )
    return  result.text

def fix_dob(passport_text):
    dob = ''
    expiry = ''
    issue_date = ''
    try:
        matches = re.findall(r'\b\d{2}[\s/\-.]+\d{2}[\s/\-.]+\d{4}\b', passport_text, re.DOTALL)
        date_objects = [datetime.strptime(re.sub(r'[\s/\-.]+', ' ', date).strip(), '%d %m %Y') for date in matches]
        sorted_dates = sorted(date_objects)
        sorted_date_strings = [date.strftime('%d %m %Y') for date in sorted_dates]

        if len(sorted_date_strings) > 1:
            dob = sorted_date_strings[0]
            issue_date = sorted_date_strings[1]
            expiry = sorted_date_strings[-1]
    except:
        matches = re.findall(r'\b\d{2}[./]\d{2}[./]\d{4}\b', passport_text)
        date_objects = [datetime.strptime(date.replace('.', '/'), '%d/%m/%Y') for date in matches]
        sorted_dates = sorted(date_objects)
        sorted_date_strings = [date.strftime('%d/%m/%Y') for date in sorted_dates]

        if len(sorted_date_strings)>1:
            dob = sorted_date_strings[0]
            issue_date = sorted_date_strings[1]
            expiry = sorted_date_strings[-1]
        else:
            matches = re.findall(r'\d{4}-\d{2}-\d{2}', passport_text)
            date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in matches]
            sorted_dates = sorted(date_objects)
            sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

            if len(sorted_date_strings)>1:
                dob = sorted_date_strings[0].replace('-', '/')
                issue_date = sorted_date_strings[1].replace('-', '/')
                expiry = sorted_date_strings[-1].replace('-', '/')
            
            else:
                matches = re.findall(r'\d{2}-\d{2}-\d{4}', passport_text)
                date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in matches]
                sorted_dates = sorted(date_objects)
                sorted_date_strings = [date.strftime('%d-%m-%Y') for date in sorted_dates]

                if sorted_date_strings:
                    dob = sorted_date_strings[0].replace('-', '/')
                    issue_date = sorted_date_strings[1].replace('-', '/')
                    expiry = sorted_date_strings[-1].replace('-', '/')

    print(f"\nDOB: {dob}, Issue Date: {issue_date}, Expiry: {expiry}\n")
    return dob, issue_date, expiry

def mrz_data(merged_dict, model):
    # try:
    input_mrz_2 = merged_dict['mrz2']
    match = re.match(
        r"(\d{10})([A-Z]{3})(\d{6})(\d)([MF])(\d{6})(\d)", 
        input_mrz_2
    )

    if match:
        birth_date_raw = match.group(3)
        expiration_date_raw = match.group(6)

        birth_year_prefix = '19' if int(birth_date_raw[:2]) > 23 else '20'
        birth_date = f"{birth_date_raw[4:]}/{birth_date_raw[2:4]}/{birth_year_prefix}{birth_date_raw[:2]}"

        exp_year_prefix = '19' if int(expiration_date_raw[:2]) > 50 else '20'
        expiration_date = f"{expiration_date_raw[4:]}/{expiration_date_raw[2:4]}/{exp_year_prefix}{expiration_date_raw[:2]}"

        result_dict = {
            'passport_number': match.group(1),
            'nationality': match.group(2),
            'dob': birth_date, 
            'gender': match.group(5),
            'expiry_date': expiration_date
        }
        print(f"\nResult_dict from MRZ: {result_dict}\n")
    else:
        mrz_json = genai_vision_mrz(input_mrz_2, model)
        json_str = mrz_json.replace('```json', '').replace('```', '').strip()
        json_str = json_str.replace('null', 'None')
        result_dict = eval(json_str)

    result_dict_name = {}
    input_mrz_1 = merged_dict['mrz1']
    match = re.match(r"P[<N]SYR([A-Z<]+)<<*([A-Z]+)<<*", input_mrz_1)
    if match:
        result_dict_name = {
            'last_name': match.group(1),
            'first_name': match.group(2)
        }
        result_dict_name['last_name'] = result_dict_name['last_name'].replace('<', ' ').strip()
        result_dict_name['first_name'] = result_dict_name['first_name'].replace('<', ' ').strip()
        
    else:
        match = re.match(r"PNSYR\s*([A-Za-z]+)(?:<+([A-Za-z]+))?<<*", input_mrz_1)
        if match:
            try:
                result_dict_name = {
                    'last_name': match.group(1),
                    'first_name': match.group(2)
                }
                result_dict_name['last_name'] = result_dict_name['last_name'].replace('<', ' ').strip()
                result_dict_name['first_name'] = result_dict_name['first_name'].replace('<', ' ').strip()
            except Exception as e:
                result_dict_name = {}
                print(f"Error: {e}")

    # Merge the name data and other MRZ data into dict_gemini
    merged_dict_mrz = {**merged_dict, **result_dict_name, **result_dict}

    # except Exception as e:
    #     print(f"Error: {e}")

    return merged_dict_mrz


def fill_with_mrz(dict_gemini, mrz_dict_final):
    fields_to_fill = ['last_name', 'first_name', 'nationality', 'dob', 'gender']
    for field in fields_to_fill:
        if not dict_gemini.get(field, ''):
            dict_gemini[field] = mrz_dict_final.get(field, '')
    return dict_gemini


def extract_passport_number(input_string):
    pattern = r'^(\d+)(?=[A-Z]{3})'
    
    match = re.search(pattern, input_string)
    
    if match:
        return match.group(1)
    else:
        return None
    
def syr_passport_extraction_front(passport_text_first, api_key):
    model = configure_genai(api_key)
    try:
        ## Process first half of the image
        passport_first_ai_result = genai_vision_second_half(passport_text_first, model)
        json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```', passport_first_ai_result, re.DOTALL)
        if json_match:
            json_str = json_match.group(2)
            dictionary_first_half = json.loads(json_str)

        else:
            json_str = passport_first_ai_result.replace('```json', '').replace('```', '').strip()
            json_str = json_str.replace('null', 'None')
            dictionary_first_half= eval(json_str)
        
        if dictionary_first_half.get('nationality', ''):
            if dictionary_first_half['nationality'].lower().startswith('syria'):
                dictionary_first_half['nationality'] = 'SYR'

    except Exception as e:
        print(f"Error occured in GenAI first half {e}")

    if dictionary_first_half and dictionary_first_half.get('passport_number', ''):
        passport_number = dictionary_first_half.pop('passport_number')
        passport_number = re.sub(r'\D', '', passport_number)

        dictionary_first_half['passport_number'] = passport_number

    merged_dict = {**dictionary_first_half}

    if merged_dict and merged_dict.get('birth_date', ''):
        merged_dict['dob'] = merged_dict.pop('birth_date')
    
    if merged_dict and merged_dict.get('birth_place', ''):
        merged_dict['place_of_birth'] = merged_dict.pop('birth_place')
    
    if merged_dict and (
        not merged_dict.get('dob') or
        not merged_dict.get('full_name') or
        not merged_dict.get('nationality') or
        not merged_dict.get('first_name') or
        not merged_dict.get('last_name')
    ):
        mrz_dict_final = mrz_data(merged_dict, model)
        merged_dict = fill_with_mrz(merged_dict, mrz_dict_final)
    
    passport_text = passport_text_first
    if merged_dict and not merged_dict.get('dob', ''):
        dob, issue_date, expiry = fix_dob(passport_text)
        merged_dict['dob'] = dob

    if not merged_dict.get('full_name', ''):
        merged_dict['full_name'] = f"{merged_dict.get('first_name', '')} {merged_dict.get('last_name', '')}"

    if not merged_dict.get('passport_number', ''):
        passport_number = extract_passport_number(merged_dict.get('mrz2', ''))
        merged_dict['passport_number'] = passport_number

    if merged_dict.get('passport_number', ''):
        passport_number = merged_dict['passport_number']
        if len(passport_number) < 9:
            passport_number = f"0{passport_number}"
        merged_dict['passport_number'] = passport_number
    
    if merged_dict.get('passport_number', ''):
        merged_dict['id_number'] = merged_dict['passport_number']

    if not merged_dict.get('mrz', ''):
        mrz1 = merged_dict.get('mrz1', '')
        mrz2 = merged_dict.get('mrz2', '')
        if mrz1 and mrz2:
            merged_dict['mrz'] = f"{mrz1} {mrz2}"

    if "gender" in merged_dict:
        gender = merged_dict["gender"].strip().upper()
        if gender == "F":
            merged_dict["gender"] = "FEMALE"
        elif gender == "M":
            merged_dict["gender"] = "MALE"

    if 'gender' in merged_dict:
        merged_dict["gender"] = merged_dict["gender"].strip().upper()

    if merged_dict.get('nationality', ''):
        nationality = merged_dict.get('nationality', '')
        if nationality and len(nationality.split(' ')) > 1:
            merged_dict['nationality'] = 'SYR'

    if not merged_dict.get('nationality', ''):
        merged_dict['nationality'] = 'SYR'
    
    merged_dict['issuing_country'] = 'SYR'

    return merged_dict

def genai_vision_back(detected_text, model):
    result = model.generate_content(
        [detected_text,"\n\n", "give me date of issue(in dd/mm/yy format), expiry date (in dd/mm/yy format), place of issue, and national number from {detected_text}, please give me output as just dictionary - issuing_date, expiry_date, place_of_issue, national_number"]
    )
    return  result.text

def find_issue_date_and_expiry(passport_text_back):
    date_pattern = re.compile(r'\b\d{2}/\d{2}/\d{4}\b')
    matches = date_pattern.findall(passport_text_back)
    
    if not matches:
        return None, None
    
    date_objects = [datetime.strptime(date, '%d/%m/%Y') for date in matches]
    sorted_dates = sorted(date_objects)
    
    issuing_date = sorted_dates[0].strftime('%d/%m/%Y')
    expiry_date = sorted_dates[-1].strftime('%d/%m/%Y')
    
    return issuing_date, expiry_date

def extract_national_number(passport_text_back):
    national_number_pattern = re.compile(r'\b\d{3}-\d{8}\b')
    match = national_number_pattern.search(passport_text_back)
    
    if match:
        return match.group(0)
    else:
        return None
    

def syr_passport_extraction_back(passport_text_back, api_key):
    model = configure_genai(api_key)
    place_of_issue = ''
    result_ai = genai_vision_back(passport_text_back, model)
    try:
        json_str = result_ai.replace('```json', '').replace('```', '').strip()
        json_str = json_str.replace('null', 'None')
        try:
            passport_back_data = eval(json_str)
            issue_date = passport_back_data.get('issuing_date', '')
            expiry_date = passport_back_data.get('expiry_date', '')
            # Validate date format
            if not is_valid_date(issue_date) or not is_valid_date(expiry_date):
                raise ValueError("Invalid date format")

        except Exception as e:
            print(f"Error in parsing or validating dates: {e}")
            passport_back_data = {'issuing_date': '', 'expiry_date': '', 'national_number': '', 'place_of_issue': ''}
            try:
                issue_date, expiry = find_issue_date_and_expiry(passport_text_back)
                if issue_date and expiry:
                    passport_back_data = {
                    'issuing_date': issue_date,
                    'expiry_date': expiry
                    }
                
                national_number = extract_national_number(passport_text_back)
                if national_number:
                    passport_back_data['national_number'] = national_number

            except Exception as e:
                print(f"Error occurred in finding dates: {e}")
                passport_back_data = {}
    
    except Exception as e:
        print(f"Error occured in GenAI back {e}")
        passport_back_data = {}
        try:
            issue_date, expiry = find_issue_date_and_expiry(passport_text_back)
            if issue_date and expiry:
                passport_back_data = {
                    'issuing_date': issue_date,
                    'expiry_date': expiry
                }

            national_number = extract_national_number(passport_text_back)
            if national_number:
                passport_back_data['national_number'] = national_number

        except Exception as e:
            print(f"Error occured in finding dates {e}")
            passport_back_data = {}

    if not passport_back_data.get('place_of_issue', ''):
        json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```', result_ai, re.DOTALL)
        if json_match:
            json_str = json_match.group(2)
            dictionary_second_half = json.loads(json_str)
            place_of_issue = dictionary_second_half.get('place_of_issue', '')
            passport_back_data['place_of_issue'] = place_of_issue

        else:
            json_str = result_ai.replace('```json', '').replace('```', '').strip()
            json_str = json_str.replace('null', 'None')
            dictionary_second_half= eval(json_str)

            place_of_issue = dictionary_second_half.get('place_of_issue', '')
            passport_back_data['place_of_issue'] = place_of_issue
    else:
        passport_back_data['place_of_issue'] = ''
        
    return passport_back_data 

