import inspect
import sys

import imandrax_api.lib as xtypes
__all__ = ["xtypes"]

from .. import auth

try:
    from imandrax_api import (  # pyright: ignore [reportMissingImports]
        Client as BaseClient,
    )
except ModuleNotFoundError as err:
    note = """
        Install imandra with the optional 'core' dependency to enable imandra.core:

            pip install 'imandra[core]>=2.0.0'
    """
    err.msg += "\n\n" + inspect.cleandoc(note)
    v = sys.version_info
    if (v.major, v.minor) < (3, 12):
        note = f"""
        Note that imandrax_api requires Python >= 3.12. You are using Python {v.major}.{v.minor}.{v.micro}.
        """
        err.msg += "\n\n" + inspect.cleandoc(note)
    raise


class Client(BaseClient):
    def __init__(self, api_key=None, scheme=None, host=None, **kwargs):
        config = auth.Config(
            api_key=api_key, scheme=scheme, host=host, api_version="internal"
        )
        kwargs["url"] = config.get_url() + "/imandrax"
        kwargs["auth_token"] = config.get_api_key()
        super().__init__(**kwargs)
