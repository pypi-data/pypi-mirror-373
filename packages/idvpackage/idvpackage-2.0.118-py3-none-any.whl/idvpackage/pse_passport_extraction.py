import re
import google.generativeai as genai
from datetime import datetime
from googletrans import Translator
import json

def configure_genai(api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    return model

def genai_vision_pse(detected_text, model):
    result = model.generate_content(
        [detected_text, "\n\n", "From provided {detected_text}  give me all required information in english. full_name, first_name, last_name, mother_name, passport_number(only digits, i.e N° or No), id_number, dob(Date of Birth dd/mm/yy format), Place of Birth, gender(M/F), issuing_date(dd/mm/yy format), expiry_date (dd/mm/yy format), Place of Issue, occupation(profession), nationality  and both lines of the MRZ, please give me  just dictionary dont write anything else - full_name, first_name, last_name, mother_name, passport_number, id_number, dob, place_of_birth: gender, issuing_date, expiry_date, issuing_place, occupation, mrz1, mrz2. Note that mrz1 is the line that starts with P and mrz2 is the line that starts with passport number"]
    )
    return  result.text

def reformat_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        
        return date_obj.strftime('%d/%m/%Y')
    except ValueError:
        return date_str

def swap_dates_if_needed(data_dict):
    try:
        # Parse the dates
        issuing_date = datetime.strptime(data_dict['issuing_date'], '%d/%m/%Y')
        expiry_date = datetime.strptime(data_dict['expiry_date'], '%d/%m/%Y')
        
        if issuing_date > expiry_date:
            data_dict['issuing_date'], data_dict['expiry_date'] = data_dict['expiry_date'], data_dict['issuing_date']
            print("Dates swapped: Issuing date and expiry date were in the wrong order.")
    
    except ValueError as e:
        print(f"Error parsing dates: {e}")
    
    return  data_dict

def mrz_add(mrz_data_dict):
    mrz_2 = mrz_data_dict['mrz2']
    mrz_1 = mrz_data_dict['mrz1']

    # 1. Extract Passport Number
    try:
        if 'passport_number' not in mrz_data_dict:
            pattern_passport = r'^(\d{7})'
            match_passport = re.search(pattern_passport, mrz_2)
            if match_passport:
                passport_number = match_passport.group(1)
                mrz_data_dict['passport_number'] = passport_number
    except Exception as e:
        print(f"Error extracting passport number for PSE: {e}")

    # 2. Extract Nationality
    try:
        if 'nationality' not in mrz_data_dict:
            pattern_nationality = r'<\d([A-Z]{3})'
            match_nationality = re.search(pattern_nationality, mrz_2)
            if match_nationality:
                nationality = match_nationality.group(1)
                mrz_data_dict['nationality'] = nationality
    except Exception as e:
        print(f"Error extracting nationality for PSE: {e}")

    # 3. Extract Date of Birth (DD/MM/YYYY format)
    try:
        if 'dob' not in mrz_data_dict:
            pattern_birth_date = r'\d{7}<\d[A-Z]{3}(\d{6})'
            match_birth_date = re.search(pattern_birth_date, mrz_2)
            if match_birth_date:
                birth_date_raw = match_birth_date.group(1)
                year_prefix = '19' if int(birth_date_raw[:2]) > 23 else '20'
                birth_date = f"{birth_date_raw[4:]}/{birth_date_raw[2:4]}/{year_prefix}{birth_date_raw[:2]}"
                mrz_data_dict['dob'] = birth_date
    except Exception as e:
        print(f"Error extracting date of birth for PSE: {e}")

    # 4. Extract Gender
    try:
        if 'gender' not in mrz_data_dict:
            pattern_gender = r'[A-Z]{3}\d{6}([MF])'
            match_gender = re.search(pattern_gender, mrz_2)
            if match_gender:
                gender = match_gender.group(1)
                mrz_data_dict['gender'] = gender
    except Exception as e:
        print(f"Error extracting gender for PSE: {e}")

    # 5. Extract Expiration Date (DD/MM/YYYY format)
    try:
        if 'expiry_date' not in mrz_data_dict:
            pattern_expiration_date = r'[MF](\d{6})'
            match_expiration_date = re.search(pattern_expiration_date, mrz_2)
            if match_expiration_date:
                expiration_date_raw = match_expiration_date.group(1)
                year_prefix = '19' if int(expiration_date_raw[:2]) > 50 else '20'
                expiration_date = f"{expiration_date_raw[4:]}/{expiration_date_raw[2:4]}/{year_prefix}{expiration_date_raw[:2]}"
                mrz_data_dict['expiry_date'] = expiration_date
    except Exception as e:
        print(f"Error extracting expiration date for PSE: {e}")

    # 6. Extract Surname from MRZ_1
    # Updated to handle multiple variations of MRZ structures.
    try:
        if 'last_name' not in mrz_data_dict:
            pattern_surname = r'P<PSE([A-Z]+)<'
            match_surname = re.search(pattern_surname, mrz_1)
            if match_surname:
                surname = match_surname.group(1)
                mrz_data_dict['last_name'] = surname
    except  Exception as e:
        print(f"Error extracting surname for PSE: {e}")

    # 7. Extract Given Name (First Name) from MRZ_1
    # Modified pattern to not rely on `<F`, as MRZ_1 structure can vary.
    try:
        if 'first_name' not in mrz_data_dict:
            pattern_given_name = r'<([A-Z]+)<[A-Z]<'
            match_given_name = re.search(pattern_given_name, mrz_1)
            if match_given_name:
                given_name = match_given_name.group(1)
                mrz_data_dict['first_name'] = given_name
    except Exception as e:
        print(f"Error extracting first name for PSE: {e}")

    # 8. If the surname or name isn't filled, use a fallback approach
    # If MRZ_1 structure varies, you can adjust these patterns.
    try:
        if 'last_name' not in mrz_data_dict:
            # Fallback to capture everything after the country code
            fallback_pattern_surname = r'P<PSE([A-Z]+)'
            match_surname = re.search(fallback_pattern_surname, mrz_1)
            if match_surname:
                mrz_data_dict['last_name'] = match_surname.group(1)
    except Exception as e:
        print(f"Error extracting surname for PSE: {e}")
    
    try:
        if 'first_name' not in mrz_data_dict:
            # Fallback to capture first name in different structures
            fallback_pattern_given_name = r'<([A-Z]+)<'
            match_given_name = re.search(fallback_pattern_given_name, mrz_1)
            if match_given_name:
                mrz_data_dict['first_name'] = match_given_name.group(1)
    except Exception as e:
        print(f"Error extracting first name for PSE: {e}")

    return mrz_data_dict

def translate_arabic_words(dictionary):
    translator = Translator()
    translated_dict = {}
    for key, value in dictionary.items():
        if key not in ['mrz1', 'mrz2']:  
            if isinstance(value, str):  
                
                detected_lang = translator.detect(value).lang
                if detected_lang == 'ar':  
                    translated_text = translator.translate(value, src='ar', dest='en').text
                    translated_dict[key] = translated_text
                else:
                    translated_dict[key] = value
            else:
                translated_dict[key] = value
        else:
            
            translated_dict[key] = value
    return translated_dict

def extract_nationality(mrz_line):
    match = re.match(r"^.{10}([A-Z]{3})", mrz_line)
    if match:
        return match.group(1)
    else:
        return None
    
def palestine_passport_extraction(passport_text, api_key):
    try:
        model = configure_genai(api_key)
        jor_passport_result_ai = genai_vision_pse(passport_text, model)
        json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```', jor_passport_result_ai, re.DOTALL)
        if json_match:
            json_str = json_match.group(2)
            passport_final_result = json.loads(json_str)

        else:
            json_str = jor_passport_result_ai.replace('```json', '').replace('```', '').strip()
            json_str = json_str.replace('null', 'None')
            passport_final_result = eval(json_str)
        
        try:
            passport_final_result = mrz_add(passport_final_result)
        except Exception as e:
            print(f"Error adding MRZ data: {e}")

        try:
            passport_final_result = swap_dates_if_needed(passport_final_result)
        except Exception as e:
            print(f"Error swapping dates: {e}")

        try:
            passport_final_result = translate_arabic_words(passport_final_result)
        except Exception as e:
            print(f"Error translating: {e}")


        if passport_final_result and not passport_final_result.get('passport_number', ''):
            ## Passport Number Pattern
            passport_number_pattern = r"(\d{8}|\d{7}|\d{6})"
            passport_number_match = re.search(passport_number_pattern, passport_text)
            if passport_number_match:
                passport_number = passport_number_match.group(0)

                if passport_number:
                    passport_final_result['passport_number'] = passport_number
                else:
                    passport_number_match = re.search(passport_number_pattern, passport_final_result.get('mrz2', ''))
                    if passport_number_match:
                        passport_number = passport_number_match.group(0)
                        passport_final_result['passport_number'] = passport_number
            
        ## Nationality Pattern
        if 'nationality' not in passport_final_result:
            try:
                nationality = extract_nationality(passport_final_result.get('mrz2', ''))
                passport_final_result['nationality'] = nationality
            except:
                mrz2 = passport_final_result.get('mrz2', '')
                nationality_pattern = r'[A-Z]{3}'
                nationality_match = re.search(nationality_pattern, mrz2)
                if nationality_match:
                    nationality = nationality_match.group(0)
                    passport_final_result['nationality'] = nationality
                else:
                    mrz2 = passport_final_result.get('mrz2', '')
                    if mrz2:
                        nationality = mrz2.split('<')[0][-3:]
                        passport_final_result['nationality'] = nationality

        mrz1 = passport_final_result.get('mrz1', '')
        mrz2 = passport_final_result.get('mrz2', '')
        if mrz1 and mrz2:
            passport_final_result['mrz'] = f"{mrz1} {mrz2}"
        
        if "gender" in passport_final_result:
            gender = passport_final_result["gender"].strip().upper()
            if gender == "F":
                passport_final_result["gender"] = "FEMALE"
            elif gender == "M":
                passport_final_result["gender"] = "MALE"
    
        if 'gender' in passport_final_result:
            passport_final_result["gender"] = passport_final_result["gender"].strip().upper()
        
        if 'issuing_place' in passport_final_result:
            passport_final_result['place_of_issue'] = passport_final_result['issuing_place'].strip().upper()

        if passport_final_result.get('nationality', '') and len(passport_final_result['nationality']) > 3:
            passport_final_result['nationality'] = 'PSE'

        if not passport_final_result.get('nationality', ''):
            passport_final_result['nationality'] = 'PSE'

        passport_final_result['issuing_country'] = 'PSE'

        return passport_final_result

    except Exception as e:
        print(f"Error occured in GenAI {e}")
        return {}

