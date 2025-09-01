__version__  = '0.2.50'

from etiket_client.settings.logging import set_up_logging
set_up_logging(__name__, __version__)

from etiket_client.sync.database.start_up import start_up
from etiket_client.sync.proc import start_sync_agent, restart_sync_agent
from etiket_client.remote.authenticate import logout, authenticate_with_console, login_with_api_token

start_up()
start_sync_agent()
