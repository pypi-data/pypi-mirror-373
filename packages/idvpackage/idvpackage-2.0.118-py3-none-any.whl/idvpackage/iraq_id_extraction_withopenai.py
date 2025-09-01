import json
import time
import datetime
import openai
from langchain.tools import tool
from langchain.tools.render import format_tool_to_openai_function
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field, validator
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from typing import Optional, Literal
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
import idvpackage.genai_utils as genai_utils
import idvpackage.genai_utils as sanity_utils
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pydantic import ValidationError
import logging
from langchain.schema.agent import AgentFinish


class Verify_IRQ_Passport(BaseModel):
    """Validates whether a given OCR text represents a valid Iraqi Passport"""
    is_valid_id: Literal["True", "False"] = Field(..., description="Return True if document is a valid Iraqi Passport" 
            "It should contain Arabic/Kurdish text like: جمهورية العراق, کۆماری عێراق and English Text: Republic of Iraq"
            "Return False otherwise.")
    side: Literal["passport", ""] = Field(..., description="Return passport if the document is a valid Iraqi Passport")

class Iraq_Passport(BaseModel):
    """Extract the fields from the OCR extracted text of an Iraqi Passport"""
    full_name: str = Field(..., description="Full name of the person on the passport")
    last_name: str = Field(..., description="Surname of the person on the passport")
    dob: str = Field(..., description="Date of Birth")
    place_of_birth: str = Field(...,
        description=(
            "Place of Birth of the person on the passport"
            "DO NOT mix it up with Issuing Authority"
            "Translate to English"
        )
    )
    mother_name: str = Field(..., description="Mother's full name")
    gender_letter: str = Field(..., description="Gender/Sex of the person on the passport. It is either M or F.")
    issuing_authority: str = Field(...,
        description=(
            "Issuing Authority"
            "Translate to English"
        )
    )
    nationality: str = Field(..., description="Nationality in ISO 3166-1 alpha-3 format (e.g., 'IRQ' for Iraqi, 'JOR' for Jordanian)", example="IRQ")
    issuing_country: str = Field(..., description="Issuing Country/Country Code (e.g. 'IRQ', 'JOR')", example='IRQ')
    id_number: str = Field(..., description="9-character alphanumeric passport number.")
    mrz1: str = Field(...,
                      description=(
                          "MRZ Line 1."
                          "Should be exactly 44 characters long."
                          "If OCR splits it across lines, join them into one."
                          "Do not confuse with MRZ Line 2 — Line 1 typically starts with 'P<' and contains names."
                      )
                      )

    mrz2: str = Field(...,
                      description=(
                          "MRZ Line 2."
                          "Should be exactly 44 characters long."
                          "If OCR splits it across lines, join them into one string."
                          "Do not confuse with MRZ Line 1 — Line 2 contains passport number, nationality, DOB, expiry, etc."
                      )
                      )

    @validator("mrz2")
    def validate_mrz2_content_length(cls, v):
        if len(v.replace('<', '')) < 28:
            raise ValueError("cropped_mrz")
        return v


