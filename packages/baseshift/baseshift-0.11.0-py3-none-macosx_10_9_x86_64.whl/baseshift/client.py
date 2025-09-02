import os
import httpx
from .version import VERSION


def get_ci_info():
    """Gathers CI/CD environment variables from the environment."""
    CI_PIPELINE_ID = os.environ.get("CI_PIPELINE_ID") or os.environ.get("GITHUB_RUN_ID")
    CI_COMMIT_REF_NAME = os.environ.get("CI_COMMIT_REF_NAME") or os.environ.get(
        "GITHUB_HEAD_REF"
    )
    CI_COMMIT_SHA = os.environ.get("CI_COMMIT_SHA") or os.environ.get("GITHUB_SHA")
    CI_MERGE_REQUEST_IID = os.environ.get("CI_MERGE_REQUEST_IID", "github")
    CI_DEFAULT_BRANCH = os.environ.get("CI_DEFAULT_BRANCH") or os.environ.get(
        "GITHUB_BASE_REF"
    )
    CI_USER = os.environ.get("GITHUB_ACTOR")

    return {
        "CI_PIPELINE_ID": CI_PIPELINE_ID,
        "CI_COMMIT_REF_NAME": CI_COMMIT_REF_NAME,
        "CI_COMMIT_SHA": CI_COMMIT_SHA,
        "CI_MERGE_REQUEST_IID": CI_MERGE_REQUEST_IID,
        "CI_DEFAULT_BRANCH": CI_DEFAULT_BRANCH,
        "CI_USER": CI_USER,
    }


async def start_clone_api_async(
    dub_uuid: str, org_token: str, server: str, grace: int = None, timeout: int = None, clone_config: dict = None
):
    """Asynchronously calls the clone start API with CI/CD info."""
    json_msg = {
        "dubUuid": dub_uuid,
        "orgToken": org_token,
        "VERSION": VERSION,
        **get_ci_info(),
    }
    if grace:
        json_msg["INACTIVITY_GRACE_SECS"] = grace
    if timeout:
        json_msg["INACTIVITY_TIMEOUT_SECS"] = timeout
    if clone_config:
        json_msg["cloneConfig"] = clone_config

    async with httpx.AsyncClient() as client:
        return await client.post(
            f"{server}/api/clone/start",
            json=json_msg,
            timeout=300.0,
        )


def start_clone_api_sync(
    dub_uuid: str, org_token: str, server: str, grace: int = None, timeout: int = None, clone_config: dict = None
):
    """Synchronously calls the clone start API with CI/CD info."""
    json_msg = {
        "dubUuid": dub_uuid,
        "orgToken": org_token,
        "VERSION": VERSION,
        **get_ci_info(),
    }
    if grace:
        json_msg["INACTIVITY_GRACE_SECS"] = grace
    if timeout:
        json_msg["INACTIVITY_TIMEOUT_SECS"] = timeout
    if clone_config:
        json_msg["cloneConfig"] = clone_config

    with httpx.Client() as client:
        return client.post(
            f"{server}/api/clone/start",
            json=json_msg,
            timeout=300.0,
        )
