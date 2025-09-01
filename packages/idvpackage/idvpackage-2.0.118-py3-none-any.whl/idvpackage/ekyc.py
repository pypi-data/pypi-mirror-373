import requests
from idvpackage.constants import *
from idvpackage.ocr_utils import fuzzy_match_fields
import openai

class Ekyc:

    def __init__(self):
        self.maps_endpoint = GOOGLE_MAPS_API_ENDPOINT
        self.gmaps_api_key = API_KEY
        self.openai_key = OPENAI_API_KEY

    def classify_address(self, address):
        openai.api_key = self.openai_key
        prompt = f"Consider yourself as an address guide, your task is to do address classification from the address that you receive. you'll only respond in 1 word that is either residential or commercial. here is an address, tell me if this address is residential or commercial: {address}"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0]["message"]["content"]

    def verify_address(self, address):
        endpoint = self.maps_endpoint
        
        params = {
            "address": address,
            "key": self.gmaps_api_key,
        }

        try:
            response = requests.get(endpoint, params=params)
            data = response.json()
            if response.status_code == 200:
                if data['status'] == 'OK':
                    for result in data['results']:
                        for address_type in result['types']:
    #                         print(result['types'])
    #                         if address_type in ['street_address', 'subpremise', 'premise']:
    #                             return "Residential", result['formatted_address'], result['types']
                            if address_type in ['food', 'restaurant', 'lodging', 'business', 'general_contractor', 'hair_care', 'health', 'spa']:
                                return True, "Commercial"
                            
                        return True, "Residential"
                    return False, "Unknown"
                else:
                    return False, None
            else:
                return False, None
        
        except Exception as e:
            return False, None
        
    def address_validation(self, user_input_address, utility_bill_address, address_from_other_source):
        res1 = fuzzy_match_fields(user_input_address, address_from_other_source)
        res2 = fuzzy_match_fields(user_input_address, utility_bill_address)

        if res1 or res2:
            return True
        else:
            return False
    
    def address_verification_and_validation(self, address):
        address = {
            'error': ''
        }
        result = self.verify_address(address)
        classification_result = self.classify_address(address)

        if result and classification_result.lower() == 'residential':
            return address
        
        else:
            address['error'] = 'address_caution'
