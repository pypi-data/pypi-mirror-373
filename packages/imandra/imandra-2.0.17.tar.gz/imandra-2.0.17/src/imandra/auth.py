import os
import sys
from typing import Dict, Optional


# Note: platformdirs distinguishes Darwin and Unix, but we use the Unix
# conventions on Darwin.
if sys.platform == "win32":
    from platformdirs.windows import Windows as PlatformDirs
else:
    from platformdirs.unix import Unix as PlatformDirs


class NoApiKey(Exception):
    pass


def _api_key_from_env():
    return os.environ.get("IMANDRA_API_KEY")


def _api_key_from_file(fpath):
    try:
        with open(fpath) as f:
            return f.read().strip()
    except OSError:
        return None


def _get_api_key(api_key=None) -> str:
    api_key = (
        api_key
        or _api_key_from_env()
        or _api_key_from_file(
            PlatformDirs(appname="imandra").user_config_path / "api_key"
        )
        or _api_key_from_file(
            PlatformDirs(appname="imandrax").user_config_path / "api_key"
        )
    )
    if api_key is None:
        raise NoApiKey("Please provide an API key.")
    return api_key


def _scheme_from_env():
    return os.environ.get("IMANDRA_API_SCHEME")


def _host_from_env():
    return os.environ.get("IMANDRA_API_HOST")


def _api_version_from_env():
    return os.environ.get("IMANDRA_API_VERSION")


class Config:
    def __init__(
        self,
        api_key: Optional[str] = None,
        scheme: Optional[str] = None,
        host: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self._api_key = _get_api_key(api_key)
        self._scheme = scheme or _scheme_from_env() or "https"
        self._host = host or _host_from_env() or "api.imandra.ai"
        self._api_version = api_version or _api_version_from_env() or "v1beta1"

    def get_api_key(self) -> str:
        return self._api_key

    def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    def get_url(self) -> str:
        return f"{self._scheme}://{self._host}/{self._api_version}"

    def get_organization(self, organization):
        return organization or os.environ.get("IMANDRA_ORGANIZATION")
