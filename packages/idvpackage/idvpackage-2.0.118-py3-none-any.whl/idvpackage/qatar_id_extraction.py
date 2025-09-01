from PIL import Image
from deep_translator import GoogleTranslator
import pycountry
from rapidfuzz import process, fuzz
from idvpackage.common import extract_text_from_image_data
from io import BytesIO
import re
import time
import datetime
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field, validator
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from typing import Optional, Literal
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from datetime import datetime, timedelta
from langchain.schema.agent import AgentFinish
import openai
import json


class QatarIDInfo(BaseModel):
    """
    Extract info from ocr-extracted text from a Qatar ID
    """
    name: str = Field(..., description="Full name in English")
    name_ar: str = Field(..., description="Full name in Arabic")
    nationality: str = Field(...,
                             description="Nationality in ISO 3166-1 alpha-3 format (e.g., 'PAK' 'QAT', 'SYR', 'PHL')",
                             example="SYR")
    id_number: str = Field(..., description="National ID number")
    dob: str = Field(..., description="Date of birth")
    expiry_date: str = Field(..., description="Card expiry date")
    occupation: str = Field(..., description="Occupation in Arabic")
    occupation_en: str = Field(..., description="Occupation, translated from Arabic to English")


@tool(args_schema=QatarIDInfo)
def verify_qatar_id_info(name='', name_ar='', nationality='', id_number='', dob='', expiry_date='', occupation='',
                         occupation_en=''):
    if occupation_en == '':
        occupation_en = GoogleTranslator('ar', 'en').translate(occupation)
    return {**locals()}


def route(result):
    if isinstance(result, AgentFinish):
        return result.return_values['output']
    else:
        tools = {
            "verify_qatar_id_info": verify_qatar_id_info
        }
        return tools[result.tool].run(result.tool_input)


def qatar_id_info_chain(ocr_text, openai_key):
    gpt_model = 'gpt-4o'

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Extract the relevant information, if not explicitly provided do not guess, leave empty string. Extract partial info. Translate where explicity stated."
         ),
        ("user", "{ocr_text}")
    ])

    model = ChatOpenAI(model=gpt_model, temperature=0,
                       openai_api_key=openai_key)
    functions = [convert_pydantic_to_openai_function(QatarIDInfo)]
    verification_model = model.bind(functions=functions)
    verification_chain = prompt | verification_model | JsonOutputFunctionsParser()

    result = verification_chain.invoke({"ocr_text": ocr_text})
    return result


def extract_name_line(ocr_text):
    """Try to extract the English name line explicitly from OCR."""
    match = re.search(r'(?i)\bname\b\s*[:\-]?\s*([A-Z][A-Z\s]+)', ocr_text)
    return match.group(1).strip() if match else None


