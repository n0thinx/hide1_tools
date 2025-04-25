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
URL_EOX_API = "https://apix.cisco.com/supporttools/eox/rest/5/EOXBySerialNumber/1/<serial-number>"
URL_EOX_API_2 = "https://apix.cisco.com/supporttools/eox/rest/5/EOXByProductID/1/<product-id>"
YOUR_CLIENT_ID = os.getenv("CLIENT_ID", default="")
YOUR_CLIENT_SECRET = os.getenv("CLIENT_SECRET", default="")


def _parse_apikey(json_data):
    
    try:
        api_key = json_data["access_token"]
        return api_key
    except KeyError:
        return None

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
        response = requests.post(url=URL_API_KEY, headers=header, params=params, verify=False) # create request for get api key
        if response.status_code == 200:
            api_key = _parse_apikey(response.json())
            return api_key, None  # Return None as the error message
        else:
            return None, f"Get Api Key is Failed, status code: {response.status_code}, reason: {response.reason}"
    except Exception as error:
        return None, f"Get Api Key is Failed cause Unknown Error, msg: {error}"


def get_eox_data(api_key, serial_number):

    url = URL_EOX_API.replace("<serial-number>", serial_number)
    
    header = {
        "Authorization": f"Bearer {api_key}"
    }
    
    params = {
        "responseencoding": "json",
    }
    
    
    try:
        # Get Data EOX
        response = requests.get(url=url, headers=header, params=params, verify=False)
        if response.status_code == 200:
            result = response.json()
            print(f" Get EOX data for SN: {(serial_number)} is Success")
            return result, None
        else:
            return None, f"Get EOX data for SN: {(serial_number)} is Failed, status code: {(response.status_code)}, reason: {(response.reason)}"
    except Exception as error:
        return None, f"Get EOX data for SN: {(serial_number)} is Failed, Cause: Unknown Error, msg: {error}"


def get_eox_data_2(api_key, product_id):
    url = URL_EOX_API_2.replace("<product-id>", product_id)
    header = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "responseencoding": "json",
    }
    try:
        # Get Data EOX
        response = requests.get(url=url, headers=header, params=params, verify=False)
        if response.status_code == 200:
            result = response.json()
            print(f" Get EOX PID data for PID: {(product_id)} is Success")
            return result, None
        else:
            return None, f"Get EOX PID data for PID: {(product_id)} is Failed, status code: {(response.status_code)}, reason: {(response.reason)}"
    except Exception as error:
        return None, f"Get EOX PID data for PID: {(product_id)} is Failed, Cause: Unknown Error, msg: {error}"