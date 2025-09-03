import requests
from enum import Enum

from ..exception import AtRegistrarException

GET_FREE_ATSIGN = "/get-free-atsign"
REGISTER_ATSIGN = "/register-person"
VALIDATE_OTP = "/validate-person"
GET_ATSIGN_V3 = "/get-atsign"
ACTIVATE_ATSIGN = "/activate-atsign"

class RegisterUtil:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": None
        }

    def get_free_atsign(self, registrar_url, api_key):
        url = registrar_url + GET_FREE_ATSIGN
        self.headers["Authorization"] = api_key
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data["data"]["atsign"]

    def get_atsign_v3(self, registrar_url, api_key, atsign="", activation_key=""):
        url = registrar_url + GET_ATSIGN_V3
        self.headers["Authorization"] = api_key
        params = {
            "atSign": atsign,
            "ActivationKey": activation_key
        }
        response = self.session.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data["value"]

    def register_atsign(self, email, atsign, registrar_url, api_key):
        url = registrar_url + REGISTER_ATSIGN
        self.headers["Authorization"] = api_key
        params = {
            "email": email,
            "atsign": atsign
        }
        response = self.session.post(url, headers=self.headers, json=params)
        response.raise_for_status()
        data = response.json()
        return "Sent Successfully" in data["message"]

    def validate_otp(self, email, atsign, otp, registrar_url, api_key, confirmation):
        url = registrar_url + VALIDATE_OTP
        self.headers["Authorization"] = api_key
        params = {
            "email": email,
            "atsign": atsign,
            "otp": otp,
            "confirmation": confirmation
        }
        response = self.session.post(url, headers=self.headers, json=params)
        response.raise_for_status()
        data = response.json()
        if data["message"] == "Verified":
            return data["cramkey"]
        elif "newAtsign" in data and data["newAtsign"] == atsign:
            return "follow-up"
        elif "message" in data and "Try again" in data["message"]:
            return "retry"
        elif "message" in data and "You already have the maximum number of free @signs" in data["message"]:
            raise AtRegistrarException("Maximum free atsigns reached for email")
        else:
            return data["message"]

    def activate_atsign(self, registrar_url, api_key, atsign, activation_key):
        url = registrar_url + ACTIVATE_ATSIGN
        self.headers["Authorization"] = api_key
        params = {
            "atSign": atsign,
            "ActivationKey": activation_key
        }
        response = self.session.post(url, headers=self.headers, json=params)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "success":
            return data["cramkey"]
        else:
            raise Exception(data["status"])


class RegisterApiResult:
    def __init__(self):
        self.data = None
        self.api_call_status = None
        self.at_exception = None

class RegisterApiTask:
    max_retries = 3

    def __init__(self):
        self.retry_count = 0
        self.params = None
        self.result = RegisterApiResult()
        self.register_util = None

    def init(self, params, register_util):
        self.params = params
        self.register_util = register_util
        self.result.data = {}

    def run(self):
        pass

    def should_retry(self):
        return self.retry_count < self.max_retries

class ApiCallStatus(Enum):
    SUCCESS = 0
    FAILURE = 1
    RETRY = 2
