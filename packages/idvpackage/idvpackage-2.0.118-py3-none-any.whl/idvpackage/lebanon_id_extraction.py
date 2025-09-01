import json
import re
import time
from typing import Any, Dict
import openai
from idvpackage.common import eastern_arabic_to_english, english_to_eastern_arabic
from deep_translator import GoogleTranslator

def extract_id_numbers(raw_data):
    match = re.search(r'[\d٠١٢٣٤٥٦٧٨٩]{7,12}', raw_data)
    
    if match:
        id_number_ar = match.group(0)
        id_number_ar_padded = id_number_ar.zfill(12).replace("0", "٠")
        id_number_ar_padded = english_to_eastern_arabic(id_number_ar_padded)
        id_number_en_padded = eastern_arabic_to_english(id_number_ar_padded)
        return id_number_ar_padded, id_number_en_padded
    else:
        return "", ""

def make_api_request_with_retries(prompt: str, max_retries: int = 3, delay_seconds: float = 2) -> Dict:
    """
    Helper function to make API requests with retry logic using OpenAI
    """
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
                return json.loads(result)
            except json.JSONDecodeError:
                try:
                    json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```|\s*({.*?})', result, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(2) or json_match.group(3)
                        try:
                            return json.loads(json_str)
                        except:
                            return eval(json_str.replace("'", '"'))
                except:
                    pass
            
            return json.loads(result)
            
        except Exception as e:
            print(f"Error during API request (attempt {attempt + 1} of {max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay_seconds)
            else:
                raise Exception(f"Max retries exceeded. Last error: {str(e)}")


def lebanon_front_id_extraction(raw_data: str) -> Dict:
    """
    Extract front ID data with retry logic
    """
    try:
        prompt = f"From the attached text, please extract the data in a structured format, the response should be a dictionary, having first_name(it can be 1 word or more, please extract accurately), father_name, mother_name, last_name, id_number, dob, place_of_birth, name(full name). Note: If there are more than 1 word for father_name or mother_name, you should pick it smartly, but make sure that it makes sense, don't pick random words for name. Note that the id_number should always be 12 digits, if the length is less than 12 then append 0 in the start for id_number_en and same way for id_number_ar. The extracted details should be in arabic and a transliterated version as well having key_name_en, including id_number, dob(dd/mm/yyyy), names, etc.. the structure should be 'first_name_ar', 'first_name_en', id_number_ar, id_number_en, dob_ar, dob_en, place_of_birth_ar, place_of_birth_en, etc. Make sure that the response should only contain a dictionary, and nothing else. Here's the text for your task: {raw_data}"
        
        front_data = make_api_request_with_retries(prompt)
        
        if front_data:
            if front_data.get('place_of_birth_ar', ''):
                front_data['place_of_birth'] = front_data.pop('place_of_birth_ar', '')
            if front_data.get('first_name_ar', ''):
                front_data['first_name'] = front_data.pop('first_name_ar', '')
            if front_data.get('last_name_ar', ''):
                front_data['last_name'] = front_data.pop('last_name_ar', '')
            if front_data.get('father_name_ar', ''):
                front_data['father_name'] = front_data.pop('father_name_ar', '')
            if front_data.get('name_ar', ''):
                front_data['name'] = front_data.pop('name_ar', '')
            if front_data.get('mother_name_ar', ''):
                front_data['mother_name'] = front_data.pop('mother_name_ar', '')
            if front_data.get('id_number_ar', ''):
                front_data['id_number'] = eastern_arabic_to_english(front_data.get('id_number_ar', ''))
                front_data.pop('id_number_en', '')
            if front_data.get('dob_en', ''):
                front_data['dob'] = front_data.pop('dob_en', '')
            
            try:
                id_number_ar, id_number_en = extract_id_numbers(raw_data)
                if id_number_ar and id_number_en:
                    if id_number_en != '000000000000':
                        front_data['id_number_ar'] = id_number_ar
                        front_data['id_number'] = id_number_en
            except Exception:
                pass

            if front_data.get('id_number', ''):
                if front_data['id_number'] == '000000000000':
                    front_data['id_number'] = ''
                    front_data['id_number_ar'] = ''

    except Exception as e:
        print(f"Error in processing the extracted data: {e}")
        front_data = {}

    return front_data


def extract_gender_normalized(extracted_text):
    gender_ar, gender = '', ''
    
    if re.search(r'ذكر', extracted_text) or re.search(r'ذکر', extracted_text):
        gender_ar = 'ذكر'
        gender = 'MALE'

    elif re.search(r'انثى', extracted_text) or re.search(r'أنثى', extracted_text) or re.search(r'انتی', extracted_text) or re.search(r'انٹی', extracted_text):
        gender_ar = 'انثى'
        gender = 'FEMALE'
    
    return gender_ar, gender


def lebanon_back_id_extraction(raw_data: str) -> Dict:
    """
    Extract back ID data with retry logic
    """
    try:
        prompt = f"From the attached text, please extract the data in a structured format, the response should be a dictionary, having Gender(MALE, FEMALE if no information then null), Marital Status(single, married, widow, if no information then null), Date of Issue, Record Number, Village, Governorate, District. The extracted details should be in arabic and a transliterated version as well having key_name_en, including gender, marital_status, village, etc.. the structure should be 'marital_status_ar', 'marital_status_en', issue_date(dd/mm/yyyy), issue_date_ar(dd/mm/yyyy), governorate_ar, governorate_en, district_ar, district_en, etc. Make sure that the response should only contain a dictionary, and nothing else. Here's the text for your task: {raw_data}"

        back_data = make_api_request_with_retries(prompt)
        
        if back_data:
            if back_data.get('marital_status_ar', ''):
                back_data['marital_status'] = back_data.pop('marital_status_ar', '')

            if back_data.get('gender_en', ''):
                back_data['gender'] = back_data.pop('gender_en', '')
            
            if not back_data.get('gender_en', '') and back_data.get('gender', ''):
                back_data['gender'] = back_data.pop('gender', '')

            if back_data.get('record_number', '') and not back_data.get('record_number_en', ''):
                back_data['card_number_ar'] = back_data.get('record_number', '')
                back_data['card_number'] = eastern_arabic_to_english(back_data.get('record_number', ''))

            if back_data.get('record_number_en', ''):
                back_data['card_number'] = back_data.pop('record_number_en', '')
            
            if back_data.get('record_number_ar', ''):
                back_data['card_number_ar'] = back_data.pop('record_number_ar', '')
            
            if not back_data.get('gender', ''):
                gender_pattern = r"(?:الجنس|Gender)\s*:\s*([\w]+)"
                gender_match = re.search(gender_pattern, raw_data, re.IGNORECASE)

                gender_ar, gender = '', ''
                if gender_match:
                    gender_ar = gender_match.group(1)
                    gender = GoogleTranslator(dest = 'en').translate(gender_ar)
                    if gender.lower() == 'male':
                        gender = 'MALE'
                    elif gender.lower() == 'female' or gender.lower() == 'feminine':
                        gender = 'FEMALE'

                if not gender_ar:
                    gender_ar, gender = extract_gender_normalized(raw_data)
                
                if gender:
                    back_data['gender'] = gender
                
                if gender_ar:
                    back_data['gender_ar'] = gender_ar
            
            if not back_data.get('issue_date', '') and back_data.get('issue_date_en', ''):
                back_data['issue_date'] = back_data.pop('issue_date_en', '')

            back_data['nationality'], back_data['issuing_country'] = 'LBN', 'LBN'

    except Exception as e:
        print(f"Error in processing the extracted data: {e}")
        back_data = {}
    
    return back_data

