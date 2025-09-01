from ..http import AUTHORIZATION
from ..registry import iRegistry


class iAuthenticator(iRegistry):
    "base interface for authenticators"

    AUTH = None  #  not logged
    AUTH_KEY = AUTHORIZATION

    AUTHENTICATOR = {}

    @classmethod
    async def auth(cls, url, params, session: "iSession", **context):
        __key__ = params.get("User")
        blue, factory, args, kw = cls.get_factory(url, __klass__=cls, __key__=__key__)
        if factory:
            try:
                # adjust argument calling
                if args:
                    assert len(args) == 1
                    (_auth,) = args
                else:
                    _auth = {}
                _params = dict(params)
                _params.update(**context, **_auth, **kw)
                result = await factory._auth(url, _params, session)
                return result

            except Exception as why:  # pragma: nocover
                print(why)
        return False

    @classmethod
    async def _auth(cls, url, params, session: "iSession"):
        "resolve authentication (i.e 401/404/407 alike situations)"
        return False
