import requests
import urllib3
import json
import os
from dotenv import load_dotenv
load_dotenv()

#  disable certificate warning
urllib3.disable_warnings()



# change your client id and client secret
URL_API_KEY = "https://id.cisco.com/oauth2/default/v1/token"
URL_EOX_API = "https://apix.cisco.com/software/suggestion/v2/suggestions/compatible/productId/<product-id>"
YOUR_CLIENT_ID = os.getenv("CLIENT_ID", default="")
YOUR_CLIENT_SECRET = os.getenv("CLIENT_SECRET", default="")


def _parse_apikey(json_data):
    
    try:
        api_key = json_data["access_token"]
        return api_key
    except KeyError:
        return None

def print_cyan(data):

    return f"{data}"

def get_apikey():
    params = {
        "grant_type": "client_credentials",
        "client_id": YOUR_CLIENT_ID,
        "client_secret": YOUR_CLIENT_SECRET
    }

    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:   
        response = requests.post(url=URL_API_KEY, headers=header, params=params, verify=False)

        if response.status_code == 200:
            api_key = _parse_apikey(response.json())
            return api_key, None  # Return None as the error message
        else:
            return None, f"Get Api Key is Failed, status code: {response.status_code}, reason: {response.reason}"
    except Exception as error:
        return None, f"Get Api Key is Failed cause Unknown Error, msg: {error}"

def get_ss_data(api_key, product_id):
    url = URL_EOX_API.replace("<product-id>", product_id)
    header = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url=url, headers=header, verify=False)

        if response.status_code == 200:
            result = response.json()
            if result == "":
                result = "N/A"
            return result, None
        else:
            return None, f"Get EOX data for SN: {product_id} is Failed, status code: {response.status_code}, reason: {response.reason}"
    except Exception as error:
        return None, f"Get EOX data for SN: {product_id} is Failed, Cause: Unknown Error, msg: {error}"