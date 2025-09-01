import etiket_client

from typing import List
from semantic_version import Version

from etiket_client.local.dao.app import dao_app_registerer

from etiket_client.remote.endpoints.models.version import ReleaseRead, VersionRead, currentVersionsNumbers
from etiket_client.remote.endpoints.version import get_web_api_version, SoftwareType, get_latest_version, get_versions,\
get_latest_release as get_latest_release_endpoint, get_release_from_version, VersionRead

def get_last_version() -> VersionRead:
    return get_latest_version(SoftwareType.qdrive, allow_beta=allow_beta())

def get_new_versions() -> List[VersionRead]:
    versions = get_versions(SoftwareType.qdrive, min_version=__format_current_version(), allow_beta=allow_beta()) 
    # since the server is not so good at filtering beta versions, we need to filter them out here
    return [version for version in versions if Version(version.version) > Version(__format_current_version() )]

def get_latest_release() -> ReleaseRead:
    return get_latest_release_endpoint(allow_beta=allow_beta())

def find_current_versions() -> currentVersionsNumbers:
    api_version = get_web_api_version()
    etiket_version = etiket_client.__version__
    dataQruiser_version_full = dao_app_registerer.get_dataQruiser_version()
    if dataQruiser_version_full is not None:
        dataQruiser_version = dataQruiser_version_full.version
    else:
        dataQruiser_version = None
    
    return currentVersionsNumbers(etiket_version=api_version, qdrive_version=etiket_version, dataQruiser_version=dataQruiser_version)    

# this is not very robust, but it should work for now
def allow_beta() -> bool:
    return any(beta_designation in etiket_client.__version__ for beta_designation in ["dev", "a", "b", "rc"])

def __format_current_version() -> str:
    return etiket_client.__version__.replace("dev", "-dev").replace("a", "-alpha").replace("b", "-beta").replace("rc", "-rc")
