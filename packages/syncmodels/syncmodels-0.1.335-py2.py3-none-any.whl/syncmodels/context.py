# ---------------------------------------------------------
# Session Accessor Helper
# ---------------------------------------------------------
class iContext:
    "a context manager"

    def __enter__(self, *args, **kw):
        return self

    async def __aenter__(self, *args, **kw):
        return self.__enter__(*args, **kw)

    def __exit__(self, *exc):
        pass

    async def __aexit__(self, *exc):
        return self.__exit__(*exc)
