class AioHttpSession:
    """
    Singleton class to use the same aiohttp ClientSession for all http requests.

    Question:   Why same ClientSession ?
    Answer  :   ref : https://docs.aiohttp.org/en/stable/client_quickstart.html
                Don’t create a session per request.
                Most likely you need a session per application which performs all requests altogether.
                A session contains a connection pool inside.
                Connection reusage and keep-alives (both are on by default) may speed up total performance.
    """
    _session = None

    def __new__(cls):
        return cls._session

    @classmethod
    def set(cls, *, session):
        """
        Set the ClientSession
        """
        if cls._session is None:
            cls._session = session

    @classmethod
    async def close(cls):
        """
        Close the ClientSession
        """
        await cls._session.close()
