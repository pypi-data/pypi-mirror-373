import json
import logging
import os

import requests
from fastapi import FastAPI, HTTPException
from pyconarr.libs.config import config, get_version
from pyconarr.libs.docs import (
    IDVector,
    Login,
    VersionList,
    description,
    openapi_tags_metadata,
)
from pyconarr.libs.jellyfin import valid_user

my_version = get_version()

logging.info(
    "Pyconarr starting in version " + my_version + " in directory " + os.getcwd()
)

app = FastAPI(
    title="Pyconarr",
    description=description,
    summary="Conarr API",
    version=my_version,
    openapi_tags=openapi_tags_metadata,
    license_info={
        "name": "GPL v3",
        "identifier": "GPL-3.0-or-later",
    },
)


@app.get("/", tags=["Health"])
@app.get("/version", tags=["Health"])
async def show_version() -> VersionList:

    r = requests.get(
        config["jellyfin"]["url"] + "/System/Info/Public",
        timeout=5,
    )
    result = {
        "jellyfin": {"version": r.json()["Version"]},
        "conarr": {"version": my_version},
    }
    return VersionList(**result)


@app.post("/v1/login", tags=["Users"])
async def v1_login(login: Login) -> IDVector:
    logging.debug("Connection of user : " + str(login.Username))

    payload = {"Username": login.Username, "Pw": login.Pw}
    headers = {
        "Content-Type": "application/json",
        "x-emby-authorization": 'MediaBrowser , Client="Conarr", Device="Pyconarr", DeviceId="Conarr", Version="'
        + my_version
        + '"',
    }
    try:
        r = requests.post(
            config["jellyfin"]["url"] + "/Users/AuthenticateByName",
            data=json.dumps(payload),
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.ReadTimeout:
        raise HTTPException(status_code=502, detail="Failed to contact jellyfin server")

    if r.status_code != 200:
        if r.status_code == 401:
            logging.error("failed to authenticate user : " + login.Username)
            if valid_user(login):
                logging.error("user is valid but failed to authenticate")
            else:
                logging.error("user is invalid")
            raise HTTPException(status_code=r.status_code, detail="Login failed")
        else:
            logging.fatal("failed to contact jellyfin server")
            raise HTTPException(
                status_code=502, detail="Failed to contact jellyfin server"
            )

    return r.json()
