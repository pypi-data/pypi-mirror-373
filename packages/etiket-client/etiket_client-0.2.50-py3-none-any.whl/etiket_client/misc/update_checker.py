import datetime, time, sys, subprocess, platform, threading

from etiket_client.python_api.version import get_new_versions
from etiket_client.settings.user_settings import user_settings
from etiket_client.exceptions import NoLoginInfoFoundException

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

def start_update_checker():
    # start separate thread to check for updates
    t = threading.Thread(target=check_for_updates, daemon=True)
    t.start()

def check_for_updates():
    while True:
        # Check for updates
        try :
            user_settings.load()
            if (user_settings.last_version_check is None or 
                    (datetime.datetime.now().timestamp() - user_settings.last_version_check) > 60*60*24):
                new_versions = get_new_versions()
                if len(new_versions) > 0:
                    load_proc()
                
            user_settings.last_version_check = datetime.datetime.now().timestamp()
            user_settings.write()
        except NoLoginInfoFoundException:
            pass
        except Exception as e:
            print("Failed to check for updates. Error: ", e)
        
        # Sleep for 1 hour
        time.sleep(60*60)

def load_proc():
    module_name =  'etiket_client.GUI.update.app'
    cmd = [sys.executable, '-m', module_name, '--detached' ]

    if platform.system() == 'Windows':
        creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        creationflags = 0
    
    subprocess.Popen(cmd,
                        creationflags=creationflags,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        close_fds=True,
                        text=True)