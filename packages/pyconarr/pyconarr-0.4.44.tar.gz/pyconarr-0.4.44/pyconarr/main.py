import logging

from pyconarr.libs.config import config
from pyconarr.libs.route import app

logging.info("Starting app " + app.title)
logging.debug("Jellyfin server URL : " + config["jellyfin"]["url"])
