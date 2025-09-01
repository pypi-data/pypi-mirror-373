import pandas as pd
import re
from datetime import datetime
from hijri_converter import convert
# from googletrans import Translator
import pycountry
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "streamlit-connection-b1a38b694505 (1).json"

def get_country_code(name_in_foreign_language):
    # translator = Translator()
    # translated_country_name = translator.translate(name_in_foreign_language, src='auto', dest='en').text
    
    # Manual mapping for known challenges or discrepancies in translation
    manual_mapping = {
        'ميانمار': 'MMR',  # Myanmar
        'البحرين': 'BHR',  # Bahrain
        'اليمن الجنوبي': 'YEM',  # Yemen
        'فلسطين': 'PSE',  # Palestine
        'الفلبين': 'PHL',  # Philippines
        'أفغانستان': 'AFG',  # Afghanistan
        'سوريا': 'SYR',  # Syria
        'سري لنكا': 'LKA'  # Sri Lanka
    }
    
    if name_in_foreign_language in manual_mapping:
        return manual_mapping[name_in_foreign_language]
    
    # try:
    #     country = pycountry.countries.get(name=translated_country_name)
    #     return country.alpha_3
    # except AttributeError:
    #     return "Country Not Found"
    
pattern = r'(\d{4}/\d{1,2}/\d{1,2}|[۰-۹]{4}/[۰-۹]{1,2}/[۰-۹]{1,2})'
def eastern_arabic_to_english(eastern_numeral):
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

    # If the character is an Eastern Arabic numeral, convert it to English; otherwise, keep it unchanged.
    english_numeral = ''.join([arabic_to_english_map[char] if char in arabic_to_english_map else char for char in eastern_numeral])
    
    return english_numeral

def distinguish_dates(date_list):
    today = datetime.now().date()
    
    # Calculate the difference between each date and today's date
    differences = [(abs((today - datetime.strptime(date, '%Y/%m/%d').date()).days), date) for date in date_list]
    
    # Sort by difference
    differences.sort(key=lambda x: x[0])
    
    # The date with the smallest difference is considered Gregorian, and the one with the largest difference is considered Hijri
    gregorian_date = differences[0][1]
    hijri_date = differences[-1][1]

    return hijri_date, gregorian_date

def hijri_to_gregorian(hijri_date):
    try:
        # Split the hijri date
        year, month, day = map(int, hijri_date.split('/'))

        # Convert the hijri date to Gregorian
        gregorian_date = convert.Hijri(year, month, day).to_gregorian()
    
    # Format the result as a string
        return f"{gregorian_date.year}/{gregorian_date.month:02}/{gregorian_date.day:02}"
    except:
        return hijri_date
    
def extract_dates(input_list):
    # Regex pattern to match YYYY/MM/DD, YYYY/MM/DD in Arabic numerals, 
    # and some other variations found in the list
    pattern = r"(\d{4}/\d{2}/\d{2}|[۰۱۲۳۴۵۶۷۸۹]{4}/[۰۱۲۳۴۵۶۷۸۹]{2}/[۰۱۲۳۴۵۶۷۸۹]{2})"
    
    extracted_dates = []
    for item in input_list:
        match = re.search(pattern, item)
        if match:
            extracted_dates.append(match.group(0))
        else:
            extracted_dates.append('')
    return extracted_dates


def detect_script(word):
    arabic_chars = range(0x0600, 0x06FF)  # Arabic Unicode Block
    english_chars = range(0x0041, 0x007A)  # English uppercase Unicode Block
    english_chars_lower = range(0x0061, 0x007A)  # English lowercase Unicode Block
    
    has_arabic = any(ord(char) in arabic_chars for char in word)
    has_english = any(ord(char) in english_chars or ord(char) in english_chars_lower for char in word)
    
    if has_arabic and has_english:
        return "Mixed"
    elif has_arabic:
        return "Arabic"
    elif has_english:
        return "English"
    else:
        return "Other"
    
def extract_english_strings(data):
    english_strings = []
    for string in data:
        if not re.search("[\u0600-\u06FF\d]", string):  # Filters out strings containing Arabic letters or digits
            english_strings.append(string)
    return english_strings

def extract_arabic_strings(data):
    arabic_strings = []
    for string in data:
        if re.search(r"[\u0600-\u06FF\d]", string):  # Filters out strings containing Arabic letters or digits
            arabic_strings.append(string)
    return arabic_strings

def clean_special_chars(data):
    cleaned_data = []
    for string in data:
        cleaned_string = re.sub(r'[^A-Za-z\s]', '', string)  # Retains only alphabets and spaces
        cleaned_data.append(cleaned_string.strip())  # .strip() removes any leading or trailing spaces
    return cleaned_data
    
