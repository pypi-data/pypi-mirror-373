import logging, getpass, socket, platform, random, string, time
from contextlib import contextmanager
from typing import Optional


from etiket_client.settings.user_settings import user_settings
from etiket_client.exceptions import APIKeyInvalidException
from etiket_client.remote.client import client
from etiket_client.remote.endpoints.api_tokens import api_token_create, api_token_delete
from etiket_client.local.dao.api_token import dao_api_token, APIKeyInfo
from etiket_client.local.database import Session
from etiket_client.remote.errors.api_tokens import APITokenNotFound
from etiket_client.sync.backends.native.sync_user import sync_current_user

logger = logging.getLogger(__name__)

# TOKEN_CACHE maps user_sub to a tuple: (timestamp, APIKeyInfo)
TOKEN_CACHE = {}
CACHE_LIFETIME = 300 # 5 minutes

def generate_token_name() -> str:
    """
    Generates a descriptive token name based on the current user, host name,
    operating system, and a 6-character alphanumeric string (letters and digits).
    
    Returns:
        str: A descriptive token name.
    """
    user = getpass.getuser()              # Current logged in user
    hostname = socket.gethostname()         # Host name
    os_name = platform.system()             # Operating system (e.g. "Windows", "Darwin", "Linux")
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{user}@{hostname} ({os_name})-{random_chars}"

def validate_or_generate_api_token(user_sub: str, server_url: str):
    """
    Generates and stores a new API token for the specified user if no valid token currently exists.

    Args:
        user_sub (str): The user's 'sub' identifier.
        server_url (str): The server's base URL.

    Returns:
        APIKeyInfo: The new (or valid existing) API token information.
    """
    existing_token = get_api_info_from_user(user_sub)
    if existing_token:
        try:
            test_api_token(user_sub, existing_token)
            return
        except APIKeyInvalidException:
            logger.info("Existing API token for user %s is invalid; removing it.", user_sub)
            remove_api_token(user_sub)
    
    token_info_raw = api_token_create(name=generate_token_name())
    token_info = APIKeyInfo(
        uid=token_info_raw.uid,
        name=token_info_raw.name,
        api_token=token_info_raw.api_token,
        server_url=server_url
    )
    store_API_token(token_info)
    logger.info("New API token created for user %s with name %s", user_sub, token_info_raw.name)
    return


def add_api_token(api_token: str, server_url: str) -> APIKeyInfo:
    """
    Adds an existing API token to the user's account.
    
    Args:
        api_token (str): The API token string.
        server_url (str): The server's base URL.
    """
    user_sub = test_api_token("unknown", APIKeyInfo(uid=None, name=None, api_token=api_token, server_url=server_url))
    remove_api_token(user_sub)
    token_info = APIKeyInfo(uid=None, name=None, api_token=api_token, server_url=server_url)
    store_API_token(token_info, check_user_account=True)
    
    logger.info("API token added for user %s", user_sub)
    return token_info

def remove_api_token(user_sub: str) -> None:
    current_token = get_api_info_from_user(user_settings.user_sub)
    if current_token:  # remove old token
        try:
            if current_token.uid is not None:  # token is managed by the server
                test_api_token(user_settings.user_sub, current_token)
                try:
                    api_token_delete(current_token.uid)
                except APITokenNotFound:  # token was manually deleted on the server
                    pass
                logger.info("API token for user %s deleted.", user_sub)
            else:
                logger.warning("API token for user %s is not managed by the server, cannot delete.", user_sub)
        except APIKeyInvalidException:
            pass
        finally:
            with Session() as session:
                dao_api_token.delete(user_settings.user_sub, session)
            # Remove the token from the cache if present.
            TOKEN_CACHE.pop(user_settings.user_sub, None)

def get_api_info_from_user(user_sub: str) -> Optional[APIKeyInfo]:
    """
    Retrieves the API token information for a given user (sub) from a local cache or database.
    Validates the token with the server; if invalid or the cached entry is stale, returns None.

    Args:
        user_sub (str): The 'sub' identifier for the user.

    Returns:
        Optional[APIKeyInfo]: An APIKeyInfo object if valid, otherwise None.
    """
    now = time.time()
    # Check if we have a cached token and whether it is still valid (not older than 5 minutes)
    if user_sub in TOKEN_CACHE:
        cached_time, api_token_info = TOKEN_CACHE[user_sub]
        if now - cached_time < CACHE_LIFETIME:
            return api_token_info
        else:
            TOKEN_CACHE.pop(user_sub)
    
    with Session() as session:
        api_token_info = dao_api_token.read(user_sub, session)
        if api_token_info is None:
            return None
        try:
            test_api_token(user_sub, api_token_info)
            TOKEN_CACHE[user_sub] = (now, api_token_info)
            return api_token_info
        except APIKeyInvalidException:
            logger.warning("API token invalid for user %s", user_sub)
            return None

def test_api_token(user_sub : str, token_info: APIKeyInfo) -> str:
    """
    Mock function to retrieve user info from the server's user-info endpoint.
    Replace this with your actual imported user_read_me function or logic.
    
    Args:
        user_sub (str): The user's sub identifier.
        token_info (APIKeyInfo): The API token info to test.
    
    Returns:
        user_sub (str): The user's sub identifier.
    """
    with client.set_api_key(user_sub, token_info.api_token, token_info.server_url):
        try:
            response = client.get("/token/userinfo", api_version="v3")
            return response['sub']
        except:
            raise APIKeyInvalidException("API token invalid.")

def store_API_token(token_info: APIKeyInfo, check_user_account: bool = False) -> None:
    """
    Stores the given API token information in the local database and updates the in-memory cache.

    Args:
        token_info (APIKeyInfo): An instance of APIKeyInfo containing token details such as uid, name,
                                 api_token, and server_url.
    """
    with client.set_api_key("unknown", token_info.api_token, token_info.server_url):
        with Session() as session:
            if check_user_account is True:
                sync_current_user(session)
            dao_api_token.create(user_settings.user_sub, token_info, session)
            TOKEN_CACHE[user_settings.user_sub] = (time.time(), token_info)
            logger.info("API token stored for user %s", user_settings.user_sub)
            
@contextmanager
def api_token_session(user_sub: Optional[str]):
    """
    A context manager that wraps client.set_api_key when a valid user_sub is provided.
    
    If user_sub is not None, retrieves the API token info and calls client.set_api_key
    to temporarily use the matching session. If user_sub is None or no token is found,
    it yields directly without modifying the session.
    
    Args:
        user_sub (str): The user's 'sub' identifier.
        
    Usage:
        with api_token_session(user_sub):
            # code executed under the user's session, if available
            response = client.get("/some/endpoint")
    """
    if user_sub is not None:
        api_token_info = get_api_info_from_user(user_sub)
        if api_token_info is not None:
            with client.set_api_key(user_sub, api_token_info.api_token, api_token_info.server_url):
                yield
        else:
            yield
    else:
        yield