@tool(args_schema=Iraq_Passport)
def sanity_check_irq_passport(full_name='',
                              last_name='',
                              dob='',
                              place_of_birth='',
                              mother_name='',
                              gender_letter='',
                              issuing_authority='',
                              nationality='',
                              issuing_country='',
                              id_number='',
                              mrz='',
                              mrz1='',
                              mrz2=''):
    try:

        # if len(mrz1)<44:
        #     return {'error':'covered_photo','error_details':'cropped mrz'}
        #
        # if len(mrz2)<44:
        #     return {'error': 'covered_photo', 'error_details': 'cropped mrz'}

        # if len(mrz2.replace('<',''))<30:
        #     return {'error': 'covered_photo', 'error_details': 'cropped mrz'}


        mrz = mrz1 + mrz2



        id_number = mrz2[0:9]

        if id_number[0] == '8':
            id_number = 'B' + id_number[1:]

        expiry_date = mrz2.replace(" ", "")[21:27]
        expiry_date = sanity_utils.parse_yymmdd(expiry_date)  # string 'YYYY-MM-DD'
        is_doc_expired = sanity_utils.is_expired_id(expiry_date)

        if is_doc_expired:
            return {"error": "expired_id", "error_details": "expired ID"}

        # Reuse expiry_date for datetime object temporarily for calculations
        expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d")
        issue_date = (expiry_date_obj - relativedelta(years=8) + timedelta(days=1)).strftime("%Y-%m-%d")

        dob = sanity_utils.convert_dob_to_standard(dob)


        if gender_letter.lower() not in ['m','f','male','female']:
            gender_letter = mrz2[20]

        if gender_letter.lower()=='m':
            gender = 'Male'
        elif gender_letter.lower()=='f':
            gender = 'Female'


        optional_fields = [gender_letter]
        required_fields = {k: v for k, v in locals().items() if k not in optional_fields}

        missing = [key for key, value in required_fields.items() if not str(value).strip()]
        if missing:
            return {
                'error': 'covered_photo',
                'error_details': f'Missing or empty fields: {", ".join(missing)}'
            }
        result =  {
            "error": "",
            "error_details": "",
            "doc_type":"passport",
            **locals()
        }

        if 'expiry_date_obj' in result.keys():
            del result['expiry_date_obj']
        if 'optional_fields' in result.keys():
            del result['optional_fields']
        if 'required_fields' in result.keys():
            del result['required_fields']
        if 'missing' in result.keys():
            del result['missing']
        return result
    except Exception as e:
        return {'error':'covered_photo','error_details':e}


class Verify_IRQ_ID(BaseModel):
    """Validates whether a given OCR text represents a valid Iraqi National ID (either front or back side)."""
    is_valid_id: Literal["True", ""] = Field(..., description="Return True if document is either a valid Iraqi National ID's front side or back side." 
            "It should contain Arabic/Kurdish text like: جمهورية العراق / وزارة الداخلية"
            "مديرية الأحوال المدنية والجوازات والاقامة"
            "کوماری عیراق / وه زاره تی ناوخو"
            "پریود به را بائی باری شارستانی و پاسپورت و نیشنگه"
            "جمهورية العراق / وزارة الداخلية"
            "کوماری عیراق / وه زاره تی ناوخو"
            "Return empty string '' otherwise.")
    side: Literal["front","back",""] = Field(..., description="Determine from the given ocr text, if this is a front side or back side of an Iraqi National ID. Return empty string if its neither."
                                             "A back side has three lines of MRZ, has dates of birth, issue and expiry"
                                             "A front side has names, and id number. No dates.")

class Iraq_National_ID_front(BaseModel):
    """Extract the fields from the OCR extracted text of an Iraqi National ID's front side. Front Side has names, (like father name, mother name etc.), national id numbers but has no dates. Translate wherever required."""
    first_name: str = Field(..., description="First name (الاسم / ناو) in Arabic.")
    first_name_en: str = Field(..., description="First name (الاسم / ناو), translated to English.")
    father_name: str = Field(..., description="Father's name (الأب / باوك) in Arabic.")
    father_name_en: str = Field(..., description="Father's name (الأب / باوك), translated to English.")
    third_name: str = Field(..., description="Paternal grandfather's name (الجد / بابير) in Arabic.")
    third_name_en: str = Field(..., description="Paternal grandfather's name (الجد / بابير), translated to English.")
    last_name: Optional[str] = Field(
        "",
        description=(
            "Family/tribal name (اللقب / نازناو) in Arabic. "
            "OCR extracts various versions of 'نازناو' like الزناو, الزنار; do not interpret them as the family name."
        )
    )
    last_name_en: Optional[str] = Field(
        "",
        description=(
            "Family/tribal name (اللقب / نازناو), translated to English. "
            "OCR extracts various versions of 'نازناو' like الزناو, الزنار; do not interpret them as the family name."
        )
    )
    mother_first_name: str = Field(..., description="Mother's name (الام/ دابك) in Arabic.")
    mother_first_name_en: str = Field(..., description="Mother's name (الام/ دابك), translated to English.")
    mother_last_name: str = Field(..., description="Maternal grandfather's name (الجد / بابير) in Arabic.")
    mother_last_name_en: str = Field(..., description="Maternal grandfather's name (الجد / بابير), translated to English.")
    gender_ar: str = Field(..., description="Gender (الجنس / ردگار): ذكر (male) or أنثى (female).")
    gender: str = Field(..., description="Gender (الجنس / ردگار), translated to English")
    id_number_front: str = Field(..., description="12-digit national ID number.")
    card_number_front: str = Field(..., description="9-character alphanumeric document number.")
    serial_number: Optional[str] = Field("", description="6-digit card serial number.")
    blood_type: Optional[str] = Field(None, description="Blood type (e.g., O+, A-).")

