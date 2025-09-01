from googletrans import Translator
import re
from datetime import datetime
import gender_guesser.detector as gender
import pycountry
from rapidfuzz import fuzz
from idvpackage.common import *

translator = Translator()


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

def extract_mother_name_and_surname(text):

    pattern_mother_name = r"(?:Mother's Name\.?|Mother Name)\s*[:：.]?\s*(?:Date of Birth\s*)?\s*(?:\d{4}-\d{2}-\d{2})?\s*([A-Z]+(?:\s+[A-Z]+)+)"
    mother_name_match = re.search(pattern_mother_name, text, re.IGNORECASE)

   
    mother_first_name = None
    mother_surname = None
    if mother_name_match:
        mother_name_full = mother_name_match.group(1).strip()
        # Split the full name to extract first name and surname
        name_parts = mother_name_full.split()
        if len(name_parts) >= 2:
            mother_first_name = name_parts[0]
            mother_surname = " ".join(name_parts[1:])

    if mother_surname:
       
        mother_surname = re.sub(r'\b(Date of Expiry|Date of Issue|Issuing Authority|Date|P|REPUBLIC OF IRAQ|Passport|Type|BAGHDAD|ananda|INTER|Issuing|Author|OF IRAQ assport|assport)\b', '', mother_surname, flags=re.IGNORECASE)
        mother_surname = re.sub(r'\s+', ' ', mother_surname).strip()

    
    return {"mother_first_name": mother_first_name, "mother_last_name": mother_surname}