# ISO3166 nationality mapping
ISO3166_nationality_mapping = {
    "004": "AFG", "008": "ALB", "012": "DZA", "016": "ASM", "020": "AND", "024": "AGO", "660": "AIA",
    "010": "ATA", "028": "ATG", "032": "ARG", "051": "ARM", "533": "ABW", "036": "AUS", "040": "AUT",
    "031": "AZE", "044": "BHS", "048": "BHR", "050": "BGD", "052": "BRB", "112": "BLR", "056": "BEL",
    "084": "BLZ", "204": "BEN", "060": "BMU", "064": "BTN", "068": "BOL", "535": "BES", "070": "BIH",
    "072": "BWA", "074": "BVT", "076": "BRA", "086": "IOT", "096": "BRN", "100": "BGR", "854": "BFA",
    "108": "BDI", "132": "CPV", "116": "KHM", "120": "CMR", "124": "CAN", "136": "CYM", "140": "CAF",
    "148": "TCD", "152": "CHL", "156": "CHN", "162": "CXR", "166": "CCK", "170": "COL", "174": "COM",
    "180": "COD", "178": "COG", "184": "COK", "188": "CRI", "191": "HRV", "192": "CUB", "531": "CUW",
    "196": "CYP", "203": "CZE", "384": "CIV", "208": "DNK", "262": "DJI", "212": "DMA", "214": "DOM",
    "218": "ECU", "818": "EGY", "222": "SLV", "226": "GNQ", "232": "ERI", "080": "ERI", "233": "EST",
    "748": "SWZ", "231": "ETH", "238": "FLK", "234": "FRO", "242": "FJI", "246": "FIN", "250": "FRA",
    "254": "GUF", "258": "PYF", "260": "ATF", "266": "GAB", "270": "GMB", "268": "GEO", "276": "DEU",
    "288": "GHA", "292": "GIB", "300": "GRC", "304": "GRL", "308": "GRD", "312": "GLP", "316": "GUM",
    "320": "GTM", "831": "GGY", "324": "GIN", "624": "GNB", "328": "GUY", "332": "HTI", "334": "HMD",
    "336": "VAT", "340": "HND", "344": "HKG", "348": "HUN", "352": "ISL", "356": "IND", "360": "IDN",
    "364": "IRN", "368": "IRQ", "372": "IRL", "833": "IMN", "376": "ISR", "380": "ITA", "388": "JAM",
    "392": "JPN", "832": "JEY", "400": "JOR", "398": "KAZ", "404": "KEN", "296": "KIR", "408": "PRK",
    "410": "KOR", "414": "KWT", "417": "KGZ", "418": "LAO", "428": "LVA", "422": "LBN", "426": "LSO",
    "430": "LBR", "434": "LBY", "438": "LIE", "440": "LTU", "442": "LUX", "446": "MAC", "450": "MDG",
    "454": "MWI", "458": "MYS", "462": "MDV", "466": "MLI", "470": "MLT", "584": "MHL", "474": "MTQ",
    "478": "MRT", "480": "MUS", "175": "MYT", "484": "MEX", "583": "FSM", "498": "MDA", "492": "MCO",
    "496": "MNG", "499": "MNE", "500": "MSR", "504": "MAR", "508": "MOZ", "104": "MMR", "516": "NAM",
    "520": "NRU", "524": "NPL", "528": "NLD", "540": "NCL", "554": "NZL", "558": "NIC", "562": "NER",
    "566": "NGA", "570": "NIU", "574": "NFK", "580": "MNP", "578": "NOR", "512": "OMN", "586": "PAK",
    "585": "PLW", "275": "PSE", "591": "PAN", "598": "PNG", "600": "PRY", "604": "PER", "608": "PHL",
    "612": "PCN", "616": "POL", "620": "PRT", "630": "PRI", "634": "QAT", "807": "MKD", "642": "ROU",
    "643": "RUS", "646": "RWA", "638": "REU", "652": "BLM", "654": "SHN", "659": "KNA", "662": "LCA",
    "663": "MAF", "666": "SPM", "670": "VCT", "882": "WSM", "674": "SMR", "678": "STP", "682": "SAU",
    "686": "SEN", "688": "SRB", "690": "SYC", "694": "SLE", "702": "SGP", "534": "SXM", "703": "SVK",
    "705": "SVN", "090": "SLB", "706": "SOM", "710": "ZAF", "239": "SGS", "728": "SSD", "724": "ESP",
    "144": "LKA", "736": "SDN", "740": "SUR", "744": "SJM", "752": "SWE", "756": "CHE", "760": "SYR",
    "158": "TWN", "762": "TJK", "834": "TZA", "764": "THA", "626": "TLS", "768": "TGO", "772": "TKL",
    "776": "TON", "780": "TTO", "788": "TUN", "792": "TUR", "795": "TKM", "796": "TCA", "798": "TUV",
    "800": "UGA", "804": "UKR", "784": "ARE", "826": "GBR", "581": "UMI", "840": "USA", "858": "URY",
    "860": "UZB", "548": "VUT", "862": "VEN", "704": "VNM", "092": "VGB", "850": "VIR", "876": "WLF",
    "732": "ESH", "887": "YEM", "894": "ZMB", "716": "ZWE", "248": "ALA", "999": "PSE", "544": "BIH",
    "230": "ETH", "886": "YEM", "901": "TWN"
}


def crop_second_part(img):
    width, height = img.size
    half_width = width // 2
    second_part = img.crop((half_width, 0, width, height))
    return second_part


def crop_third_part(img):
    width, height = img.size
    part_height = height // 6
    third_part = img.crop((0, 3.7 * part_height, width, height))
    return third_part


def detect_id_card(client, image_data, id_text, part=None):
    if id_text:
        vertices = id_text[0].bounding_poly.vertices
        left = vertices[0].x
        top = vertices[0].y
        right = vertices[2].x
        bottom = vertices[2].y

        padding = 40
        left -= padding
        top -= padding
        right += padding
        bottom += padding

        # img = image_data
        # with Image.open(io.BytesIO(image_data)) as img:
        #     id_card = img.crop((max(0, left), max(0, top), right, bottom))

        pil_image = Image.open(BytesIO(image_data))
        compressed_image = BytesIO()
        pil_image.save(compressed_image, format="JPEG", quality=50, optimize=True)
        compressed_image_data = compressed_image.getvalue()
        compressed_pil_image = Image.open(BytesIO(compressed_image_data))
        id_card = compressed_pil_image.crop((max(0, left), max(0, top), right, bottom))

        width, height = id_card.size
        if width < height:
            id_card = id_card.rotate(90, expand=True)

        if part == 'second':
            part_img = crop_second_part(id_card)
        if part == 'third':
            part_img = crop_third_part(id_card)

        # 2nd call to vision AI
        part_text = extract_text_from_image_data(client, part_img)

        return id_card, part_img, part_text
    else:
        print('No text found in the image.')


def is_arabic(word):
    return re.search(r'[\u0600-\u06FF]', word) is not None


def extract_name_ar(text):
    # patterns = [
    #     r"(?:الاسم|الإسم):\s*([^\n]+)",
    #     r"الاسم\s+([^\n]+)"
    # ]

    patterns = [
        r"(?:الإسم|الاسم):\s*([^\n]+)",
        r"(?:الإسم|الاسم)\s+([^\n]+)",
    ]

    for pattern in patterns:
        regex = re.compile(pattern, re.MULTILINE)
        match = regex.search(text)
        if match:
            return match.group(1).strip()

    return None


