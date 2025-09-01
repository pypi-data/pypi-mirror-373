__version__ = '0.2.50'

from etiket_client import logout, authenticate_with_console, restart_sync_agent, login_with_api_token
from etiket_client.settings.user_settings import user_settings

import logging
logger = logging.getLogger(__name__)
logger.info("qDrive version: {}".format(__version__))

def launch_GUI():
    from etiket_client.GUI.sync.app import launch_GUI as l_GUI
    l_GUI()

from qdrive.dataset.dataset import dataset
from qdrive.measurement.measurement import Measurement