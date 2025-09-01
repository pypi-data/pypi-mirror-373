import re

# ---------------------------------------------------------
# Authenticator Helpers
# ---------------------------------------------------------
from agptools.logs import logger
from agptools.containers import expand_expression
import base64

import requests
from . import iAuthenticator

from ..http import (
    AUTHORIZATION,
    AUTH_USER,
    AUTH_SECRET,
    AUTH_URL,
    AUTH_KEY,
    AUTH_VALUE,
    AUTH_METHOD,
    AUTH_PAYLOAD,
    AUTH_TOKEN,
    METHOD_BASIC,
    METHOD_JSON,
    METHOD_TOKEN,
    METHOD_KEYCLOAK,
    METHOD_FORM,
    BASIC_HEADERS,
)
from ..definitions import REG_PRIVATE_KEY

log = logger(__name__)


def score(item):
    "score by counting how many uri values are not None"
    info, m = item
    sc = len(m.groups())
    return sc, info


class BasicAuthenticator(iAuthenticator):
    """"""

    @classmethod
    async def _auth(cls, url, params, session: "iSession"):
        "resolve authentication (i.e 401/404/407 alike situations)"
        session.headers.update(params)
        return True


class EndPointAuthenticator(iAuthenticator):
    """"""

    @classmethod
    async def _auth(cls, url, params, session: "iSession"):
        "resolve authentication (i.e 401/404/407 alike situations)"
        response = None
        # depending of the auth EP method ...

        auth_url = params.get(AUTH_URL, url)
        if (meth := params.get(AUTH_METHOD)) in (METHOD_BASIC, None):
            # get basic credentials
            concatenated = params[AUTH_USER] + ":" + params[AUTH_SECRET]
            encoded = base64.b64encode(concatenated.encode("utf-8"))
            headers = {
                **BASIC_HEADERS,
                # CONTENT_LENGTH: '0',
                # 'Authorization': 'Basic MkpNaWZnS0RrbTliRXB2ZjV4RWRPOFJMWlZvYTpISzU2MWZrd1U1NEIxNDhuMnFTdnJHREFYMEFh',
                AUTHORIZATION: f"Basic {encoded.decode('utf-8')}",
            }
            response = requests.post(auth_url, headers=headers, verify=True)
        elif meth in (METHOD_JSON, METHOD_KEYCLOAK):
            headers = {
                **BASIC_HEADERS,
                # CONTENT_TYPE: APPLICATION_JSON,
                # CONTENT_LENGTH: '0',
                # 'Authorization': 'Basic MkpNaWZnS0RrbTliRXB2ZjV4RWRPOFJMWlZvYTpISzU2MWZrd1U1NEIxNDhuMnFTdnJHREFYMEFh',
                # AUTHORIZATION: f"Basic {encoded.decode('utf-8')}",
            }
            #  TODO: use asyncio (faster)
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         auth_url, headers=headers, data=params[AUTH_PAYLOAD]
            #     ) as response:
            #         response_text = await response.text()
            #         print(f"Status: {response.status}")
            #         print(f"Response: {response_text}")
            response = requests.post(
                auth_url,
                headers=headers,
                data=params[AUTH_PAYLOAD],
                verify=True,
            )
        elif meth in (METHOD_TOKEN,):
            key = params.get(AUTH_KEY)
            template = params[AUTH_VALUE]
            result = {
                **params,
                "token": params.get(AUTH_TOKEN),
            }
            rendered = expand_expression(result, template)
            session.headers[key] = rendered
        elif meth in (METHOD_FORM,):
            # RMC: Autenticación con envío de datos como form-urlencoded
            headers = {
                **BASIC_HEADERS,
                "Content-Type": "application/x-www-form-urlencoded",
            }
            payload = params[AUTH_PAYLOAD]
            response = requests.post(
                auth_url,
                headers=headers,
                data=payload,  # 'data' se envía como form-urlencoded
                verify=True,
            )

        else:
            raise RuntimeError(f"Unknown method: {meth}")

        if response:
            if response.status_code in (200,):
                result = response.json()
                # expires_in = result.get("expires_in")  # secs

                key = params.get(AUTH_KEY)
                if key:
                    template = params[AUTH_VALUE]
                    #  i.e. "Bearer {access_token}"
                    # allow expressions such:
                    # "Bearer {access_token}" or
                    # "Bearer {data.access_token}"
                    rendered = expand_expression(result, template)
                    session.headers[key] = rendered
                    # session.headers[key] = template.format_map(
                    #     result
                    # )
                else:
                    session.headers.update(result)
            else:
                log.error(
                    "%s: %s: %s",
                    response.status,
                )
                result = await response.text()
                log.error(result)
                log.error("Status: %s", response.status)
                return False

        exclude = "|".join([REG_PRIVATE_KEY] + session.bot.ALLOWED_PARAMS)
        _params = {k: v for k, v in params.items() if not re.match(exclude, k)}
        session.headers.update(_params)
        return True