@tool(args_schema=Iraq_National_ID_front)
def sanity_check_irq_front(
    id_number_front='',
    card_number_front='',
    first_name='',
    first_name_en='',
    father_name='',
    father_name_en='',
    third_name='',
    third_name_en='',
    last_name='',
    last_name_en='',
    mother_first_name='',
    mother_first_name_en='',
    mother_last_name='',
    mother_last_name_en='',
    gender_ar='',
    gender='',
    blood_type='',
    serial_number=''

) -> dict:
    print("SANITY CHECK IRQ FRONT WAS CALLED")
    """Run sanity checks on the data extracted from Iraq national ID's front side."""
    #Post-Processing steps
    try:
        if not id_number_front.isdigit() or len(id_number_front) != 12:
            return {'error': 'invalid_national_number', 'error_details': 'invalid national number, please take a clearer picture of your image. Note: We do not accept Civil Status IDs.'}

        if len(card_number_front) != 9:
            return {'error': 'invalid_document_number', 'error_details': 'invalid document number, please take a clearer picture of your image. Note: We do not accept Civil Status IDs.'}

        doc_type = 'national_identity_card'
        #at this point, verify_irq_id has run, so we can safely assume the nationality here is IRQ
        nationality='IRQ'
        nationality_en = 'IRQ'

        optional_fields = ('last_name', 'last_name_en','serial_number','blood_type')
        required_fields = {k: v for k, v in locals().items() if k not in optional_fields}

        result_dict = {**locals()}



        if not last_name or not last_name_en:
            name = result_dict.get('first_name', '') + " " + result_dict.get('father_name', '')
            name_en = result_dict.get('first_name_en', '') + " " + result_dict.get('father_name_en', '')
        else:
            name = result_dict.get('first_name', '') + " " + result_dict.get('father_name', '') + " " + result_dict.get('last_name','')
            name_en = result_dict.get('first_name_en', '') + " " + result_dict.get('father_name_en', '')+ " " + result_dict.get("last_name_en",'')

        missing = [key for key, value in required_fields.items() if not str(value).strip()]
        if missing:
            return {'error': 'covered_photo', 'error_details': f'Missing or empty fields: {", ".join(missing)}'}


        result =  {
            "error": "",
            "error_details": "",
            **locals()
        }

        if 'required_fields' in result.keys():
            del result['required_fields']
        if 'missing' in result.keys():
            del result['missing']
        if 'optional_fields' in result.keys():
            del result['optional_fields']
        if 'result_dict' in result.keys():
            del result['result_dict']
        return result

    except Exception as e:
        return {'error':'covered_photo','error_details':e}



class Iraq_National_ID_back(BaseModel):
    """Extract only the Arabic fields from the OCR text of an Iraqi National ID's back side. A back side has fields like dates: issue, expiry, birth. Translate where required."""
    issuing_authority: str = Field(..., description="Issuing authority (جهة الاصدار / لايانى ددرجوون) in Arabic")
    issuing_authority_en: str = Field(..., description="Issuing authority (جهة الاصدار / لايانى ددرجوون), translated to English")
    issue_date: str = Field(..., description="Date of issue")
    expiry_date: str = Field(..., description="Date of expiry")
    place_of_birth: str = Field(..., description="Place of birth in Arabic.")
    place_of_birth_en: str = Field(..., description="Place of birth, translated to English.")
    dob: str = Field(..., description="Date of birth")
    family_number: str = Field(..., description='18-character alphanumeric Family number (الرقم العائلي / ژمارەى خێزانی)')
    mrz1: str = Field(...,description="MRZ Line 1: Includes document type (ID), issuing country code (IRQ), document number, and check digits. Example: 'IDIRQAL36266736200026108063<<<'")
    mrz2: str = Field(...,description="MRZ Line 2: Encodes date of birth (YYMMDD), gender (M/F), expiry date (YYMMDD), and nationality code (IRQ) and check digit at the end of '<<<<<<'. Example: '0007191M2811280IRQ<<<<<<<<<<<7'")
    mrz3: str = Field(...,description="MRZ Line 3: Contains surname and given name(s), separated by '<<'. Given names may include multiple parts separated by '<'. If no surname is present, it starts with '<<'. Example: 'AHMED<<ALI<HASSAN' or '<<ALI'")
    last_name_back: str = Field(...,description="Surname extracted from MRZ line 3, before the '<<' separator.")
    first_name_back: str = Field(...,description="Given name extracted from MRZ line 3, after the '<<' seperator.")


