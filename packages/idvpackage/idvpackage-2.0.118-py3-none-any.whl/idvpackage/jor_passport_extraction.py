import google.generativeai as genai
import re
from datetime import datetime
from googletrans import Translator
import json
import openai
import time

def configure_genai(api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    return model

def genai_vision_jor(detected_text, model):
        result = model.generate_content(
            [detected_text,"\n\n", "From provided {detected_text} give me all required information in english. full_name, first_name, last_name, mother_name, passport_number, dob(Date of Birth dd/mm/yy format), Place of Birth, gender(M/F), issuing_date(dd/mm/yy format), expiry_date (dd/mm/yy format), Place of Issue, nationality,  and both lines of the MRZ, please give me  just dictionary dont write anything else - full_name, first_name, last_name, mother_name, passport_number, dob, place_of_birth, gender, issuing_date, expiry_date, issuing_place, nationality, mrz1, mrz2. Note that mrz1 is the line that starts with P<JOR and mrz2 is the line that starts with passport number, Also note if you are unable to find the passport number directly then use mrz2 inital words that comes before the symbol '<' as the passport number"]
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

def mrz_add(dictionary_image_half):

    
    mrz_2 = dictionary_image_half['mrz2']
    mrz_1 = dictionary_image_half['mrz1']

    mrz_data_dict = {}


    pattern_surname = r'P<JOR([^<]+)'
    match_surname = re.search(pattern_surname, mrz_1)
    if match_surname:
        mrz_data_dict['last_name_mrz'] = match_surname.group(1)


    pattern_given_names = r'<([^<]+)<([^<]+)<([^<]+)<<'
    match_given_names = re.search(pattern_given_names, mrz_1)
    if match_given_names:
        mrz_data_dict['first_name_mrz'] = match_given_names.group(1)
        mrz_data_dict['middle_name_1'] = match_given_names.group(2)
        mrz_data_dict['middle_name_2'] = match_given_names.group(3)
    


    pattern_passport = r'^([A-Z0-9]+)<'
    match_passport = re.search(pattern_passport, mrz_2)
    if match_passport:
        passport_number = match_passport.group(1)
        mrz_data_dict['passport_number'] = passport_number
    

    
    pattern_nationality = r'<.[A-Z]{3}' 

    match_nationality = re.search(pattern_nationality, mrz_2)
    if match_nationality:
        nationality = match_nationality.group(0)[2:]
        mrz_data_dict['nationality'] = nationality
        

    
    pattern_birth_date = r'\d{7}<([0-9]{6})'
    match_birth_date = re.search(pattern_birth_date, mrz_2)
    if match_birth_date:
        birth_date_raw = match_birth_date.group(1)
        year_prefix = '19' if int(birth_date_raw[:2]) > 23 else '20'
        birth_date = f"{birth_date_raw[4:]}/{birth_date_raw[2:4]}/{year_prefix}{birth_date_raw[:2]}"
        mrz_data_dict['dob'] = birth_date
    

    
    pattern_gender = r'([MF])'
    match_gender = re.search(pattern_gender, mrz_2)
    if match_gender:
        gender = match_gender.group(1)
        mrz_data_dict['gender'] = gender
    

   
    pattern_expiry_date = r'[MF](\d{6})'
    match_expiry_date = re.search(pattern_expiry_date, mrz_2)
    if match_expiry_date:
        expiry_date_raw = match_expiry_date.group(1)
        year_prefix = '19' if int(expiry_date_raw[:2]) > 50 else '20'
        expiry_date = f"{expiry_date_raw[4:]}/{expiry_date_raw[2:4]}/{year_prefix}{expiry_date_raw[:2]}"
        mrz_data_dict['expiry_date'] = expiry_date
        

        

        for key, value in mrz_data_dict.items():
            if key in dictionary_image_half and dictionary_image_half[key] in ['None', None, 'N/A', '', ' ', 'NaN', 'nan', 'null']:
                dictionary_image_half[key] = value
            elif key not in dictionary_image_half:
                dictionary_image_half[key] = value

        
        if len(dictionary_image_half['last_name']) > 1:
            # Substitute last_name with last_name_mrz
            dictionary_image_half['last_name'] = dictionary_image_half['last_name_mrz']


    return dictionary_image_half

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

def make_api_request_with_retries(prompt: str, max_retries: int = 3, delay_seconds: float = 2):
    """
    Helper function to make API requests with retry logic using OpenAI
    """
    start_time = time.time()
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                temperature=0.4,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            result = response.choices[0].message.content
            
            try:
                api_response = json.loads(result)
            except json.JSONDecodeError:
                try:
                    json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```|\s*({.*?})', result, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(2) or json_match.group(3)
                        try:
                            api_response = json.loads(json_str)
                        except:
                            api_response = eval(json_str.replace("'", '"'))
                    else:
                        raise json.JSONDecodeError("No JSON found in response", result, 0)
                except Exception as e:
                    print(f"Error parsing response: {str(e)}")
                    raise
            
            # print(f"GenAI request took {time.time() - start_time:.2f} seconds")
            return api_response
            
        except Exception as e:
            print(f"Error during API request (attempt {attempt + 1} of {max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay_seconds)
            else:
                raise Exception(f"Max retries exceeded. Last error: {str(e)}")

def jordan_passport_extraction(passport_text, api_key):
    start_time = time.time()
    try:
        prompt = f"From provided text, give me all required information in english only. full_name, first_name, last_name, mother_name, passport_number, dob(Date of Birth dd/mm/yyyy format), Place of Birth, gender(M/F), issuing_date(dd/mm/yyyy format), expiry_date (dd/mm/yyyy format), Place of Issue, nationality, and both lines of the MRZ(mrz1, mrz2). Please give me just dictionary dont write anything else - full_name, first_name, last_name, mother_name, passport_number, dob, place_of_birth, gender, issuing_date, expiry_date, issuing_place, nationality, mrz1, mrz2. Note that mrz1 is the line that starts with P<JOR and mrz2 is the line that starts with passport number. Also note if you are unable to find the passport number directly then use mrz2 initial words that comes before the symbol '<' as the passport number. If there are any arabic words in mother_name, or place_of_birth, or authority, just keep the english words, do not ever include arabic words in the output. Here's the text: {passport_text}"

        passport_final_result = make_api_request_with_retries(prompt)

        # print(f"\nPassport GenAI result: {passport_final_result}\n")

        # try:
        #     passport_final_result = swap_dates_if_needed(passport_final_result)
        # except Exception as e:
        #     print(f"Error swapping dates: {e}")

        # try:
        #     passport_final_result = translate_arabic_words(passport_final_result)
        # except Exception as e:
        #     print(f"Error translating: {e}")

        if passport_final_result and not passport_final_result.get('passport_number', ''):
            passport_number_pattern = r"([A-Za-z]\d{8}|[A-Za-z]\d{7}|[A-Za-z]\d{6})"
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
            passport_final_result['nationality'] = 'JOR'
        
        if not passport_final_result.get('nationality', ''):
            passport_final_result['nationality'] = 'JOR'

        passport_final_result['issuing_country'] = 'JOR'
        
        processing_time = time.time() - start_time

        return passport_final_result

    except Exception as e:
        processing_time = time.time() - start_time
        print(f"Error occurred in passport extraction: {e}")
        print(f"Failed processing took {processing_time:.2f} seconds")
        return {}