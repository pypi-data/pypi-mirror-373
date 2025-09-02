import os

import requests
from dotenv import load_dotenv
from functools import cache

from ..logging import setup_logging

logger = setup_logging(__file__)
values_loaded = load_dotenv("cred.env")
logger.info("credentials loaded from env: " + str(values_loaded))

ACCESS_ID = os.getenv('access_id')
ACCESS_KEY = os.getenv('access_key')

AUTH_URL = "https://api.akeyless.io/auth"
SECRET_URL = "https://api.akeyless.io/get-secret-value"
TARGET_URL = "https://api.akeyless.io/get-target-details"

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json"
}


@cache
def __get_token():
    token_response = requests.post(AUTH_URL, json={
        "access-type": "access_key",
        "access-id": ACCESS_ID,
        "access-key": ACCESS_KEY,
    }, headers=HEADERS).json()
    return token_response['token']


def get_secrets(secrets):
    if isinstance(secrets, str):
        secrets = [secrets]
    payload = {
        "accessibility": "regular",
        "names": secrets,
        "pretty-print": True,
        "token": __get_token()
    }
    try:
        response = requests.post(SECRET_URL, json=payload, headers=HEADERS).json()
    except Exception as e:
        logger.error(e)
        __get_token.cache_clear()
        payload = {
            "accessibility": "regular",
            "names": secrets,
            "pretty-print": True,
            "token": __get_token()
        }
        response = requests.post(SECRET_URL, json=payload, headers=HEADERS).json()
    if len(secrets) == 1:
        return response[secrets[0]]
    return [response[secret] for secret in secrets]


def get_target(name: str):
    payload = {
        "show-versions": False,
        "name": name,
        "token": __get_token()
    }
    try:
        response = requests.post(TARGET_URL, json=payload, headers=HEADERS).json()
    except Exception as e:
        logger.error(e)
        __get_token.cache_clear()
        payload = {
            "show-versions": False,
            "name": name,
            "token": __get_token()
        }
        response = requests.post(TARGET_URL, json=payload, headers=HEADERS).json()
    return list(response['value']['db_target_details'].values())
