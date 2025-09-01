from etiket_client.exceptions import NoLoginInfoFoundException, NotLoggedInException
from etiket_client.remote.client import client
from etiket_client.remote.api_tokens import validate_or_generate_api_token, add_api_token
from etiket_client.settings.user_settings import user_settings
from etiket_client.sync.backends.native.sync_user import sync_current_user
from etiket_client.sync.backends.native.sync_scopes import sync_scopes
from etiket_client.local.database import Session

from dataclasses import dataclass
from getpass import getpass
from typing import Callable, Dict, List, Optional

import logging, requests, json, sysconfig, os, etiket_client

logger = logging.getLogger(__name__)

AUTH_METHODS_URL = "https://server-info.dataqruiser.com/server_addresses_1.1.json"

@dataclass
class OpenIdConfig:
    name: str
    client_id: str
    audience: str
    openid_configuration_url: str
    scopes: List[str]

@dataclass
class AuthConfig:
    server_url : str
    allow_password_flow: bool
    openid_providers: List[OpenIdConfig]

def authenticate_with_console() -> None:
    """
    Authenticate the user via console input.
    """
    auth_methods = get_auth_methods()
    if not auth_methods:
        print("Failed to retrieve servers and associated auth methods. Please try again later.")
        return

    print("Please select the server you want to log in to:")
    for i, institution in enumerate(auth_methods.keys()):
        print(f"{i + 1}. {institution}")

    try:
        selected_index = int(input("Please enter the number of your server: ")) - 1
        selected_institution = list(auth_methods.keys())[selected_index]
        selected_auth_config = auth_methods[selected_institution]
    except (ValueError, IndexError):
        print("Invalid selection. Please try again.")
        return

    if len(selected_auth_config.openid_providers) + int(selected_auth_config.allow_password_flow) > 1:
        print("Please select your authentication method:")
        for i, openid_provider in enumerate(selected_auth_config.openid_providers):
            print(f"{i + 1}. {openid_provider.name}")
        if selected_auth_config.allow_password_flow:
            print(f"{len(selected_auth_config.openid_providers) + 1}. QHarbor username and password")
        try:
            selected_index = int(input("Please enter the number of your authentication method: ")) - 1
            if selected_index < 0 or selected_index > len(selected_auth_config.openid_providers):
                raise ValueError
        except ValueError:
            print("Invalid selection. Please try again.")
        
        if selected_index != len(selected_auth_config.openid_providers):
            return login_using_sso(selected_auth_config.openid_providers[selected_index], selected_auth_config.server_url)
    else:
        if selected_auth_config.allow_password_flow == False:
            return login_using_sso(selected_auth_config.openid_providers[0], selected_auth_config.server_url)    
        
    username = input("Please enter your username: ")
    password = getpass("Please enter your password: ")

    try:
        login_legacy(username, password, auth_methods[selected_institution])
        print(f"Log in successful. Welcome {username}!")
    except Exception as e:
        print(f"Log in failed: {e}, please try again.")
    
def login_legacy(username: str, password: str, institution_url: str) -> None:
    """
    Log in to the specified institution.
    """
    client._login_legacy(username, password, institution_url)
    with Session() as session:
        sync_current_user(session)
        validate_or_generate_api_token(username, institution_url)
        sync_scopes(session)

def login_using_sso(openIdInfo: OpenIdConfig, institution_url: str, tcp_server_listener: Optional[Callable[[int], str]]=None) -> None:
    """
    Log in to the specified institution using SSO.
    """
    client._login_via_sso(openIdInfo.client_id, openIdInfo.openid_configuration_url, institution_url,
                          openIdInfo.scopes, tcp_server_listener)
    with Session() as session:
        sync_current_user(session)
        validate_or_generate_api_token(user_settings.user_sub, institution_url)
        sync_scopes(session)

def login_with_api_token(api_connection_string : str) -> None:
    """
    Logs in using an API token and sets the client for subsequent requests.
    
    Args:
        api_connection_string (str): The API token and server URL separated by a at sign (@).
    """
    if "@" not in api_connection_string:
        raise ValueError("Invalid format: connection string must contain an '@' character")
        
    parts = api_connection_string.split("@", 1)  # Split on first @ only
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid format: connection string must be in the format 'token@server_url'")
        
    api_token, server_url = parts
    client._login_via_api_token(api_token, server_url)
    with Session() as session:
        sync_current_user(session)
        add_api_token(api_token, server_url)
        sync_scopes(session)

def get_auth_methods() -> Dict[str, AuthConfig]:
    """
    Retrieves authentication methods for institutions by fetching a JSON
    file from a remote server. Returns a dictionary where the keys are
    institution names and values are AuthConfig objects with server URL,
    password flow permissions, and OpenID provider details.
    """    
    try:
        response = requests.get(AUTH_METHODS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
   
        auth_methods = {}

        for institution, auth_config in data['server_addresses'].items():
            try:
                if auth_config.get("is_development", True) is False or dev_mode_enabled():
                    auth_methods[institution] = AuthConfig(
                        server_url=auth_config['etiket_url'],
                        allow_password_flow=auth_config['allow_password_flow'],
                        openid_providers=[
                            OpenIdConfig(
                                name=openid_config_name,
                                client_id=openid_config['client_id'],
                                audience=openid_config.get('audience', None),
                                openid_configuration_url=openid_config['config_url'],
                                scopes=openid_config.get('scopes', [])
                            ) for openid_config_name, openid_config in auth_config.get('openid_providers', {}).items()
                        ]
                    )
            except KeyError as e:
                logger.error(
                    "Missing expected key '%s' for institution '%s' in the JSON response from URL '%s'.",
                    e, institution, AUTH_METHODS_URL
                )
                raise KeyError(f"Failed to parse server addresses for institution '{institution}'. Missing key '{e}'.") from e
        return auth_methods
    except requests.exceptions.RequestException as e:
        logger.error("Error downloading the file: %s", e)
        raise ValueError(f"Error downloading the server addresses from '{AUTH_METHODS_URL}'.") from e
    except json.JSONDecodeError as e:
        logger.error("Error decoding the JSON: %s", e)
        raise ValueError(f"Error decoding the JSON from '{AUTH_METHODS_URL}'.") from e

def _is_logged_in() -> bool:
    """
    Check if the user is logged in by attempting to refresh the token.
    """
    logger.info("Checking if host is logged in.")
    try:
        client.get("/token/userinfo", api_version="v3")
        return True
    except NoLoginInfoFoundException:
        logger.info("Host is not logged in.")
        return False

def logout() -> None:
    client._logout()

def validate_login_status() -> None:
    if client.check_login() is False:
        raise NotLoggedInException("No user is logged in, please log in first.")
    
def dev_mode_enabled() -> bool:
    """
    Check if the package is installed in development mode.
    """
    try:
        lib_location = etiket_client.__file__
        site_package_location = sysconfig.get_paths()['purelib']
        if os.path.commonpath([lib_location, site_package_location]) == site_package_location:
            return False
        return True
    except Exception:
        return False