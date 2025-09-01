import urllib.request, urllib.error, logging 

logger = logging.getLogger(__name__)

def check_internet_connection(timeout = 5) -> bool:
    """
    Checks if an internet connection can be made.
    """
    try:
        urllib.request.urlopen('https://www.google.com', timeout = timeout)
        return True
    except urllib.error.URLError:
        logger.exception("ConnectionError : Failed to open URL")
        return False