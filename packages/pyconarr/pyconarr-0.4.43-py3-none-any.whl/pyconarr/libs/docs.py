from pydantic import BaseModel

description = """
    API for Conarr, a containerized application for managing and organizing your media collection.

    Conarr allows you to manage sonarr, radarr, prowlarr, jellyseerr from a single interface. It is designed to be run in a containerized environment, and is built using FastAPI, Vue.js, and Docker.

    It also allow you to share some features to your jellyfin server without giving admin rights to your arr apps.
"""


openapi_tags_metadata = [
    {"name": "Health", "description": "API for health and auto-test"},
    {"name": "Users", "description": "API for user interactions"},
]


class Version(BaseModel):
    version: str


class VersionList(BaseModel):
    jellyfin: Version
    conarr: Version


class Login(BaseModel):
    Username: str
    Pw: str


class JellyfinPolicy(BaseModel):
    IsAdministrator: bool


class JellyfinConfiguration(BaseModel):
    AudioLanguagePreference: str | None = None
    SubtitleLanguagePreference: str | None = None


class JellyfinUser(BaseModel):
    Name: str
    Policy: JellyfinPolicy
    Configuration: JellyfinConfiguration


class IDVector(BaseModel):
    User: JellyfinUser