@tool(args_schema=Iraq_National_ID_back)
def sanity_check_irq_back(
    issuing_authority='',
    issuing_authority_en='',
    issue_date='',
    expiry_date='',
    place_of_birth='',
    place_of_birth_en='',
    dob='', mrz1='', mrz2='', mrz3='',
    last_name_back='',
    first_name_back='',
    family_number=''
):
    try:
        #===========Post-Processing==============
        print("SANITY CHECK IRQ BACK WAS CALLED")
        """Run sanity checks on the data extracted from Iraq national ID's back side."""
        doc_type = 'national_identity_card'

        family_number = sanity_utils.fix_family_number(family_number)

        family_number_en = family_number

        #At this point, verify_irq_id has been run, so we can safely say its an Iraqi ID.
        nationality='IRQ'
        issuing_country='IRQ'

        if mrz1:
            card_number = mrz1.strip()[5:14]
            card_number_back = mrz1.strip()[5:15]
            id_number = mrz1.strip()[15:27]
            mrz = [mrz1 + mrz2 + mrz3]

        else:
            return {'error':'covered_photo', 'error_details':'cropped_mrz'}



        #==============Sanity checks for blur detection and/or cropped image
        valid_expiry_issue = sanity_utils.is_expiry_issue_diff_valid(issue_date,expiry_date, 10)
        age_check = sanity_utils.is_age_18_above(dob)
        dob_match_mrz_dob = sanity_utils.is_mrz_dob_mrz_field_match(dob, mrz2)

        is_doc_expired = sanity_utils.is_expired_id(expiry_date)

        if is_doc_expired:
            return {"error":"expired_id", 'error_details':'expired ID'}

        if mrz2:
            gender_back = sanity_utils.find_gender_from_back(mrz2.strip())
        else:
            gender_back=''



        if not (all([valid_expiry_issue, age_check, dob_match_mrz_dob])):
            return {'error':'covered_photo', 'error_details':'blur or cropped or low-quality image'}


        #Check required fields
        optional_fields = ('last_name_back','first_name_back')
        required_fields = {k: v for k, v in locals().items() if k not in optional_fields}

        missing = [key for key, value in required_fields.items() if not str(value).strip()]
        if missing:
            return {
                'error': 'covered_photo',
                'error_details': f'Missing or empty fields: {", ".join(missing)}'
            }

        result =  {
            "error": "",
            "error_details": "",
            **locals()
        }

        if 'required_fields' in result.keys():
            del result['required_fields']
        if 'missing' in result.keys():
            del result['missing']
        if 'optional_fields' in result.keys():
            del result['optional_fields']
        return result
    except Exception as e:
        return {'error':'covered_photo','error_details':e}



def route(result):
    if isinstance(result, AgentFinish):
        return {'error': 'covered_photo', 'error_details': result.return_values['output']}
    else:
        tools = {
            "sanity_check_irq_back": sanity_check_irq_back,
            "sanity_check_irq_front": sanity_check_irq_front,
            "sanity_check_irq_passport": sanity_check_irq_passport
        }
        return tools[result.tool].run(result.tool_input)

def route_verification(result):
    if isinstance(result,AgentFinish):
        return ''
    else:
        return result.tool_input

