import logging

import requests
from fastapi import HTTPException
from pyconarr.libs.config import config, get_version
from pyconarr.libs.docs import Login


def valid_user(login: Login) -> bool:
    headers = {
        "Content-Type": "application/json",
        "x-emby-authorization": 'MediaBrowser , Client="Conarr", Device="Pyconarr", DeviceId="Conarr", Version="'
        + get_version()
        + '", Token="'
        + config["jellyfin"]["admin_token"]
        + '"',
    }
    try:
        r = requests.get(
            config["jellyfin"]["url"] + "/Users",
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.ReadTimeout:
        raise HTTPException(status_code=502, detail="Failed to contact jellyfin server")
    if r.status_code == 200:
        list_users = r.json()
        if any(login.Username == user["Name"] for user in list_users):
            return True
        else:
            return False
    else:
        logging.error(str(r.status_code) + " " + r.text)
        raise HTTPException(status_code=502, detail="Failed to contact jellyfin server")
