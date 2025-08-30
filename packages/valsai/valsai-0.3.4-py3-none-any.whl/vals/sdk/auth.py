import os
import re
import time

import requests
from descope import DescopeClient

VALS_ENV = os.getenv("VALS_ENV", "PROD")
VALS_ENDPOINT = os.getenv("VALS_ENDPOINT", None)

DEFAULT_REGION = "us-east-1"

global_api_key = None
global_in_eu = None
global_auth_dict = {}
global_endpoint = None


def configure_credentials(
    api_key: str, in_eu: bool = False, endpoint: str | None = None
):
    """
    Configure the Vals API Key to be used with requests.
    This will take precedence over any credentials set in environment variables, or with vals login.

    API key can be generated in the Web App. If you are using the EU platform, make sure to set
    in_eu = True, otherwise leave it as the default.
    """
    global global_api_key, global_in_eu, global_endpoint
    global_api_key = api_key.strip()
    global_in_eu = in_eu
    global_endpoint = endpoint


def _get_region():
    global global_in_eu
    if global_in_eu is not None:
        return "eu-north-1" if global_in_eu else "us-east-1"

    if "VALS_REGION" in os.environ:
        vals_region = os.environ["VALS_REGION"].lower()
        if vals_region not in ["europe", "us"]:
            raise ValueError(
                f"Invalid region: {vals_region}. Must be 'europe' or 'us'."
            )

        return "eu-north-1" if vals_region == "europe" else "us-east-1"

    return DEFAULT_REGION


def be_host():
    frontend_host = fe_host()

    if frontend_host == "https://platform.vals.ai":
        return "https://prodbe.playgroundrl.com"
    if frontend_host == "https://eu.platform.vals.ai":
        return "https://europebe.playgroundrl.com"
    if frontend_host == "https://dev.platform.vals.ai":
        return "https://devbe.playgroundrl.com"
    if frontend_host == "https://bench.platform.vals.ai":
        return "https://benchbe.playgroundrl.com"
    if frontend_host == "http://localhost:3000":
        return "http://localhost:8000"

    return f"{frontend_host.split('.')[0]}-be.vals.ai"


def _clean_frontend_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith("https://") or url.startswith("http://"):
        url = f"https://{url}"

    # Check if the URL is valid and ends with platform.vals.ai
    # Accepts both http and https, and optional subdomains/orgs
    pattern = r"^https?://([a-zA-Z0-9\-]+\.)*platform\.vals\.ai$"
    if not re.match(pattern, url):
        raise ValueError(f"Unrecognized frontend endpoint: {url}")

    return url


def fe_host():
    if global_endpoint is not None and global_endpoint != "":
        return _clean_frontend_url(global_endpoint)

    if VALS_ENDPOINT is not None:
        return _clean_frontend_url(VALS_ENDPOINT)

    region = _get_region()
    if region == "eu-north-1":
        return "https://eu.platform.vals.ai"
    if VALS_ENV == "LOCAL":
        return "http://localhost:3000"
    if VALS_ENV == "DEV":
        return "https://dev.platform.vals.ai"
    if VALS_ENV == "BENCH":
        return "https://bench.platform.vals.ai"

    return "https://platform.vals.ai"


def get_descope_client():
    if (
        global_endpoint is not None
        and global_endpoint != ""
        or VALS_ENDPOINT is not None
    ):
        try:
            response = requests.post(
                f"{be_host()}/get_descope_project_id/",
            )
        except Exception:
            raise Exception(
                f"Could not connect to the backend server. Double check the endpoint: {fe_host()}"
            )

        if response.status_code != 200:
            raise Exception("Error reading the Descope Project ID from the server.")
        data: dict[str, str] = response.json()
        if "project_id" not in data:
            raise Exception("Error reading the Descope Project ID from the server.")
        project_id: str = str(data["project_id"])

    elif _get_region() == "eu-north-1":
        project_id = "P2lXkjgPTaW5f8ZlhBzCpnxeqlpj"
    elif VALS_ENV == "DEV" or VALS_ENV == "BENCH":
        project_id = "P2ktNOjz5Tgzs9wwS3VpShnCbmik"
    elif VALS_ENV == "LOCAL":
        project_id = "P2xKhP7i7uQCa2YC3JaSf44h4Fll"
    elif VALS_ENV == "PROD":
        project_id = "P2lXkZaPuDqCzGxoxGHseomQi7ac"

    else:
        raise Exception(f"Unrecognized VALS_ENV: {VALS_ENV}")
    return DescopeClient(project_id=project_id, jwt_validation_leeway=30)


def _get_auth_token():
    """
    Get a new session token that can be used in Authorization header.

    Internally, reads the api key from either the VALS_ENV
    variable or a configured value, then uses the Descope SDK to
    exchange the api key for a session token.
    """
    global global_api_key, global_in_eu, global_auth_dict

    # API key was specified with configure_credentials
    if global_api_key is not None:
        api_key = global_api_key

    # API Key is specified in environment
    elif "VALS_API_KEY" in os.environ:
        api_key = os.environ["VALS_API_KEY"]
    else:
        raise Exception(
            "Either the `VALS_API_KEY` environment variable should be set, or the API key should be set with configure_credentials (in vals.sdk.auth.)."
        )

    if (
        "access_expiry" not in global_auth_dict
        # Refresh token 1 minute before it expires
        or time.time() + 60 > global_auth_dict["access_expiry"]
    ):
        descopeClient = get_descope_client()

        response = descopeClient.exchange_access_key(api_key)

        global_auth_dict = {
            **global_auth_dict,
            "access_token": response["sessionToken"]["jwt"],
            "access_expiry": response["sessionToken"]["exp"],
        }

    return global_auth_dict["access_token"]