def extract_name_fields_from_cropped_part(text):
    pattern = r"Name:\s*([A-Z\s-]+)"
    name_dict = {}
    match = re.search(pattern, text)

    if match:
        extracted_name = match.group(1).strip()
        extracted_name = extracted_name.replace("\n", " ")
        unnecessary_words = ['OF', 'THE']
        extracted_name = [word for word in extracted_name.split() if word.upper() not in unnecessary_words]
        if len(extracted_name[-1]) <= 2:
            extracted_name = extracted_name[:-1]

        extracted_name = ' '.join(extracted_name)

        name_dict["name"] = extracted_name.strip()
        name_parts = extracted_name.split()

        first_name = name_parts[0].upper()
        last_name = name_parts[-1].upper()

        name_dict["first_name"] = first_name
        name_dict["last_name"] = last_name
    return name_dict


def identify_front(text):
    front_id_keywords = ["State of Qatar"]
    pattern = '|'.join(map(re.escape, front_id_keywords))

    try:
        if re.search(pattern, text, re.IGNORECASE):
            return True
        else:
            return False
    except:
        return 'error'


def sort_dates_by_datetime(dates):
    return sorted(dates, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))


def extract_and_check_country(words):
    for word in words:
        try:
            country = pycountry.countries.lookup(word)
            if country:
                return country.name.upper()
        except LookupError:
            pass

    return ''


def extract_and_check_country_normalized(words):
    normalized_words = [re.sub(r'\s+|-', '', word).lower() for word in words]

    for country in pycountry.countries:
        common_name_normalized = re.sub(r'\s+|-', '', country.name).lower()
        official_name_normalized = re.sub(r'\s+|-', '', getattr(country, 'official_name', '')).lower()

        if common_name_normalized in normalized_words or official_name_normalized in normalized_words:
            return country.name.upper()

    return ''


def extract_name_after_nationality(word_list, nationality):
    nationality_index = word_list.index(nationality) if nationality in word_list else -1

    if nationality_index != -1 and nationality_index < len(word_list) - 1:
        words_after_nationality = word_list[nationality_index + 1:]
        return words_after_nationality
    else:
        return []


def get_fuzzy_match_score(line, patterns, threshold=80):
    result = process.extractOne(line, patterns, scorer=fuzz.WRatio)
    if result and result[1] > threshold:
        return result[1]
    return None


def extract_occupation_in_empty_case(text):
    pattern = re.compile(r'المهنة\s*[:]*\s*(\S*)', re.IGNORECASE)
    lines = text.split('\n')

    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            if match.group(1):
                return match.group(1).strip()
            if i + 1 < len(lines):
                return lines[i + 1].strip()

    return ''


def extract_occupation_in_empty_case_v2(text):
    pattern = re.compile(r'occupation\s*[:]*\s*(\S*)', re.IGNORECASE)
    lines = text.split('\n')

    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            if match.group(1):
                return match.group(1).strip()
            if i + 1 < len(lines):
                return lines[i + 1].strip()

    return ''


def genAI(ar_front_data, model):
    query = f"Please extract the nationality from the following text and provide the corresponding ISO 3166-1 alpha-3 country code for that nationality: {ar_front_data}"
    response = model.generate_content(query)
    nationality_ai = re.findall(r'\*\*(.*?)\*\*', response.text)[1]
    return nationality_ai


def genAI_for_occupation(dct, model):
    query = f"""
    You are provided with the following front_data: {dct}. 

    Check if  'occupation_en' information is valid and correct. Please review this broadly without focusing on the specifics.
    for example if (doctor teacher employee and etc it is occupation as well)
    If 'occupation_en' match the expected values, respond with 'correct'. 
    If it is incorrect, respond with 'not_correct', if you are not able to determine then respond with 'undetermined'.
    as a response give me 'not_correct','undetermined' or 'correct' nothing else 
    """
    response = model.generate_content(query)
    value = response.candidates[0].content.parts[0].text.strip()

    return value


def genAI_for_occupation_correct(passport_details, model):
    query = f"""
    Please extract the occupation from the following text and provide it in this format:
    - English: **occupation**
    - Arabic: **occupation** return only these 2 nothing else.
    So you will get occupation in arabic and translate it into english and send it
      if no info about occupation then 'not_provided', for both English and Arabic: {passport_details}
    """
    response = model.generate_content(query)
    occupation_ai = re.findall(r'\*\*(.*?)\*\*', response.text)

    return occupation_ai


def genAI_for_expiry_date(ar_front_data, model):
    query = f"""
    Please extract the expiry date from the following text and provide it in this format(dd/mm/yyyy):
    - expiry_date, return only this 1 variable, nothing else.
      if no info about expiry_date found then return 'expiry_date': 'not_provided': {ar_front_data}
    """
    response = model.generate_content(query)
    expiry_ai = re.findall(r'\*\*(.*?)\*\*', response.text)[1]

    return expiry_ai


def make_api_request_with_retries(prompt: str, max_retries: int = 3, delay_seconds: float = 2):
    """
    Helper function to make API requests with retry logic using OpenAI
    """
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
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


