import re
from datetime import datetime
import pycountry
from rapidfuzz import fuzz
from idvpackage.common import *
import json
import time
import openai

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


def extract_pob_and_poi(passport_data, dob_for_match, passport_number_mrz):
    place_of_birth, place_of_issue = '', ''
    try:
        pattern = re.compile(rf"Nationality(.*?){dob_for_match}|Nation(.*?){dob_for_match}", re.DOTALL)
        match = pattern.search(passport_data)
        if match:
            substring = match.group(1) or match.group(2)
            if substring:
                capital_letters = re.findall(r'[A-Z]{2,}', substring)
                if not capital_letters or len(capital_letters)<=1:
                    match, substring = '', ''

        if not match:
            pattern = re.compile(rf"Place(.*?)PCSDN", re.DOTALL)
            match = pattern.search(passport_data)

            if not match:
                pattern_phsdn = re.compile(rf"{dob_for_match}(.*?)PHSDN", re.DOTALL)
                match = pattern_phsdn.search(passport_data)

            if match:
                substring = match.group(1)
                if substring:
                    capital_letters = re.findall(r'[A-Z]{2,}', substring)
                    if not capital_letters or len(capital_letters)<=1:
                        match, substring = '', ''
            
            if not match:
                pattern = re.compile(rf"{passport_number_mrz}(.*?){dob_for_match}", re.DOTALL)
                match = pattern.search(passport_data.replace('O', '0'))

            if match:
                substring_orig = match.group(1)
                lines = substring_orig.split('\n')
                arabic_and_english_pattern = re.compile(r'[\u0600-\u06FF].*[A-Z]|[A-Z].*[\u0600-\u06FF]')
                filtered_lines = [line for line in lines if arabic_and_english_pattern.search(line) and 'SDN' not in line]
                substring = '\n'.join(filtered_lines)
                substring = substring.replace('0', 'O')
                if substring:
                    capital_letters = re.findall(r'[A-Z\d]{2,}', substring)
                    if capital_letters and len(capital_letters)<2:
                        capital_letters = re.findall(r'[A-Z\d]{2,}', substring_orig)
                        substring = '\n'.join(capital_letters)
                    else:
                        substring = substring

        if substring:
            #print(f'SUBSTRING: {substring}')
            capital_letters = re.findall(r'[A-Z]{2,}', substring)
            capital_letters = [re.sub(r'\d+', '', i) for i in capital_letters]
            capital_letters = [i for i in capital_letters if not (len(i)<=2 or i=='SDN' or i=='') or i=='AL']
            #print(f'CAPS NEW: {capital_letters}')
            # for item in ['SDN', 'MI', 'MY', 'MA', 'SS', 'MS', 'ME']:
            #     if item in capital_letters:
            #         capital_letters.remove(item)
                
            if len(capital_letters)>2 and ('AL' in capital_letters or 'NEW' in capital_letters) and (capital_letters[0]=='AL' or capital_letters[0]=='NEW'):
                place_of_birth = capital_letters[0] +' '+ capital_letters[1]
                place_of_issue = capital_letters[2]
            elif len(capital_letters)<=3:
                if len(capital_letters) > 2:
                    place_of_birth = capital_letters[0]
                    place_of_issue = capital_letters[1] +' '+ capital_letters[2]

                else:
                    place_of_birth = capital_letters[0]
                    place_of_issue = capital_letters[1]
            else:
                place_of_birth = capital_letters[0] +' '+ capital_letters[1]
                place_of_issue = capital_letters[2] +' '+ capital_letters[3]
    except:
        place_of_birth, place_of_issue = '', ''
    
    return place_of_birth, place_of_issue


def find_names_with_context(text, keywords):
    lines = text.strip().split('\n')
    keyword_set = set(keywords)
    
    arabic_word_pattern = re.compile(r'[\u0600-\u06FF]+')
    english_word_pattern = re.compile(r'[A-Za-z]+')
    arabic_name_candidates = []
    
    def contains_three_arabic_words(line):
        return len(arabic_word_pattern.findall(line)) >= 3
    
    def is_mixed_language(line):
        return bool(arabic_word_pattern.search(line)) and bool(english_word_pattern.search(line))
    
    for i, line in enumerate(lines):
        words = set(line.split())
        if words & keyword_set:
            if i > 0 and contains_three_arabic_words(lines[i - 1]) and not is_mixed_language(lines[i - 1]):
                arabic_name_candidates.append((line, lines[i - 1]))
            elif i < len(lines) - 1 and contains_three_arabic_words(lines[i + 1]) and not is_mixed_language(lines[i + 1]):
                arabic_name_candidates.append((line, lines[i + 1]))
    
    return arabic_name_candidates


