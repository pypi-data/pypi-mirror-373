from .context import iContext


class iResponse(iContext):
    "mimic http responses"

    status = 100

    def __init__(
        self,
        status=200,
        headers=None,
        links=None,
        real_url=None,
        body=None,
        **kw,
    ):
        self.status = status
        self.headers = headers or {}
        self.links = links or {}
        self.real_url = real_url
        self.body = body
        self.__dict__.update(kw)

    async def json(self):
        "return the body as json"
        return self.body