def extract_numeric_fields_from_raw(ar_front_data, third_part_text, name_extracted, extract_names=False):
    front_data = GoogleTranslator(dest='en').translate(ar_front_data)
    id_number_pattern = r"\b\d{11}\b"

    words = re.findall(r'\b[A-Z]{4,}\b', ar_front_data)
    nationality = extract_and_check_country(words)

    nationality_iso = ''
    if not nationality:
        nationality = extract_and_check_country_normalized(words)

    if nationality:
        try:
            country = pycountry.countries.lookup(nationality)
            nationality_iso = country.alpha_3
        except:
            nationality_iso = ''

    print(f'------------Nationality from OCR: {nationality_iso}')
    # Extract nationality from ID number
    id_number_match = re.search(id_number_pattern, ar_front_data, re.IGNORECASE)
    if id_number_match:
        id_number = id_number_match.group(0)
        # Extract nationality code from ID number (digits 4-6)
        if len(id_number) >= 6:
            nationality_code = id_number[3:6]  # 0-based indexing, so 3:6 gives us digits 4-6
            nationality_from_id = ISO3166_nationality_mapping.get(nationality_code, '')
            print(f'------------Nationality from ID number code: {nationality_from_id}')

            # Use nationality from ID if OCR nationality is empty, invalid, or different
            if nationality_from_id:
                if not nationality_iso or len(nationality_iso) != 3:
                    nationality_iso = nationality_from_id
                elif nationality_iso != nationality_from_id:
                    nationality_iso = nationality_from_id
    else:
        try:
            id_number_match = re.search(id_number_pattern, ar_front_data, re.IGNORECASE)
            id_number = id_number_match.group(0)
        except:
            id_number = ''

    names_list = extract_name_after_nationality(words, nationality)
    name = ' '.join(names_list)
    if not name:
        name = name_extracted

    dates = sort_dates_by_datetime(re.findall(r'\d{2}/\d{2}/\d{4}', ar_front_data))
    combined_back_pattern = r'(Director General of the General Department|Directorate of Passports|Passport Number|Passport Expiry)'
    back_match = re.search(combined_back_pattern, ar_front_data, re.IGNORECASE)

    try:
        if back_match:
            if 'Passport' in ar_front_data:
                ar_front_data = ar_front_data.split("Name")[0]

            dates = sort_dates_by_datetime(re.findall(r'\d{2}/\d{2}/\d{4}', ar_front_data))

            if len(dates) > 2:
                dob = dates[0]
                expiry = dates[1]
            elif len(dates) <= 2:
                dob = dates[0]
                expiry = dates[-1]
        else:
            dob = dates[0]
            expiry = dates[-1]
    except:
        try:
            dob = dates[0]
            expiry = dates[-1]
        except:
            dob = ''
            expiry = ''

    if 'Passport' in ar_front_data:
        ar_front_data = ar_front_data.split("Name")[0]

    ar_front_data_filtered = [
        re.sub(r'\b[a-zA-Z0-9]+\b', '',
               line.replace(':', '').replace('/', '').replace('.', '').replace('المهنة', '').replace('تاريخ الميلاد',
                                                                                                     '').replace(
                   'دولة قطر', '').replace('الرقم الشخصي', '').replace('الصلاحية', '').replace('الجنسية', '').replace(
                   'رخصة إقامة', '').replace('الرقم', '').replace('اللى', '').replace('طو', '').replace('دولة',
                                                                                                        '').replace(
                   'الهند', '').replace('بطاقة', '').replace('إثبات', '').replace('شخصية', '').replace('ہے',
                                                                                                       '').replace('۔',
                                                                                                                   ''))
        for line in ar_front_data.split('\n')
    ]

    cleaned_lines = [line for line in ar_front_data_filtered if line.strip()]

    patterns_to_remove = [
        r"State Of Qatar", r"Residency Permit", r"ID\.No:", r"D\.O\.B\.:", r"D\.O\.B:",
        r"Expiry:", r"Nationality:", r"\d{9}", r"\d{2}/\d{2}/\d{4}", r"بنغلاديش", r"الهند",
        r"on", r"الرقم الشخصي:", r"تاريخ الميلاد:", r"الصلاحية:",
        r"الجنسية:", r"دولة قطر", r"رخصة إقامة", r"المهنة:", r"الاسم:", r"Name:"
    ]

    if nationality:
        patterns_to_remove.append(re.escape(nationality))

    if name:
        patterns_to_remove.append(re.escape(name))

    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns_to_remove]

    countries_list = ['أفغانستان', 'جزر أولاند', 'ألبانيا', 'یمنی', 'الجزائر', 'ساموا الأمريكية', 'مغربي', 'أندورا',
                      'أنغولا', 'أنغويلا', 'القارة القطبية الجنوبية', 'أنتيغوا وبربودا', 'الأرجنتين', 'أرمينيا',
                      'أروبا', 'أستراليا', 'النمسا', 'أذربيجان', 'باهاماس', 'البحرين', 'بنغلاديش', 'بربادوس',
                      'بيلاروسيا', 'بلجيكا', 'بليز', 'بنين', 'برمودا', 'بوتان', 'بوليفيا', 'البوسنة والهرسك',
                      'بوتسوانا', 'جزيرة بوفيه', 'البرازيل', 'إقليم المحيط الهندي البريطاني', 'جزر العذراء البريطانية',
                      'بروناي', 'بلغاريا', 'بوركينا فاسو', 'بوروندي', 'كابو فيردي', 'كمبوديا', 'الكاميرون', 'كندا',
                      'الجزر الكاريبية الهولندية', 'جزر كايمان', 'جمهورية أفريقيا الوسطى', 'تشاد', 'تشيلي', 'الصين',
                      'جزيرة الكريسماس', 'جزر كوكوس', 'كولومبيا', 'جزر القمر', 'جمهورية الكونغو', 'جزر كوك',
                      'كوستاريكا', 'كرواتيا', 'كوبا', 'كوراساو', 'قبرص', 'التشيك', 'الدنمارك', 'جيبوتي', 'دومينيكا',
                      'جمهورية الدومينيكان', 'جمهورية الكونغو الديمقراطية', 'الاكوادور', 'السلفادور',
                      'غينيا الاستوائية', 'إريتريا', 'إستونيا', 'إسواتيني', 'إثيوبيا', 'جزر فوكلاند', 'جزر فارو',
                      'فيجي', 'فنلندا', 'فرنسا', 'غويانا الفرنسية', 'بولينزيا الفرنسية', 'أراض فرنسية جنوبية',
                      'الجابون', 'غامبيا', '\u202bجورجيا', 'ألمانيا', 'غانا', 'جبل طارق', 'اليونان', 'جرينلاند',
                      'غرينادا', 'غوادلوب', 'غوام', 'غواتيمالا', 'غيرنزي', 'غينيا', 'غينيا بيساو', 'غيانا', 'هايتي',
                      'جزيرة هيرد وجزر ماكدونالد', 'هندوراس', 'هونج كونج', 'هنجاريا', 'آيسلندا', 'الهند', 'أندونيسيا',
                      'إيران', 'العراق', 'أيرلندا', 'جزيرة مان', 'إيطاليا', 'ساحل العاج', 'جامايكا', 'اليابان', 'جيرسي',
                      'الأردن', 'كازاخستان', 'كينيا', 'كيريباتي', 'كوسوفو', 'الكويت', 'قيرغيزستان', 'لاوس', 'لاتفيا',
                      'لبنان', 'ليسوتو', 'ليبيريا', 'ليبيا', 'ليختنشتاين', 'ليتوانيا', 'لوكسمبورغ', 'ماكاو', 'مدغشقر',
                      'مالاوي', 'ماليزيا', 'المالديف', 'مالي', 'مالطا', 'جزر مارشال', 'مارتينيك', 'موريتانيا',
                      'موريشيوس', 'مايوت', 'المكسيك', 'ولايات ميكرونيسيا المتحدة', 'مولدوفا', 'موناكو', 'منغوليا',
                      'مونتينيغرو', 'مونتسرات', 'المغرب', 'موزمبيق', 'ميانمار', 'ناميبيا', 'ناورو', 'نيبال', 'هولندا',
                      'جزر الأنتيل الهولندية', 'كاليدونيا الجديدة', 'نيوزيلندا', 'نيكاراغوا', 'النيجر', 'نيجيريا',
                      'نييوي', 'جزيرة نورفولك', 'كوريا الشمالية', 'مقدونيا الشمالية', 'جزر ماريانا الشمالية', 'النرويج',
                      'سلطنة عمان', 'باكستان', 'بالاو', 'فلسطين', 'بنما', 'بابوا غينيا الجديدة', 'باراغواي', 'بيرو',
                      'الفلبين', 'جزر بيتكيرن', 'بولندا', 'البرتغال', 'بورتوريكو', 'قطر', 'ريونيون', 'رومانيا', 'روسيا',
                      'رواندا', 'سان بارتيلمي', 'سانت هيلينا', 'سانت كيتس ونيفيس', 'سانت لوسيا', 'سانت مارتن',
                      'سان بيير وميكلون', 'سانت فينسنت والغرينادين', 'ساموا', 'سان مارينو', 'ساو تومي وبرينسيب',
                      'السعودية', 'السنغال', 'صربيا', 'سيشل', 'سيراليون', 'سنغافورة', 'سانت مارتن', 'سلوفاكيا',
                      'سلوفينيا', 'جزر سليمان', 'الصومال', 'جنوب أفريقيا', 'جورجيا الجنوبية وجزر ساندويتش الجنوبية',
                      'كوريا الجنوبية', 'جنوب السودان', 'إسبانيا', 'سريلانكا', 'السودان', 'سورينام',
                      'سفالبارد ويان ماين', 'السويد', 'سويسرا', 'سوريا', 'تايوان', 'طاجيكستان', 'تنزانيا', 'تايلاند',
                      'تيمور الشرقية', 'توجو', 'توكيلاو', 'تونغا', 'ترينيداد وتوباغو', 'تونس', 'تركيا', 'تركمانستان',
                      'جزر توركس وكايكوس', 'توفالو', 'جزر الولايات المتحدة الصغيرة النائية', 'جزر العذراء الأمريكية',
                      'أوغندا', 'أوكرانيا', 'الإمارات العربية المتحدة', 'المملكة المتحدة', 'الولايات المتحدة الأمريكية',
                      'أوروغواي', 'أوزبكستان', 'فانواتو', 'مدينة الفاتيكان', 'فنزويلا', 'فيتنام', 'واليس وفوتونا',
                      'الصحراء الغربية', 'اليمن', 'زامبيا', 'زيمبابوي', 'اردني', 'اردنی', 'سریلانکا', 'پاکستان',
                      'بيكور', 'ایران', 'المهلة']

    arabic_keywords_to_remove = [
        "الرقم الشخصي", "تاريخ الميلاد", "الصلاحية", "لدولة", "الجنسية", "دولة قطر", "رخصة إقامة", "المهنة", "الإسم",
        "بطاقة", "إثبات", "شخصية", "ـلـة قـ", "ـة", "سلاحية"
    ]

    filtered_lines = []
    for line in cleaned_lines:
        match_score = get_fuzzy_match_score(line, arabic_keywords_to_remove)
        match_score1 = get_fuzzy_match_score(line, countries_list)

        if match_score or match_score1:
            score = match_score if match_score else match_score1
        elif not any(pattern.search(line) for pattern in compiled_patterns):
            filtered_lines.append(line)

    occupation, occupation_en = '', ''

    front_data = {
        "nationality": nationality_iso,
        "id_number": id_number,
        "dob": dob,
        "expiry_date": expiry,
        "occupation": occupation,
        "occupation_en": occupation_en
    }

    try:
        if extract_names:
            prompt = f"""Please extract the following information from the text and provide it in a structured dictionary format: {{'occupation': 'abc', 'occupation_en': 'abc', 'nationality': 'XXX', 'name': 'FULL NAME', 'first_name': 'FIRST', 'last_name': 'LAST', 'name_ar': 'ARABIC NAME'}}
            For the name fields:
            - Extract the full name in English and split it into first and last name
            - Extract the full name in Arabic (name_ar)
            For occupation:
            - Extract in both Arabic and English
            For nationality:
            - Provide the ISO 3166-1 alpha-3 country code
            Here's the text: {ar_front_data}"""
        else:
            prompt = f"""Please extract the occupation and nationality(ISO 3166-1 alpha-3 country code) from the following text and provide it in a structured dictionary format: {{'occupation': 'abc', 'occupation_en': 'abc', 'nationality': 'XXX'}}
            So you will get occupation in arabic and translate it into english as well and send it as part of your response. The results should always be a dictionary with only 3 keys as mentioned above and nothing else.  Here's the text for your task: {ar_front_data}"""

        response = make_api_request_with_retries(prompt)

        if response.get('occupation', ''):
            front_data['occupation'] = response['occupation']

        if response.get('occupation_en', ''):
            front_data['occupation_en'] = response['occupation_en']

        if extract_names:
            if response.get('name', ''):
                front_data['name'] = response['name']
            if response.get('first_name', ''):
                front_data['first_name'] = response['first_name']
            if response.get('last_name', ''):
                front_data['last_name'] = response['last_name']
            if response.get('name_ar', ''):
                front_data['name_ar'] = response['name_ar']

        if front_data.get('occupation_en', ''):
            if front_data['occupation_en'].lower() in ['not available', 'unspecified', 'not specified',
                                                       'not provided'] or front_data[
                'occupation_en'].lower().startswith('director of nationality'):
                front_data['occupation'], front_data['occupation_en'] = '', ''

    except Exception as e:
        print(f"Error in processing the extracted data: {e}")
        front_data['occupation'], front_data['occupation_en'] = '', ''

    return front_data