def sdn_passport_extraction(passport_text):
    passport_details = {}

    patterns = {
        'passport_number': (r"([A-Za-z]\d{8}|[A-Za-z]\d{7})", lambda match: match.group(1) if match else ''),
        'passport_number_mrz': (r"([A-Za-z]\d{8}|[A-Za-z]\d{7})", lambda match: match.group(1) if match else ''),
        'dob_mrz': (r'(\d+)[MF]', lambda match: convert_dob(match.group(1)) if match else ''),
        'expiry_date_mrz': (r'[MF](\d+)', lambda match: convert_expiry_date(match.group(1)) if match else ''),
        'gender': (r'(\d)([A-Za-z])(\d)', lambda match: match.group(2) if match else '')
    }
    
    passport_text_clean = passport_text.replace(" ", "")
    
    mrz1_pattern = r"PCSDN[A-Z<]+<<[A-Z<]+<"
    matches = re.findall(mrz1_pattern, passport_text_clean)
        
    try:
        mrz1 = matches[0]
    except:
        try:
            mrz1_pattern = r"PHSDN[A-Z<]+<<[A-Z<]+<"
            matches = re.findall(mrz1_pattern, passport_text_clean)
            mrz1 = matches[0]
        except:
            mrz1 = ''

    name_dict = {}
    
    try:
        pattern = r"(PC([A-Z]{3})((?:[<A-Z]+)+)<)"
        matches = re.findall(pattern, passport_text_clean)

        if matches:
            mrz1, raw_names = matches[0][0], matches[0][2]
            processed_names = raw_names.replace('<', ' ').strip()
            # name_parts = processed_names.split()
            
            # if len(name_parts) > 1 and re.search(r'\b(al|el)\b', name_parts[1].lower()):
            #     surname = ' '.join(name_parts[:2])
            #     given_names = ' '.join(name_parts[2:])
            # else:
            #     surname = name_parts[0]
            #     given_names = ' '.join(name_parts[1:])

            # print(f'\nNAME DICT HERE 2: {processed_names}\n')

            passport_details['full_name'] = processed_names
        else:
            pattern = r"(PH([A-Z]{3})((?:[<A-Z]+)+)<)"
            matches = re.findall(pattern, passport_text_clean)

            if matches:
                mrz1, raw_names = matches[0][0], matches[0][2]
                processed_names = raw_names.replace('<', ' ').strip()
                # name_parts = processed_names.split()
                
                # if len(name_parts) > 1 and re.search(r'\b(al|el)\b', name_parts[1].lower()):
                #     surname = ' '.join(name_parts[:2])
                #     given_names = ' '.join(name_parts[2:])
                # else:
                #     surname = name_parts[0]
                #     given_names = ' '.join(name_parts[1:])

                #print(f'\nNAME DICT HERE 2: {processed_names}\n')

                passport_details['full_name'] = processed_names
    except:
        passport_details['full_name'] = ''

    if not passport_details.get('full_name', ''):
        pattern = r"SDN(((?:[<A-Z]+)+)<)"
        matches = re.findall(pattern, passport_text_clean)

        if matches:
            raw_names = matches[0][0]
            processed_names = raw_names.replace('<', ' ').strip()
            passport_details['full_name'] = processed_names

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
        matches = re.findall(r'\d{2}-\d{2}-\d{4}', passport_text)
        date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in matches]
        sorted_dates = sorted(set(date_objects))
        sorted_date_strings = [date.strftime('%d-%m-%Y') for date in sorted_dates]

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
            
            # print(f"DATES 4: {sorted_date_strings}")
            
            if sorted_date_strings:
                dob = sorted_date_strings[0].replace('-', '/')
                issue_date = sorted_date_strings[1].replace('-', '/')
                expiry = sorted_date_strings[-1].replace('-', '/')
       
    except:
        dob, issue_date, expiry = '', '', ''

    passport_details['dob'] = get_dates_to_generic_format(dob)
    passport_details['expiry_date'] = get_dates_to_generic_format(expiry)
    passport_details['issue_date'] = get_dates_to_generic_format(issue_date)
    
    ## HANDLE GENDER CASES EXCEPTIONS
    if not (passport_details['gender']):
        # print(f'inside gender case')
        gender_pattern = r'(\d)([MFmf])(\d)'
        gender_match = re.search(gender_pattern, passport_text_clean)
        if gender_match:
            passport_details['gender'] = gender_match.group(2)
    
    ## NATIONALITY FROM MRZ
    nationality_ptrn =  r"PC([A-Z]{3})"
    matches = re.findall(nationality_ptrn, passport_text)
    # print(f'Matches nationality: {matches}')
    try:
        nationality = matches[0]
        passport_details['nationality'] = nationality
    except:
        nationality = ''

    if not passport_details.get('nationality', ''):
        nationality_ptrn =  r"PH([A-Z]{3})"
        matches = re.findall(nationality_ptrn, passport_text)
        try:
            nationality = matches[0]
            passport_details['nationality'] = nationality
        except:
            nationality = ''

    ## NATIONALITY FROM GENERIC DATA
    if not passport_details.get('nationality', ''):
        nationality_keywords = load_nationality_keywords()
        nationality = find_nationality_in_text(passport_text, nationality_keywords)

        passport_details['nationality'] = nationality

    ## HANDLE NATIONA NUMBER HERE
    try:
        national_no_pattern = r'(\d{3}-\d{4}-\d{4})'
        national_no_match = re.search(national_no_pattern, passport_text)
        if national_no_match:
            passport_details['national_number'] = national_no_match.group(1)
        else:
            national_no_pattern = r'(\d{3}-\d{4}-\d{4})'
            national_no_match = re.search(national_no_pattern, passport_text_clean)
            if national_no_match:
                passport_details['national_number'] = national_no_match.group(1)
    except:
        passport_details['national_number'] = ''
    
    ## ELIMINATE DUPLICATED FIELDS AND KEEP ONLY ONE THAT HAS VALUE
    try:
        ### 1. Remove passport number and keep only passport number from mrz
        if not passport_details.get('passport_number_mrz', '') and passport_details.get('passport_number', ''):
            passport_details['passport_number_mrz'] = passport_details['passport_number']
        
        if passport_details.get('passport_number', ''):
            passport_details.pop('passport_number')
        
        ### 2. Remove dob from mrz and keep only dob from generic
        if not passport_details.get('dob', '') and passport_details.get('dob_mrz', ''):
            passport_details['dob'] = passport_details['dob_mrz']

        if passport_details.get('dob_mrz', ''):
            passport_details.pop('dob_mrz')

        ### 3. Remove expiry from mrz and keep only expiry from generic
        if not passport_details.get('expiry_date', '') and passport_details.get('expiry_date_mrz', ''):
            passport_details['expiry_date'] = passport_details['expiry_date_mrz']

        if passport_details.get('expiry_date_mrz'):
            passport_details.pop('expiry_date_mrz')
        
        if passport_details.get('passport_number_mrz', ''):
            passport_details['id_number'] = passport_details['passport_number_mrz']

        ### 4. Remove name from mrz and keep only name from generic
    except:
        pass

    ## HANDLE PLACE OF BIRTH AND PLACE OF ISSUE HERE
    # print(f"mrz: {passport_details.get('dob_mrz')}, dob: {passport_details.get('dob')}")
    dob_for_match = passport_details.get('dob', passport_details.get('dob_mrz')).replace('/', '-')
    pattern = re.compile(rf"{dob_for_match}(.*?)PCSDN|{dob_for_match}(.*?)SDN[A-Z]{{4,}}", re.DOTALL)
    match = pattern.search(passport_text)

    if not match:
        pattern_phsdn = re.compile(rf"{dob_for_match}(.*?)PHSDN", re.DOTALL)
        match = pattern_phsdn.search(passport_text)

    if match:
        substring = match.group(1) if match.group(1) is not None else match.group(2)
        name_list = passport_details.get('full_name', '').split(' ')
        capital_letters = re.findall(r'[A-Z]{2,}', substring)
        capital_letters = [re.sub(r'\d+', '', i) for i in capital_letters]
        capital_letters = [i for i in capital_letters if not (len(i)<=2 or i=='SDN' or i=='' or i in name_list) or i=='AL']
        # print(f'CAPS: {capital_letters}')
        # for item in ['SDN', 'MI', 'MY', 'MA', 'SS', 'MS', 'ME', 'SU']:
        #     if item in capital_letters:
        #         capital_letters.remove(item)

        try:
            if len(capital_letters)>2 and ('AL' in capital_letters or 'NEW' in capital_letters) and (capital_letters[0]=='AL' or capital_letters[0]=='NEW'):
                place_of_birth = capital_letters[0] +' '+ capital_letters[1]
                place_of_issue = capital_letters[2]
            elif len(capital_letters)<=3:
                if len(capital_letters) > 2:
                    place_of_birth = capital_letters[0]
                    place_of_issue = capital_letters[1] +' '+ capital_letters[2]

                else:
                    place_of_birth = capital_letters[0]
                    place_of_issue = capital_letters[1]
            else:
                place_of_birth = capital_letters[0] +' '+ capital_letters[1]
                place_of_issue = capital_letters[2] +' '+ capital_letters[3]
        except:
            place_of_birth, place_of_issue = extract_pob_and_poi(passport_text, dob_for_match, passport_details.get('passport_number_mrz', ''))

        passport_details['place_of_birth'] = place_of_birth
        passport_details['place_of_issue'] = place_of_issue
    else:
        try:
            place_of_birth, place_of_issue = extract_pob_and_poi(passport_text, dob_for_match, passport_details.get('passport_number_mrz', ''))
            passport_details['place_of_birth'] = place_of_birth
            passport_details['place_of_issue'] = place_of_issue
        except:
            passport_details['place_of_birth'] = ''
            passport_details['place_of_issue'] = ''


    ## HANDLE ARABIC NAME FROM PASSPORT
    pattern = re.compile(rf"SDN(.*?){passport_details.get('passport_number_mrz', '')}", re.DOTALL)
    match = re.findall(pattern, passport_text)

    if match:
        substring = match[0]
        arabic_regex = re.compile(r'^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s]+$')
        result = []

        for line in substring.split('\n'):
            if arabic_regex.match(line) and len(line.split()) >= 4:
                result.append(line)
        
        name_ar = ''
        if result:
            name_ar = ' '.join(result)
            passport_details['name_ar'] = name_ar

        # print(f'\nARABIC NAME 1: {name_ar}\n')

    if not passport_details.get('name_ar', ''):
        name_keywords = passport_details.get('full_name', '').split(' ')
        results = find_names_with_context(passport_text, name_keywords)
        if results:
            passport_details['name_ar'] = results[0][1]
            # print(f'\nARABIC NAME 2: {results[0][1]}\n')
        else:
            name_keywords = ['Full', 'Name']
            results = find_names_with_context(passport_text, name_keywords)
            if results:
                passport_details['name_ar'] = results[0][1]
                # print(f'\nARABIC NAME 3: {results[0][1]}\n')
            else:
                name_keywords = ['الاسم']
                results = find_names_with_context(passport_text, name_keywords)
                if results:
                    passport_details['name_ar'] = results[0][1]
                    # print(f'\nARABIC NAME 4: {results[0][1]}\n')

    ## HANDLE MRZ1 IF NOT COMPLETE
    if len(mrz1) < 40:
        mrz1_pattern = r'PC[A-Z]{3}[A-Z0-9<]{5,44}'
        match = re.search(mrz1_pattern, passport_text.replace(" ", ""))
        if match:
            mrz1 = match.group(0)

    if not mrz1:
        mrz1 = ''

    if mrz1 and len(mrz1) < 44:
        mrz1 = mrz1 = f"{mrz1}{'<' * (44 - len(mrz1))}"

    ## HANDLE MRZ2 IF NOT COMPLETE
    if not mrz2:
        try:
            mrz2 = passport_details.get('passport_number_mrz', '') + passport_details.get('nationality', '') + convert_to_mrz_date(passport_details.get('dob_mrz', '')) + passport_details.get('gender', '') + convert_to_mrz_date(passport_details.get('expiry_date_mrz', ''))
        except:
            mrz2 = ''
    
    if len(mrz2) >= 28 and len(mrz2) < 40:
        mrz2 = mrz2 = f"{mrz2}{'<' * (44 - len(mrz2))}"

    passport_details['mrz'] = mrz1 + mrz2
    passport_details['mrz1'] = mrz1
    passport_details['mrz2'] = mrz2

    ## EXTRACT ENGLISH NAME FROM PASSPORT HERE

    # print(f"PASSPORT DETAILS HERE: {passport_details}")


    try:
        pattern_1 = re.compile(r'\b(SDN|THE|SUDAN|PC|OF|REPUBLIC|SON|TOKAR|AP|CT|PUR|\w)\b', re.IGNORECASE)
        pattern = re.compile(r'^[A-Z\s]{3,}[A-Z\s]{3,}[A-Z\s]{3,}$', re.MULTILINE)
        matches = pattern.findall(pattern_1.sub('', passport_text))
        
        if matches:
            #print(f'MATCHES: {matches}')
            # filtered_matches = [
            #     match for match in matches 
            #     if ('REPUBLIC OF THE SUDAN' not in match.upper() and 'SUDAN' not in match.upper() and 'THE REPUBLIC' not in match.upper() and 'THE' not in match.upper() and 'PASSPORTS' not in match.upper())
            #     and (len(match.replace('\n', ' ').strip().split(' ')) >= 3)
            #     ]
            excluded_keywords = {'republic of the sudan', 'sudan','the republic', 'passports', 'republic of'}
            filtered_matches = [
                match for match in matches 
                if not any(keyword.upper() in match.upper() for keyword in excluded_keywords) 
                and len(match.replace('\n', ' ').strip().split()) >= 3
            ]

            if filtered_matches:
                def get_long_string(lst):
                    if len(lst) > 1:
                        return max(lst, key=len)
                    else:
                        return lst[0]
                    return None

                result = get_long_string(filtered_matches)
                full_name_generic = result.strip().replace('\n', ' ')
                #full_name_generic = filtered_matches[0].strip().replace('\n', ' ')
            else:
                full_name_generic = ''

            passport_details['full_name_generic'] = full_name_generic
        else:
            passport_details['full_name_generic'] = passport_details.get('full_name', '')
    except:
        passport_details['full_name_generic'] = passport_details.get('full_name', '')

    if passport_details.get('full_name_generic', ''):
        passport_details['name'] = passport_details['full_name_generic']
        name_split = passport_details['full_name_generic'].split(' ')
        passport_details['first_name'] = name_split[0]
        passport_details['last_name'] = name_split[-1]
        passport_details['middle_name'] = ' '.join(name_split[1:-1])
    else:
        if passport_details.get('full_name', ''):
            name_split = passport_details['full_name'].split(' ')
            passport_details['first_name'] = name_split[0]
            passport_details['last_name'] = name_split[-1]
            passport_details['middle_name'] = ' '.join(name_split[1:-1])
        else:
            passport_details['first_name'] = ''
            passport_details['last_name'] = ''
            passport_details['middle_name'] = ''

    passport_details['issuing_country'] = 'SDN'

    if "gender" in passport_details:
        gender = passport_details["gender"].strip().upper()
        if gender == "F":
            passport_details["gender"] = "FEMALE"
        elif gender == "M":
            passport_details["gender"] = "MALE"

    if 'gender' in passport_details:
        passport_details["gender"] = passport_details["gender"].strip().upper()

    passport_details_genai = extract_passport_details_genai(passport_text)

    if passport_details_genai and passport_details_genai.get('name_ar', ''):
        passport_details['name_ar'] = passport_details_genai.get('name_ar', '')

    if passport_details_genai and passport_details_genai.get('name_en', ''):
        passport_details['name_en'] = passport_details_genai.get('name_en', '')
        passport_details['full_name_generic'] = passport_details_genai.get('name_en', '')
        passport_details['name'] = passport_details_genai.get('name_en', '')

    if passport_details_genai and passport_details_genai.get('place_of_birth', ''):
        passport_details['place_of_birth'] = passport_details_genai.get('place_of_birth', '')

    if passport_details_genai and passport_details_genai.get('place_of_issue', ''):
        passport_details['place_of_issue'] = passport_details_genai.get('place_of_issue', '')

    full_name_generic_2 = passport_details.get('full_name_generic','')
    try:
        name_list = full_name_generic_2.split(' ')
        passport_details['first_name'] = name_list[0]
        passport_details['last_name'] = name_list[-1]
        passport_details['middle_name'] = ' '.join(name_list[1:-1])

    except Exception as e:
        if passport_details_genai and passport_details_genai.get('first_name', ''):
            passport_details['first_name'] = passport_details_genai.get('first_name', '')

        if passport_details_genai and passport_details_genai.get('middle_name', ''):
            passport_details['middle_name'] = passport_details_genai.get('middle_name', '')

        if passport_details_genai and passport_details_genai.get('last_name', ''):
            passport_details['last_name'] = passport_details_genai.get('last_name', '')
    
    full_name_generic_ar = passport_details.get('name_ar', '')
    try:
        name_parts = full_name_generic_ar.split(' ')
        
        # Handle compound names
        compound_prefixes = ['عبد', 'عبدال', 'فضل', 'بمسك']
        compound_suffixes = ['الدين', 'الله', 'الرحمن', 'الجنه']
        
        # Process first name
        if len(name_parts) >= 2:
            # Check for specific compound first names
            if name_parts[0] == 'عبد' or (name_parts[0] == 'فضل' and name_parts[1] == 'الله'):
                passport_details['first_name_ar'] = name_parts[0] + ' ' + name_parts[1]
                first_name_end_idx = 2
            # Handle the specific case of "بمسك الجنه"
            elif name_parts[0] == 'بمسك' and len(name_parts) >= 2 and name_parts[1] == 'الجنه':
                passport_details['first_name_ar'] = name_parts[0] + ' ' + name_parts[1]
                first_name_end_idx = 2
            else:
                # Regular first name
                passport_details['first_name_ar'] = name_parts[0]
                first_name_end_idx = 1
        else:
            passport_details['first_name_ar'] = name_parts[0] if name_parts else ''
            first_name_end_idx = 1
        
        # Process last name - check if last parts form a compound name
        if len(name_parts) >= 2:
            # Check for repeating patterns at the end (like "محمد خير")
            if len(name_parts) >= 4 and name_parts[-2] == name_parts[-4] and name_parts[-1] == name_parts[-3]:
                # We have a repeating two-word pattern at the end
                passport_details['last_name_ar'] = name_parts[-2] + ' ' + name_parts[-1]
                last_name_start_idx = len(name_parts) - 2
            # Check for compound last names
            elif len(name_parts) >= 3:
                # Check for عبد + something
                if name_parts[-2] == 'عبد':
                    passport_details['last_name_ar'] = 'عبد ' + name_parts[-1]
                    last_name_start_idx = len(name_parts) - 2
                # Check for something + الدين/الله/etc.
                elif name_parts[-1] in compound_suffixes:
                    passport_details['last_name_ar'] = name_parts[-2] + ' ' + name_parts[-1]
                    last_name_start_idx = len(name_parts) - 2
                else:
                    passport_details['last_name_ar'] = name_parts[-1]
                    last_name_start_idx = len(name_parts) - 1
            else:
                passport_details['last_name_ar'] = name_parts[-1]
                last_name_start_idx = len(name_parts) - 1
        else:
            passport_details['last_name_ar'] = ''
            last_name_start_idx = len(name_parts)
        
        # Middle name is everything between first and last name
        if first_name_end_idx < last_name_start_idx:
            passport_details['middle_name_ar'] = ' '.join(name_parts[first_name_end_idx:last_name_start_idx])
        else:
            passport_details['middle_name_ar'] = ''
    except Exception as e:
        if passport_details_genai and passport_details_genai.get('first_name_ar', ''):
            passport_details['first_name_ar'] = passport_details_genai.get('first_name_ar', '')

        if passport_details_genai and passport_details_genai.get('last_name_ar', ''):
            passport_details['last_name_ar'] = passport_details_genai.get('last_name_ar', '')

        if passport_details_genai and passport_details_genai.get('middle_name_ar', ''):
            passport_details['middle_name_ar'] = passport_details_genai.get('middle_name_ar', '')

    print(f"passport details: {passport_details}")
    
    if passport_details_genai and passport_details_genai.get('issue_date', ''):
        passport_details['issue_date'] = passport_details_genai.get('issue_date', '')

    if passport_details_genai and passport_details_genai.get('nationality', ''):
        if passport_details.get('nationality', '') != passport_details_genai.get('nationality', ''):
            passport_details['nationality'] = passport_details_genai.get('nationality', '')
    
    if passport_details_genai and passport_details_genai.get('mrz1', ''):
        passport_details['mrz1'] = passport_details_genai.get('mrz1', '')

    if passport_details_genai and passport_details_genai.get('mrz2', ''):
        passport_details['mrz2'] = passport_details_genai.get('mrz2', '')

    if passport_details_genai and passport_details_genai.get('mrz', ''):
        passport_details['mrz'] = passport_details_genai.get('mrz', '')
    
    if passport_details_genai and passport_details_genai.get('id_number', ''):
        passport_details['id_number'] = passport_details_genai.get('id_number', '')

    if passport_details_genai and passport_details_genai.get('passport_number_mrz', ''):
        if passport_details.get('passport_number_mrz', '') != passport_details_genai.get('id_number', passport_details_genai.get('passport_number', '')):
            passport_details['passport_number_mrz'] = passport_details_genai.get('id_number', passport_details_genai.get('passport_number', ''))
    
    if passport_details_genai and passport_details_genai.get('gender', ''):
        if passport_details.get('gender', '') != passport_details_genai.get('gender', ''):
            passport_details['gender'] = passport_details_genai.get('gender', '')
    # try:
    #     full_name_generic = ''
    #     passport_details['full_name_generic'] = full_name_generic
    # except:
    #     passport_details['full_name_generic'] = ''

    # print(f"\nPassport Details: {passport_details}\n")

    return passport_details