def get_dates_to_generic_format(date):
    formats = ["%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date, fmt).strftime("%d/%m/%Y")
        except ValueError:
            pass
    return None


def validate_date(date):
    try:
        date = datetime.strptime(date, "%d-%m-%Y")
        return date.strftime("%d-%m-%Y")
    except ValueError:
        try:
            date = datetime.strptime(date, "%d/%m/%Y")
            return date.strftime("%d/%m/%Y")
        except:
            return ''

def identify_gender(name):
    d = gender.Detector()
    gender_prediction = d.get_gender(name)
    return gender_prediction


def translated_gender_identifier(passport_text):
    translator = Translator()
    try:
        trans_res = translator.translate(passport_text, src='ar', dest='en').text 
    except:
        from deep_translator import GoogleTranslator
        trans_res = GoogleTranslator('ar', 'en').translate(passport_text)
    if re.search('male', trans_res, re.IGNORECASE):
        return 'M'
    if re.search('female', trans_res, re.IGNORECASE):
        return 'F'

    return ''


def extract_names(passport_text):
    try:
        pattern = r'Full Name\s+([A-Z\s-]+)\nSurname\s+([A-Z\s-]+)'
        matches = re.search(pattern, passport_text)
        if matches:
            name = matches.group(1).strip()
            last_name = matches.group(2).strip()

            return name, last_name
        else:
            pattern = r'Full Name\s+([A-Z][A-Za-z\s-]+)|Name\s+([A-Z][A-Za-z\s-]+)|Sumame\s+([A-Z]+)|Surname\s+([A-Z]+)'

            matches = re.findall(pattern, passport_text)
            clean_matches = [match[0].strip() if match[0] else match[1] for match in matches]

            if len(clean_matches) > 1:
                name, last_name = clean_matches[0], clean_matches[1]

                if '\n' in name:
                    name_list = name.split("\n")
                    name_list.remove('IRQ')
                    name_list = [word for word in name_list if word.isupper()]

                    if not name_list[0] == 'IRQ':
                        if len(name_list) > 1:
                            name = name_list[0]
                            last_name = name_list[1]
                            if len(last_name)<2:
                                last_name = ''
                        if len(name_list) == 1:
                            name = name_list[0]

            elif len(matches) == 1:
                name, last_name = clean_matches[0].split("Surname")
                if len(name.split(" ")) > 3:
                    name_list = name.split("\n")
                    name = name_list[1]
                if len(last_name)>1:
                    last_name.split("\n")[0]

            if not last_name or len(last_name)<3:
                name_pattern = r"[A-Z<]+<<[A-Z<]+<"
                name_match = re.search(name_pattern, passport_text)
                if name_match:
                    names = name_match.group(0)
                    
                    extracted_text = names.replace('<', ' ')
                    # print(f"TEXT: {extracted_text}")
                    name_list = extracted_text.strip().split()
                    # name = ' '.join(name_list[1:])
                    last_name = name_list[0]

            return name.replace("\n", ""), last_name.replace("\n", "")
    except:
        return '', ''


def load_nationality_keywords():
    countries = pycountry.countries
    nationality_keywords = set()

    # Common suffixes for demonyms
    demonym_suffixes = ['ian', 'ese', 'ish', 'i', 'ic', 'an', 'nian']

    for country in countries:
        nationality_keywords.add(country.name.upper())
        nationality_keywords.add(country.alpha_3.upper())

        # Adding guessed demonyms
        for suffix in demonym_suffixes:
            demonym = country.name.upper() + suffix
            nationality_keywords.add(demonym.upper())

        # Add common demonyms if the official name is available
        if hasattr(country, 'official_name'):
            nationality_keywords.add(country.official_name.upper())
            for suffix in demonym_suffixes:
                demonym = country.official_name.upper() + suffix
                nationality_keywords.add(demonym.upper())

    return nationality_keywords


def extract_names_exception(passport_text, only_last_name=False):
    ## REMOVE REDUNDANT WORDS AFFECTING ALGO
    threshold = 50
    passport_lines = passport_text.split("\n")
    keyword = 'WHEN NEEDED'
    for text in passport_lines:
        similarity = fuzz.partial_ratio(text.lower(), keyword.lower())
        if similarity >= threshold:
            passport_text = passport_text.replace(text, "")

    ## Find 3 consecutive uppercase words as name and single uppercase word as last name
    name_pattern = r'([A-Z]{3,} [A-Z]{3,} [A-Z]{1,}|[A-Z]{3,} [A-Z]{3,} [A-Z]{1,} [A-Z]{1,})\s+([A-Z-]+)'
    
    match = re.search(name_pattern, passport_text)
    
    name, last_name = '', ''

    if match:
        name = match.group(1).strip()
        last_name = match.group(2).strip()

        try:
            if len(last_name) < 3:
                escaped_keyword_start = re.escape(name)
                escaped_keyword_end = re.escape('Exp')

                subsequent_search_pattern = fr"(?<={escaped_keyword_start})(.*?)(?={escaped_keyword_end})"
                intermediate_text = re.search(subsequent_search_pattern, passport_text, re.DOTALL)

                if intermediate_text:
                    intermediate_text = intermediate_text.group(1)
                    all_caps_words = re.findall(r"\b[A-Z][A-Z ]+\b", intermediate_text)

                    if all_caps_words:
                        for word in all_caps_words:
                            if ' ' not in word:
                                last_name = word
                                break
        except:
            pass

        return name, last_name
    
    elif only_last_name:
        escaped_keyword_start = re.escape('Name')
        escaped_keyword_end = re.escape('Exp')

        subsequent_search_pattern = fr"(?<={escaped_keyword_start})(.*?)(?={escaped_keyword_end})"
        intermediate_text = re.search(subsequent_search_pattern, passport_text, re.DOTALL)

        last_name = ''
        if intermediate_text:
            intermediate_text = intermediate_text.group(1)
            all_caps_words = re.findall(r"\b[A-Z][A-Z ]+\b", intermediate_text)

            nationality_keywords = load_nationality_keywords()

            if all_caps_words:
                for word in all_caps_words:
                    if ' ' not in word and word not in nationality_keywords:
                        last_name = word
                        break
        
        return last_name

    else:
        return '', ''
    
def convert_to_mrz_date(date_str):
    if date_str:
        try:
            month, day, year = date_str.split('/')

            year_last_two_digits = year[-2:]

            mrz_date = year_last_two_digits + month.zfill(2) + day.zfill(2)

            return mrz_date
        except:
            return ''
    else:
        return ''

def find_nationality_in_text(text, nationality_keywords):
    import re
    for keyword in nationality_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            return keyword
    return None

def iraq_passport_extraction(passport_text):
    passport_details = {}

    patterns = {
        'passport_number': (r"([A-Da-d]\d{8}|[A-Da-d]\d{7})", lambda match: match.group(1) if match else ''),
        'passport_number_mrz': (r"([A-Za-z]\d{8}|[A-Za-z]\d{7})", lambda match: match.group(1) if match else ''),
        'dob_mrz': (r'(\d+)[MF]', lambda match: convert_dob(match.group(1)) if match else ''),
        'expiry_date_mrz': (r'[MF](\d+)', lambda match: convert_expiry_date(match.group(1)) if match else ''),
        'gender': (r'(\d)([A-Za-z])(\d)', lambda match: match.group(2) if match else '')
    }
    
    passport_text_clean = passport_text.replace(" ", "")
    
    mrz1_pattern = r"P<{COUNTRY_CODE}[A-Z<]+<<[A-Z<]+<"
    
    iso_nationalities = [country.alpha_3 for country in pycountry.countries]
    
    name_dict = {}
    for country_code in iso_nationalities:
        current_pattern = mrz1_pattern.format(COUNTRY_CODE=country_code)

        mrz1_match = re.search(current_pattern, passport_text_clean)
        if mrz1_match:
            mrz1 = mrz1_match.group(0)
            
            extracted_text = mrz1.replace('P<','').replace(country_code,'').replace('<', ' ')
            name_list = extracted_text.strip().split()
            name = ' '.join(name_list[1:])
            passport_surname = name_list[0]

            if re.search(r'\bal\b', passport_surname.lower()):
                passport_surname = '-'.join(name_list[0:2])
                name = ' '.join(name_list[2:])

            name_dict = {
                'nationality': country_code,
                'full_name': name,
                'last_name': passport_surname
            }

            passport_details.update(name_dict)
        
            break
        else:
            mrz1 = None
    
    if not mrz1:
        pattern = r"P[<\w@<]+<<[\w<]+<"
        matches = re.findall(pattern, passport_text)
        
        try:
            mrz1 = matches[0]
        except:
            mrz1 = ''

        if matches:
            processed_matches = matches[0][5:]
        
            extracted_text = processed_matches.replace('@', '').replace('<', ' ')
            name_list = extracted_text.strip().split()
            name = ' '.join(name_list[1:])
            passport_surname = name_list[0]
            if re.search(r'\bal\b', passport_surname.lower()) or re.search(r'\bl\b', passport_surname.lower()):
                passport_surname = '-'.join(name_list[0:2])
                name = ' '.join(name_list[2:])

            name_dict = {
                    'full_name': name,
                    'last_name': passport_surname
                }

            passport_details.update(name_dict)

    if not mrz1 or not name:
        pattern = r"(P<([A-Z]{3})((?:[<A-Z]+)+)<<)"
        matches = re.findall(pattern, passport_text)

        if matches:
            mrz1, raw_names = matches[0][0], matches[0][2]
            processed_names = raw_names.replace('<', ' ').strip()
            name_parts = processed_names.split()
            
            if len(name_parts) > 1 and re.search(r'\b(al|el)\b', name_parts[1].lower()):
                surname = ' '.join(name_parts[:2])
                given_names = ' '.join(name_parts[2:])
            else:
                surname = name_parts[0]
                given_names = ' '.join(name_parts[1:])

            name_dict = {
                    'full_name': given_names,
                    'last_name': surname
                }

            passport_details.update(name_dict)

    ## HANDLE NAME GENERIC FOR VALIDATION
    name_generic, passport_surname_generic = extract_names(passport_text)
    if len(name_generic.split(" "))<3:
        name_generic_temp, passport_surname_generic_temp = extract_names_exception(passport_text)
        if name_generic_temp:
            name_generic, passport_surname_generic = name_generic_temp, passport_surname_generic_temp
    if not passport_surname_generic:
        passport_surname_generic = extract_names_exception(passport_text, only_last_name=True)
    
    if not passport_surname_generic or passport_surname_generic=='IRAQI':
        pattern = r"(([A-Z]{3})((?:[<A-Z]+)+)<<)"
        matches = re.findall(pattern, passport_text.replace(' ', ''))

        if matches:
            surname = ''
            mrz1, raw_names = matches[0][0], matches[0][2]
            processed_names = raw_names.replace('<', ' ').strip()
            name_parts = processed_names.split()

            if len(name_parts) > 1 and re.search(r'\b(al|el)\b', name_parts[1].lower()):
                surname = ' '.join(name_parts[:2])
                given_names = ' '.join(name_parts[2:])
            else:
                surname = name_parts[0]
                given_names = ' '.join(name_parts[1:])

            passport_surname_generic = surname

    name_generic, passport_surname_generic = ''.join(filter(lambda x: x.isupper() or x == '-' or x == ' ', name_generic)), ''.join(filter(lambda x: x.isupper() or x == '-' or x == ' ', passport_surname_generic))
    name_dict = {
            'full_name_generic': name_generic,
            'surname_generic': passport_surname_generic
        }

    passport_details.update(name_dict)

    mrz2_pattern = r"\n[A-Z]\d+.*?(?=[<]{2,})"
    mrz2_matches = re.findall(mrz2_pattern, passport_text_clean)
    
    if mrz2_matches:
        mrz2 = mrz2_matches[0][1:]
    else:
        mrz2 = ''

    ## EXTRACTING FIELDS FROM MRZ2
    mrz2_keys = ['gender', 'passport_number_mrz', 'dob_mrz', 'expiry_date_mrz']

    for key, value in patterns.items():
        pattern = value[0]
        transform_func = value[1]

        text = passport_text
        if key in mrz2_keys:
            text = mrz2

        match = re.search(pattern, text)
        passport_details[key] = transform_func(match) if match else ''
    
    if passport_details['passport_number_mrz'] and (passport_details['passport_number_mrz']!=passport_details['passport_number']):
        passport_details['passport_number'] = passport_details['passport_number_mrz']

    ## HANDLE PASSPORT NO FROM MRZ
    if not passport_details.get('passport_number_mrz'):
        passport_number_pattern = r"([A-Za-z]\d{8,}[A-Za-z]{2,}.*?|[A-Za-z]*\d{8,}[A-Za-z]{2,}.*?)"
        passport_number_match = re.search(passport_number_pattern, passport_text_clean)
        if passport_number_match:
            passport_number = passport_number_match.group(1)
            passport_details['passport_number_mrz'] = passport_number[:9]
        
    ## HANDLE DOB DOE FROM MRZ
    if not (passport_details.get('dob_mrz') or passport_details.get('expiry_date_mrz')):
        dob_pattern = r"(\d{7})[MF]"
        dob_match = re.search(dob_pattern, passport_text_clean)
        if dob_match:
            dob = dob_match.group(1)
            passport_details['dob_mrz'] = convert_dob(dob)
        else:
            dob_pattern = r'.*?[\S]R[\S](\d{9,})\b'
            dob_match = re.search(dob_pattern, passport_text_clean)
            if dob_match:
                dob = dob_match.group(1)[:7]
                passport_details['dob_mrz'] = validate_date(convert_dob(dob))
    
        doe_pattern = r"[MF](\d+)"
        doe_match = re.search(doe_pattern, passport_text_clean)
        if doe_match:
            expiry = doe_match.group(1)
            passport_details['expiry_date_mrz'] = validate_date(convert_expiry_date(expiry))
        else:
            doe_pattern = r'.*?[\S]R[\S](\d{9,})\b'
            doe_match = re.search(doe_pattern, passport_text_clean)
            if doe_match:
                expiry = doe_match.group(1)[8:]
                passport_details['expiry_date_mrz'] = validate_date(convert_expiry_date(expiry))

    ## HANDLE DOB AND DOE CASES FROM GENERIC DATA FOR VALIDATION
    dob = ''
    expiry = ''
    issue_date = ''
    
    try:
        matches = re.findall(r'\d{4}/\d{2}/\d{2}', passport_text)
        date_objects = [datetime.strptime(date, '%d/%m/%Y') for date in matches]
        sorted_dates = sorted(set(date_objects))
        sorted_date_strings = [date.strftime('%d/%m/%Y') for date in sorted_dates]

        # print(f"DATES: {sorted_date_strings}")
        dob = sorted_date_strings[0]
        issue_date = sorted_date_strings[1]
        expiry = sorted_date_strings[-1]
    except:
        matches = re.findall(r'\b\d{2}[./]\d{2}[./]\d{4}\b', passport_text)
        # try:
        date_objects = [datetime.strptime(date.replace('.', '/'), '%d/%m/%Y') for date in matches]
        sorted_dates = sorted(set(date_objects))
        sorted_date_strings = [date.strftime('%d/%m/%Y') for date in sorted_dates]

        # print(f"DATES 2: {sorted_date_strings}")
        if len(sorted_date_strings)>1:
            dob = sorted_date_strings[0]
            issue_date = sorted_date_strings[1]
            expiry = sorted_date_strings[-1]
        else:
            # try:
                matches = re.findall(r'\d{4}-\d{2}-\d{2}', passport_text)
                date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in matches]
                sorted_dates = sorted(set(date_objects))
                sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

                # print(f"DATES 3: {sorted_date_strings}")
                if len(sorted_date_strings)>1:
                    dob = sorted_date_strings[0].replace('-', '/')
                    issue_date = sorted_date_strings[1].replace('-', '/')
                    expiry = sorted_date_strings[-1].replace('-', '/')
                
                else:
                    matches = re.findall(r'\d{2}-\d{2}-\d{4}', passport_text)
                    date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in matches]
                    sorted_dates = sorted(set(date_objects))
                    sorted_date_strings = [date.strftime('%d-%m-%Y') for date in sorted_dates]

                    if sorted_date_strings:
                        dob = sorted_date_strings[0].replace('-', '/')
                        issue_date = sorted_date_strings[1].replace('-', '/')
                        expiry = sorted_date_strings[-1].replace('-', '/')
        #         except:
        #             dob, expiry = '', ''
        # except:
        #     dob, expiry = '', ''

    passport_details['passport_date_of_birth_generic'] = get_dates_to_generic_format(dob)
    passport_details['passport_date_of_expiry_generic'] = get_dates_to_generic_format(expiry)
    passport_details['issue_date'] = get_dates_to_generic_format(issue_date)
    
    ## HANDLE GENDER CASES EXCEPTIONS
    if not (passport_details['gender']):
        gender_pattern = r'(\d)([MFmf])(\d)'
        gender_match = re.search(gender_pattern, passport_text_clean)
        if gender_match:
            passport_details['gender'] = gender_match.group(2)
        else:
            if re.search(r'ذكر', passport_text) or re.search(r'ذکر', passport_text):
                passport_details['gender'] = 'M'

            elif re.search(r'انثى', passport_text) or re.search(r'أنثى', passport_text):
                passport_details['gender'] = 'F'

            else:
                if passport_details.get('full_name'):
                    first_name = passport_details['full_name'].split()[0].capitalize()
                    predicted_gender = identify_gender(first_name)
                    passport_details['gender'] = 'M' if predicted_gender.lower() == 'male' else 'F' if predicted_gender.lower() == 'female' and predicted_gender != 'unknown' else translated_gender_identifier(passport_text)

    if not passport_details.get('nationality', ''):
        nationality_keywords = load_nationality_keywords()
        passport_text = passport_text.replace('REPUBLIC OF IRAQ', '').replace('IRQ', '')
        nationality = find_nationality_in_text(passport_text, nationality_keywords)
        
        passport_details['nationality'] = nationality

    if len(mrz1) < 40:
        mrz1_pattern = r'P<[A-Z]{3}[A-Z0-9<]{5,44}'
        match = re.search(mrz1_pattern, passport_text.replace(" ", ""))
        if match:
            mrz1 = match.group(0)

    if not mrz1:
        mrz1 = ''

    if mrz1 and len(mrz1) < 44:
        mrz1 = mrz1 = f"{mrz1}{'<' * (44 - len(mrz1))}"
        
    # print(passport_details)
    if passport_details.get('nationality', ''):
        if passport_details['nationality'] == 'IRAQI' or passport_details['nationality'] == 'IRAQ':
            passport_details['nationality'] = 'IRQ'

    if not mrz2:
        try:
            mrz2 = passport_details.get('passport_number', '') + passport_details.get('nationality', '') + convert_to_mrz_date(passport_details.get('dob_mrz', '')) + passport_details.get('gender', '') + convert_to_mrz_date(passport_details.get('expiry_date_mrz', ''))
        except:
            mrz2 = ''
    
    if len(mrz2) >= 28 and len(mrz2) < 40:
        mrz2 = mrz2 = f"{mrz2}{'<' * (44 - len(mrz2))}"

    passport_details['mrz'] = mrz1 + mrz2
    passport_details['mrz1'] = mrz1
    passport_details['mrz2'] = mrz2

    if "gender" in passport_details:
        gender = passport_details["gender"].strip().upper()
        if gender == "F":
            passport_details["gender"] = "FEMALE"
        elif gender == "M":
            passport_details["gender"] = "MALE"
    
    if 'gender' in passport_details:
        passport_details["gender"] = passport_details["gender"].strip().upper()


    # print(f"PASSPORT DETAILS HERE: {passport_details}")

    return passport_details