def qatar_front_id_extraction(client, image_data, front_id_text, front_id_text_description, openai_key):
    # cropped_id_card, third_part, third_part_text = detect_id_card(client, image_data, front_id_text, part='third')
    # front_data = extract_name_fields_from_cropped_part(third_part_text.replace("\n", ""))
    try:
        english_name_raw = extract_name_line(front_id_text_description)
        if not english_name_raw:
            return {'error': 'covered_photo', 'error_details': 'English name not found in OCR'}

        result = qatar_id_info_chain(front_id_text_description, openai_key)

        name = result.get("name", "")
        name_parts = name.split()
        first_name = name_parts[0]
        last_name = name_parts[-1]

        front_data = {
            'name': name,
            'first_name': first_name,
            'last_name': last_name,
            'name_ar': result.get('name_ar', ''),
            'nationality': result.get('nationality', ''),
            'id_number': result.get('id_number', ''),
            'dob': result.get('dob', ''),
            'expiry_date': result.get('expiry_date', ''),
            'occupation': result.get('occupation', ''),
            'occupation_en': result.get('occupation_en', '')
        }


    except Exception as e:
        return {'error': 'covered_photo', 'error_details': f'Exception Thrown {e}'}
    # if 'error' in front_data.keys():
    #     return front_data
    # if not front_data.get('name', '') or not front_data.get('first_name', '') or not front_data.get('last_name', '') or len(front_data.get('name', '').split(' ')) < 2:
    #     front_data_temp = extract_name_fields_from_cropped_part(front_id_text_description)
    #     front_data['name'] = front_data_temp.get('name', '')
    #     front_data['first_name'] = front_data_temp.get('first_name', '')
    #     front_data['last_name'] = front_data_temp.get('last_name', '') if len(front_data_temp.get('last_name', ''))>1 else ''
    #
    # name_ar = extract_name_ar(front_id_text_description)
    # if name_ar:
    #     front_data["name_ar"] = name_ar
    # else:
    #     front_data["name_ar"] = ''

    # # Check if we need to extract names using GPT
    # need_name_extraction = not front_data.get('name', '') or not front_data.get('first_name', '') or not front_data.get('last_name', '') or not front_data.get('name_ar', '') or len(front_data.get('name', '').split(' ')) < 2
    #
    # numeric_fields = extract_numeric_fields_from_raw(front_id_text_description, third_part_text, front_data.get('name', ''), extract_names=need_name_extraction)
    #
    # #If names were extracted via GPT, update front_data with the new values
    # if need_name_extraction:
    #     if numeric_fields.get('name', ''):
    #         front_data['name'] = numeric_fields['name']
    #     if numeric_fields.get('first_name', ''):
    #         front_data['first_name'] = numeric_fields['first_name']
    #     if numeric_fields.get('last_name', ''):
    #         front_data['last_name'] = numeric_fields['last_name']
    #     if numeric_fields.get('name_ar', ''):
    #         front_data['name_ar'] = numeric_fields['name_ar']
    #
    # #Update the rest of the fields
    # front_data.update({k: v for k, v in numeric_fields.items() if k not in ['name', 'first_name', 'last_name', 'name_ar']})

    if not front_data.get('expiry_date', ''):
        try:
            # Find all dates in dd-mm-yyyy format
            date_pattern = r'\d{2}-\d{2}-\d{4}'
            dates = re.findall(date_pattern, front_id_text_description)

            if dates:
                # Convert strings to datetime objects
                date_objects = []
                for date_str in dates:
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                        date_objects.append(date_obj)
                    except ValueError:
                        continue

                if date_objects:
                    # Get the latest date as expiry
                    max_date = max(date_objects)
                    front_data['expiry_date'] = max_date.strftime('%d-%m-%Y')
                else:
                    front_data['expiry_date'] = ''
            else:
                front_data['expiry_date'] = ''
        except Exception as e:
            print(f"Error extracting expiry date: {e}")
            front_data['expiry_date'] = ''
    return front_data


