import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

from etiket_client.sync.run import run_sync_iter
from etiket_client.local.database import Session 

# run single iteration of the sync agent and report errors
if __name__ == '__main__':
    with Session() as session:
        run_sync_iter(session)