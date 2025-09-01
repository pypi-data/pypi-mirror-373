import re

from agptools.helpers import INT

from aiohttp.client_exceptions import ContentTypeError, ClientError

# ----------------------------------------------------------
# HTTP definitions
# ----------------------------------------------------------

STATUS_OK = 200
STATUS_AUTH = 403

ACCEPT = "Accept"
ACCEPT_ENCODING = "Accept-Encoding"
ACCEPT_LANGUAGE = "Accept-Language"
CONTENT_TYPE = "Content-Type"
CONTENT_LENGTH = "Content-Length"
USER_AGENT = "User-Agent"
AUTHORIZATION = "Authorization"
AUTH_URL = "auth_url__"
AUTH_KEY = "auth_key__"
AUTH_VALUE = "auth_value__"
AUTH_USER = "auth_user__"
AUTH_SECRET = "auth_secret__"
AUTH_PAYLOAD = "auth_payload__"
AUTH_TOKEN = "auth_token__"
AUTH_METHOD = "auth_method__"
AUTH_PREAUTH = "auth_preauth__"
METHOD_BASIC = "Basic"
METHOD_JSON = "Json"
METHOD_KEYCLOAK = "KeyCloak"
METHOD_TOKEN = "Token"
METHOD_FORM = "Form"
BEARER_RENDER = "Bearer {token}"
USER_AGENT = "User-Agent"

TEXT_PLAIN = "text/plain"
TEXT_HTML = "text/html"

APPLICATION_PYTHON = "application/python"
APPLICATION_JSON = "application/json"
APPLICATION_XML = "application/xml"
APPLICATION_ZIP = "application/zip"
APPLICATION_GTAR = "application/x-gtar"
APPLICATION_MS_EXCEL = "application/vnd.ms-excel"
APPLICATION_OCTET_STREAM = "application/octet-stream"
TEXT_CSV = "text/csv"

ALL_TEXT = {TEXT_PLAIN, TEXT_HTML}
ALL_JSON = {APPLICATION_JSON}
ALL_XML = {APPLICATION_XML}
ALL_TAR = {APPLICATION_GTAR}
ALL_PYTHON = {APPLICATION_PYTHON}


PATTERNS = {
    APPLICATION_PYTHON: [APPLICATION_PYTHON],
    APPLICATION_JSON: [APPLICATION_JSON],
    TEXT_PLAIN: [TEXT_PLAIN],
    TEXT_HTML: [TEXT_HTML],
    APPLICATION_XML: [APPLICATION_XML],
    APPLICATION_ZIP: [APPLICATION_ZIP],
    APPLICATION_GTAR: [APPLICATION_GTAR],
    APPLICATION_MS_EXCEL: [
        APPLICATION_MS_EXCEL,
    ],  # TODO: agp : REVIEW
    APPLICATION_OCTET_STREAM: [APPLICATION_OCTET_STREAM],
    TEXT_CSV: [TEXT_CSV],
}

BASIC_HEADERS = {
    # USER_AGENT: 'python-requests/2.32.2',
    USER_AGENT: "Mozilla/5.0 (X11; Linux i686; rv:125.0) Gecko/20100101 Firefox/125.0",
    ACCEPT_ENCODING: "gzip, deflate",
    ACCEPT: "*/*",
}
# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------


def guess_content_type(headers):
    # TODO: 'application/json; charset=utf-8'
    # return APPLICATION_JSON
    content_type = headers.get(CONTENT_TYPE, TEXT_PLAIN).lower()

    for type_, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, content_type):
                return type_

    #  fallback
    return APPLICATION_JSON


async def extract_result(response):
    try:
        content_type = guess_content_type(response.headers)
        if content_type in ALL_JSON:
            result = await response.json()
        elif content_type in ALL_PYTHON:
            result = response.body
        elif content_type in ALL_XML:
            result = await response.text()
        else:
            result = await response.text()
    except ContentTypeError:
        if x := INT(response.headers.get(CONTENT_LENGTH, "-1")):
            if isinstance(x, int) and x > 0:
                result = await response.text()
    except ClientError:
        result = None
    except Exception:
        result = response

    return result