def qatar_front_id_extraction_old(client, image_data, front_id_text, front_id_text_description):
    cropped_id_card, third_part, third_part_text = detect_id_card(client, image_data, front_id_text, part='third')
    front_data = extract_name_fields_from_cropped_part(third_part_text.replace("\n", ""))
    if not front_data.get('name', '') or not front_data.get('first_name', '') or not front_data.get('last_name',
                                                                                                    '') or len(
            front_data.get('name', '').split(' ')) < 2:
        front_data_temp = extract_name_fields_from_cropped_part(front_id_text_description)
        front_data['name'] = front_data_temp.get('name', '')
        front_data['first_name'] = front_data_temp.get('first_name', '')
        front_data['last_name'] = front_data_temp.get('last_name', '') if len(
            front_data_temp.get('last_name', '')) > 1 else ''

    name_ar = extract_name_ar(front_id_text_description)
    if name_ar:
        front_data["name_ar"] = name_ar
    else:
        front_data["name_ar"] = ''

    # Check if we need to extract names using GPT
    need_name_extraction = not front_data.get('name', '') or not front_data.get('first_name', '') or not front_data.get(
        'last_name', '') or not front_data.get('name_ar', '') or len(front_data.get('name', '').split(' ')) < 2

    numeric_fields = extract_numeric_fields_from_raw(front_id_text_description, third_part_text,
                                                     front_data.get('name', ''), extract_names=need_name_extraction)

    # If names were extracted via GPT, update front_data with the new values
    if need_name_extraction:
        if numeric_fields.get('name', ''):
            front_data['name'] = numeric_fields['name']
        if numeric_fields.get('first_name', ''):
            front_data['first_name'] = numeric_fields['first_name']
        if numeric_fields.get('last_name', ''):
            front_data['last_name'] = numeric_fields['last_name']
        if numeric_fields.get('name_ar', ''):
            front_data['name_ar'] = numeric_fields['name_ar']

    # Update the rest of the fields
    front_data.update(
        {k: v for k, v in numeric_fields.items() if k not in ['name', 'first_name', 'last_name', 'name_ar']})

    if not front_data.get('expiry_date', ''):
        try:
            # Find all dates in dd-mm-yyyy format
            date_pattern = r'\d{2}-\d{2}-\d{4}'
            dates = re.findall(date_pattern, front_id_text_description)

            if dates:
                # Convert strings to datetime objects
                date_objects = []
                for date_str in dates:
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                        date_objects.append(date_obj)
                    except ValueError:
                        continue

                if date_objects:
                    # Get the latest date as expiry
                    max_date = max(date_objects)
                    front_data['expiry_date'] = max_date.strftime('%d-%m-%Y')
                else:
                    front_data['expiry_date'] = ''
            else:
                front_data['expiry_date'] = ''
        except Exception as e:
            print(f"Error extracting expiry date: {e}")
            front_data['expiry_date'] = ''

    return front_data


