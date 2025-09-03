import inspect


def session():
    try:
        from .session import HttpInstanceSession
    except ModuleNotFoundError as err:
        note = """
            Install imandra with the optional 'http_api_client' dependency to enable imandra.session():

                pip install 'imandra[http_api_client]'
        """
        err.msg += "\n\n" + inspect.cleandoc(note)
        raise
    return HttpInstanceSession()