def extraction_chain(ocr_text, openai_key, side = ''):
    try:
        gpt_model = 'gpt-4o'
        print("WE ARE IN EXTRACTION CHAIN")
        tools_func = [sanity_check_irq_back, sanity_check_irq_front, sanity_check_irq_passport]

        model = ChatOpenAI(model=gpt_model, temperature=0,
                           openai_api_key=openai_key)
        extraction_functions = [format_tool_to_openai_function(f) for f in tools_func]
        extraction_model = model.bind(functions=extraction_functions)

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Extract the relevant information, if not explicitly provided do not guess, leave empty string. Extract partial info. Translate values wherever it is required."
             ),
            ("user", "{ocr_text}")
        ])

        prompt_verify_doc = ChatPromptTemplate.from_messages([
            ("system", "Verify the relevant document."
             ),
            ("user", "{ocr_text}")
        ])

        model_verification = ChatOpenAI(model=gpt_model, temperature=0,
                           openai_api_key=openai_key)
        verification_function = [convert_pydantic_to_openai_function(Verify_IRQ_ID), convert_pydantic_to_openai_function(Verify_IRQ_Passport)]
        verification_model = model_verification.bind(functions=verification_function)
        verification_chain = prompt_verify_doc | verification_model | OpenAIFunctionsAgentOutputParser() | route_verification
        st = time.time()
        verification_model_result = verification_chain.invoke({"ocr_text":ocr_text})
        logging.info(f'----------------Time taken for Verification Chain: {time.time() - st} seconds\n')
        if verification_model_result == '':
            if side=='front':
                return {'error':f'not_front_id'}, ''
            if side=='back':
                return {'error':f'not_back_id'}, ''
            if side=='page1':
                return {'error': f'not_passport'}, ''
            else:
                return {'error':'covered_photo'}
        else:
            is_valid_id = verification_model_result.get("is_valid_id","")


            if verification_model_result.get("side","")=='passport':
                side_predicted='page1'

            else:
                side_predicted = verification_model_result.get("side","")
            print("Side Predicted:", side_predicted)



        if is_valid_id=="True" and side==side_predicted:
            max_retries = 2
            st = time.time()
            for attempt in range(max_retries+1):
                extraction_chain = prompt | extraction_model | OpenAIFunctionsAgentOutputParser() | route
                data = extraction_chain.invoke({"ocr_text": ocr_text})

                if data.get('error')=='':
                    return data, side_predicted
                if data.get('error')!='' and attempt>=max_retries:
                    return data, side_predicted
                elif data.get('error')!='' and attempt<max_retries:
                    print("RETRYING")
                    time.sleep(2)
                    continue
        #Only for testing purpose, comment out when pushing to production.
        # if is_valid_id=="True" and side=='auto':
        #     max_retries = 2
        #     for attempt in range(max_retries+1):
        #         extraction_chain = prompt | extraction_model | OpenAIFunctionsAgentOutputParser() | route
        #         data = extraction_chain.invoke({"ocr_text": ocr_text})

                if data.get('error')=='':
                    return data, side_predicted
                if data.get('error')!='' and attempt>=max_retries:
                    return data, side_predicted
                elif data.get('error')!='' and attempt<max_retries:
                    print("RETRYING")
                    time.sleep(2)
                    continue
            logging.info(f'----------------Time taken for Extraction Chain: {time.time() - st} seconds\n')

        else:
            if side=='' or side=='auto':
                side = side_predicted
                error = f"not_{side}_id"
                return {'error':error}, side
            if side=='front' or side=='back':
                return {'error':f'not_{side}_id'}, side
            elif side=='page1':
                return {'error':'not_passport'}, side

    except ValidationError as e:
        errors = e.errors()  # list of error dicts
        # Extract all messages
        error = [error['msg'] for error in errors]
        return {'error':error[0], 'error_details': 'cropped mrz'},''
    except Exception as e:
        return {'error':'bad_image', 'error_details':e}, ''

# from idvpackage.llm_ocr import llm_ocr_extraction
#
# def ocr_and_extraction(base_64_image, openai_key, side):
#     openai.api_key = openai_key
#     ocr_text = llm_ocr_extraction(base_64_image)
#     result,side =  extraction_chain(ocr_text, openai_key,side)
#     return ocr_text,result,side