def extract_employer_from_back(data, passport_number, passport_date, serial_no):
    patterns_to_remove = [r"\b[a-zA-Z0-9]+\b",
                          r"توقع حامل البطاقة",
                          r"مدير عام الجنسية والمنافذ وشؤون الوالدين",
                          r"المستقدم", r"توقع", r"حامل", r"البطاقة", r"مدير", r"عام", r"الإدارة",
                          r"الجوازات", r"مدير عام الجنسية والمناقة وشؤون الوافدين",
                          r"صل", r"تاريخ النهاء الجواز", r"تاريخ", r"الجواز", r"البطاقة", r"توقع حامل البطاقة",
                          r"رق[ـم]* ج[ـوا]*ز السفر", r"تاريخ انتهاء ?الجواز", r"الرقم المسلسل",
                          r"ن[ـو]*ع الرخص[ـة]*", r"مدير عام الإدارة العامة( للجوازات| الجورت)?",
                          r"عمل",
                          r"الارة البا",
                          r"وزارة الله",
                          r"مدير عام الجنسية والمنافذ وشؤون الوافدين",
                          r"مدير إدارة الجنسية و وثائق السفر",
                          r"العنوان منطقة",
                          r"General Director of Nationality",
                          r"Borders & Expatriates Affairs",
                          r"Passport expiry date",
                          r"تاریخ انتهاء الجواز",
                          r"Drectorate of Passports",
                          r"Directorate of Passports",
                          r"Holder's Signature",
                          r"Authority's signature",
                          r"Residericy Type",
                          r"ترفيع حامل البطاقة", r"توقيع حامل البطاقة", r"passport_number|passport_date|serial_no",
                          r"Holder's signature", r"Passport Number", r"Passport Expiry",
                          r"Serial No", r"Residency Type", r"Employer", r"Directorate of Passports",
                          r"General Director of the General", re.escape(passport_number),
                          re.escape(passport_date), re.escape(serial_no), r":",
                          ]

    if 'employer' not in data.lower() or 'passport' not in data.lower():
        employer = ''
        return employer

    # compiled_patterns = [re.compile(pattern) for pattern in patterns_to_remove]
    compiled_patterns = [re.compile(pattern) for pattern in patterns_to_remove if pattern.strip()]
    data = data.replace("Employer", "").replace("Employe", "").replace("المستقدم :", "").replace("المستقدم", "")

    address_keywords = ["العنوان", "منطقة", "شارع"]
    lines = [
        line.strip() for line in data.split("\n")
        if line.strip() and not any(keyword in line for keyword in address_keywords)
    ]

    filtered_lines = []
    for line in lines:
        matched = False
        for pattern in compiled_patterns:
            if pattern.search(line):
                # print(f'Pattern: {pattern.pattern} matched line: {line}')
                matched = True
                break

        if not matched:
            filtered_lines.append(line)

    # print(f'FILTERED LINES: {filtered_lines}\n')

    lines = [re.sub(r'[A-Za-z0-9]', '', i) for i in filtered_lines]

    # print(f'FILTERED LINES 2: {lines}\n')

    try:
        employer = max(lines, key=len)
    except:
        employer = ''

    if employer:
        employer.strip().replace("'", '')
    else:
        employer = ''

    return employer


