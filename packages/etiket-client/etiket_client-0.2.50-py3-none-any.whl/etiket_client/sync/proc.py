import logging, psutil, sys, subprocess, platform
import re

from etiket_client.settings.user_settings import user_settings
from typing import List

logger = logging.getLogger(__name__)

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

class PIDGetError(Exception):
    pass

def _get_windows_python_pids():
    """Get PIDs of Python processes on Windows using cmd.exe"""
    try:
        cmd = ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/NH', '/FO', 'CSV']
        result = subprocess.run(['cmd', '/c', *cmd], 
                                capture_output=True, text=True, check=True)
        pids = []
        for line in result.stdout.splitlines():
            if line.strip():
                match = re.search(r'"(\d+)"', line)
                if match:
                    pids.append(int(match.group(1)))
        return pids
    except Exception as e:
        raise PIDGetError(f"Error getting PIDs: {e}")

def start_sync_agent():
    logger.info('Trying to start a new sync agent.')
    name ='etiket_sync'
    module_name =  'etiket_client.sync.run'
    cmd = [sys.executable, '-m', module_name, '--detached' ]
    
    running, procs = _is_running(name , module_name, use_settings=False)
    if not running:
        if platform.system() == 'Windows':
            creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        else:
            creationflags = 0
        proc = subprocess.Popen(
                cmd,
                creationflags=creationflags,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                close_fds=True,
                text=True)
        logger.info('New sync process started.')
    else:
        proc = procs[0]
    
    if user_settings.sync_PID != proc.pid:
        user_settings.sync_PID = proc.pid
        user_settings.write()

def restart_sync_agent():
    logger.info('Trying to restart the sync agent.')
    kill_sync_agent()
    start_sync_agent()

def is_running_sync_agent(fast = True):
    name ='etiket_sync'
    module_name =  'etiket_client.sync.run'
    running, _ = _is_running(name, module_name, use_settings=fast)
    return running

def kill_sync_agent():
    name ='etiket_sync'
    module_name =  'etiket_client.sync.run'
    running, procs = _is_running(name, module_name, use_settings=False)
    if running:
        for proc in procs: proc.kill()
                    
def _is_running(name, module_name, use_settings=True) -> 'List[bool, List[psutil.Process]]':
    logger.info('Checking if sync agent is running, use_settings = %s.', use_settings)

    if use_settings:
        user_settings.load()
        if user_settings.sync_PID:
            try:
                proc = psutil.Process(user_settings.sync_PID)
                if proc.name().startswith('python') or proc.name().startswith('Python'):
                    if module_name in proc.cmdline() or 'Python qdrive sync' in proc.cmdline():
                        logger.info('Sync agent is running (proc name :: %s, with module name : %s and PID %s).', name, module_name, proc.pid)
                        return True, [proc]
            except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
                pass
    else:
        if platform.system() == 'Windows':
            try:
                logger.info('Attempting to get Python PIDs using cmd.exe')
                python_pids = _get_windows_python_pids()
                procs = []
                for pid in python_pids:
                    try:
                        proc = psutil.Process(pid)
                        if module_name in proc.cmdline() or 'Python qdrive sync' in proc.cmdline():
                            logger.info('Sync agent found via tasklist (proc name :: %s, with module name : %s and PID %s).', name, module_name, proc.pid)
                            procs.append(proc)
                    except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
                        continue
                # If tasklist succeeded, return its findings directly
                logger.info(f'Tasklist method found {len(procs)} matching process(es).')
                return bool(procs), procs
            except PIDGetError as e:
                 logger.warning(f"Failed to get PIDs using tasklist: {e}. Falling back to psutil.process_iter.")
                 # Fall through to the generic psutil method below

        # This part runs for non-Windows systems OR as a fallback for Windows
        logger.info('Using psutil.process_iter to find sync agent.')
        procs = []
        for proc in psutil.process_iter(['name', 'cmdline', 'pid']):
            try:
                if proc.name().startswith('python') or proc.name().startswith('Python'):
                    if module_name in proc.cmdline() or 'Python qdrive sync' in proc.cmdline():
                        logger.info('Sync agent found via psutil (proc name :: %s, with module name : %s and PID %s).', name, module_name, proc.pid)
                        procs.append(proc)
            except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
                continue

        if procs:
            logger.info(f'psutil.process_iter found {len(procs)} matching process(es).')
            return True, procs

    logger.info('No sync agent is active.')
    return False, []