def extract_id_details(result):
    # result = detect_text(uploaded_id)
    df = pd.DataFrame({'res':[result]})
    pattern = r'(\d{4}/\d{1,2}/\d{1,2}|[۰-۹]{4}/[۰-۹]{1,2}/[۰-۹]{1,2})'
    i = 0
    df['Extracted_data']=''
    try:
        nationality=[ele for ele in [ele for ele in df['res'].iloc[i] if 'الجنسية' in ele ][0].split('الجنسية') if ele!=''][0].strip()

        nationality=get_country_code(nationality)
    except:
        nationality=''
    try:
        ## employer
        employer_ar=[ele for ele in [ele for ele in df['res'].iloc[i] if 'صاحب العمل' in ele ]][0]
        employer=[ele for ele in employer_ar.split('صاحب العمل') if ele!=''][0].strip()

    except:
        employer=''
    try:
        ### issuing place
        issuing_place_ar=[ele for ele in df['res'].iloc[i] if 'مكان الإصدار' in ele][0]
        issuing_place=issuing_place_ar.split('مكان الإصدار')[-1].strip()
    except:
        issuing_place=''
    try:
        comon_pattern=[ele for ele in [ele for ele in df['res'].iloc[i] if (('الإصدار' in ele ) and('مكان' not in ele))][0].split('الإصدار') if ele!=''][0].strip()
        matches = re.findall(pattern, comon_pattern)

        matches=[eastern_arabic_to_english(ele) for ele in matches]

        issuing_date, dob=matches[0],matches[1]

        #issuing_date = hijri_to_gregorian(issuing_date)
        
    except:
        
        try: 
            dob=[ele for ele in [ele for ele in df['res'].iloc[i] if 'الميلاد' in ele ][0].split('الميلاد') if ele!=''][0].strip()
            issuing_date= [ele for ele in [ele for ele in df['res'].iloc[i] if( 'الإصدار' in ele) and ('مكان' not in ele ) ][0].split('الإصدار') if ele!=''][0].strip()
            #issuing_date=hijri_to_gregorian(issuing_date)
        except:
            try:
                dob=[ele for ele in [ele for ele in df['res'].iloc[i] if 'الميلاد' in ele ][0].split('الميلاد') if ele!=''][-1].strip()
                issuing_date=[ele for ele in [ele for ele in df['res'].iloc[i] if 'الميلاد' in ele ][0].split('الميلاد') if ele!=''][0].strip('الانتهاء').strip()
                #issuing_date=hijri_to_gregorian(issuing_date)
            except:
                issuing_date,dob='',''
    
    try:

        #issuing_date_ar,dob_ar=re.findall(pattern, comon_pattern)

        ### Id Number 
        id_number=[item for item in df['res'].iloc[i] if re.fullmatch(r'\d{10}', item)][0]
        id_number=eastern_arabic_to_english(id_number)
    
    except:
        
        try:
            id_number = [ele for ele in eastern_arabic_to_english([ele for ele in [ele for ele in df['res'].iloc[i] if 'الرقم' in ele ][0].split('الرقم') if ele!=''][0].strip()).split(' ') if len(ele)==10][0]
            id_number=eastern_arabic_to_english(id_number)
        except:
            id_number=''
    
    try:
        profession_Ar=[ele for ele in [ele for ele in df['res'].iloc[i] if 'المهنة' in ele ]][0]

        profession=[ele for ele in profession_Ar.split('المهنة') if ele!=''][-1]

    except:
        profession=''
    try:
        Name_Index=[extract_arabic_strings(df['res'].iloc[i]).index(ele) for ele in extract_arabic_strings(df['res'].iloc[i]) if 'وزارة' in ele][0]
        Name_1=extract_arabic_strings(df['res'].iloc[i])[Name_Index+1]
        Name_length=len(Name_1.split(' '))
        Name_en=max([ele for ele in clean_special_chars(extract_english_strings(df['res'].iloc[i])) if ele not in ['KINGDOM OF SAUDI ARABIA','MINISTRY OF INTERIOR']], key=lambda x: x.count(' '))
        Name_ar=[ele for ele in [Name_1,Name_en] if ele!=Name_en][0]  
        
    except:
        
        Name_en,Name_ar='',''

    df['Extracted_data'].iloc[i]=[nationality,employer,issuing_date, dob,id_number,profession,Name_en,Name_ar]
    
    cols = ['nationality', 'employer', 'issuing_date', 'dob', 'id_number', 'profession', 'Name_en', 'Name_ar']

    for index, col_name in enumerate(cols):
        df[col_name] = df['Extracted_data'].apply(lambda x: x[index])

    df['dob']=extract_dates(df['dob'].tolist())

    df['dob']=df['dob'].apply(lambda x: eastern_arabic_to_english(x))

    df['issuing_date']=df['issuing_date'].apply(lambda x: eastern_arabic_to_english(x))

    df['issuing_date']=df['issuing_date'].apply(lambda x: hijri_to_gregorian(x))

    dob = df['dob'].iloc[0]

    if dob:
        parsed_date = datetime.strptime(dob, "%Y/%m/%d")
        dob = parsed_date.strftime("%d/%m/%Y")

    # df['gender']= ''
    # df['expiry_data']= ' '

    # print(df)
    # TODO: gender, expiry_data
    return {'id_number': df['id_number'].iloc[0], 'nationality': df['nationality'].iloc[0], 'gender': '', 'dob': dob, 'expiry_date': '', 'name': df['Name_en'].iloc[0], 'occupation': df['profession'].iloc[0], 'employer': df['employer'].iloc[0]}