def make_api_request_with_retries(prompt: str, max_retries: int = 3, delay_seconds: float = 2):
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

def extract_passport_details_genai(passport_data):
    """
    Function to extract passport details using OpenAI API
    """
    try:
        prompt = f"""From the attached text, please extract the data in a structured format. The response should be a dictionary containing:
        - name_ar (Arabic name if available)
        - name_en (English name)
        - place_of_birth (English place of birth)
        - place_of_issue (English place of issue)
        - gender (FEMALE or MALE)
        - mrz1 (first line of MRZ)
        - mrz2 (second line of MRZ)
        - passport_number (should be in format: letter followed by 8 digits)
        - dob (in format dd/mm/yyyy)
        - issue_date (in format dd/mm/yyyy)
        - expiry_date (in format dd/mm/yyyy)
        - nationality (ISO 3166-1 alpha-3 country code)
        - first_name (from English name)
        - middle_name (from English name)
        - last_name (from English name)
        - first_name_ar (Arabic first name)
        - last_name_ar (Arabic last name)
        - middle_name_ar (Arabic middle name)

        Make sure to extract the correct names from both Arabic and English text. 
        Important NOTE: If the number of words in name_en and name_ar are not equal, translate the English name (name_en) into Arabic and update name_ar with the translated text.
        
        The MRZ lines should be complete.
        The response should only contain a dictionary with these fields.

        Here's the text: {passport_data}"""

        back_data = make_api_request_with_retries(prompt)

        if back_data:
            if back_data.get('passport_number', ''):
                back_data['id_number'] = back_data.pop('passport_number', '')

            if back_data.get('mrz1', '') and back_data.get('mrz2', ''):
                back_data['mrz'] = back_data.get('mrz1', '') + back_data.get('mrz2', '')
            
            back_data['issuing_country'] = 'SDN'

            if "gender" in back_data:
                gender = back_data["gender"].strip().upper()
                if gender == "F":
                    back_data["gender"] = "FEMALE"
                elif gender == "M":
                    back_data["gender"] = "MALE"
        
            if 'gender' in back_data:
                back_data["gender"] = back_data["gender"].strip().upper()

    except Exception as e:
        print(f"Error in processing the extracted data: {e}")
        back_data = {
            'name_ar': '',
            'name_en': '',
            'first_name': '',
            'middle_name': '',
            'last_name': '',
            'first_name_ar': '',
            'last_name_ar': '',
            'middle_name_ar': '',
            'dob': '',
            'issue_date': '',
            'expiry_date': '',
            'place_of_birth': '',
            'place_of_issue': '',
            'nationality': '',
            'mrz1': '',
            'mrz2': '',
            'mrz': ''
        }
    
    return back_data




