from dataclasses import dataclass
from typing import Optional

@dataclass
class APIKeyInfo:
    """
    Data class representing an API key and its related information.

    Attributes:
        uid (Optional[uuid.UUID]): The unique identifier of the token.
        name (Optional[str]): A user-friendly name for the token.
        api_token (str): The actual API token string.
        server_url (str): The base URL to which the token belongs.
    """
    uid: Optional[str]
    name: Optional[str]
    api_token: str
    server_url: str