def qatar_back_id_extraction(back_id_text_description):
    serial_no_pattern = r"\b\d{14}\b|\b[A-Za-z0-9]{13,16}\b"
    passport_no_pattern = r"([A-Za-z]\d{8}|[A-Za-z]{2}\d{7}|[A-Za-z]\d{7}|[A-Za-z]\d{6})"
    # emp_pattern = r'Employer:\s*([\w\s.]+.)\n\b'

    serial_no_match = re.search(serial_no_pattern, back_id_text_description, re.IGNORECASE)

    try:
        if serial_no_match:
            serial_no = serial_no_match.group(0)
        else:
            serial_no = serial_no_match.group(1)
    except:
        serial_no = ''

    passport_no_match = re.search(passport_no_pattern, back_id_text_description, re.IGNORECASE)
    if passport_no_match:
        passport_no = passport_no_match.group(0)
    else:
        passport_no = ''

    dates = sort_dates_by_datetime(re.findall(r'\d{2}/\d{2}/\d{4}', back_id_text_description))
    passport_expiry = dates[0] if dates else ''

    try:
        back_id_text_description_original = back_id_text_description
        if 'Name' in back_id_text_description:
            back_id_text_description = back_id_text_description.split("Serial")[1]

        employer = extract_employer_from_back(back_id_text_description, passport_no, passport_expiry, serial_no)
        # print(f'Employer here 1: {employer}\n')

        if employer is None or employer == '':
            back_id_text_description_splitted_2 = back_id_text_description_original.split("Name")[1]
            employer = extract_employer_from_back(back_id_text_description_splitted_2, passport_no, passport_expiry,
                                                  serial_no)
            # print(f'Employer here 2: {employer}\n')

        if not is_arabic(employer):
            employer = extract_employer_from_back(back_id_text_description, passport_no, passport_expiry, serial_no)
            # print(f'Employer here 3: {employer}\n')
    except:
        try:
            employer = extract_employer_from_back(back_id_text_description, passport_no, passport_expiry, serial_no)
            # print(f'Employer here 4: {employer}\n')
        except:
            employer = ''

    employer_en = ''
    if employer:
        try:
            employer_en = GoogleTranslator(dest='en').translate(employer)
            if employer_en and (employer_en.startswith('Director of the Nationality') or employer_en.startswith(
                    'Director of Nationality') or employer_en.startswith('Director General')) or employer_en == None:
                employer, employer_en = '', ''
        except:
            pass

    back_data = {
        "passport_number": passport_no,
        "passport_expiry": passport_expiry,
        "card_number": serial_no,
        "employer": str(employer),
        "employer_en": employer_en,
        "issuing_country": "QAT"
    }

    return back_data