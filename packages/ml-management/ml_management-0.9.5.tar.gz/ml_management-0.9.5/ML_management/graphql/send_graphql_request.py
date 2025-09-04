import locale
import posixpath
from typing import Any, Optional

import httpx
from sgqlc.operation import Operation

from ML_management.session import AuthSession
from ML_management.variables import get_server_url


def send_graphql_request(op: Operation, json_response: bool = True, timeout: Optional[int] = 60) -> Any:
    """Send request to server and process the response."""
    json_data = AuthSession().sgqlc_request(op, timeout)

    if "errors" in json_data:
        server_url = get_server_url()
        try:
            if locale.getdefaultlocale()[0][:2] == "ru":
                url_base = posixpath.join(server_url, "locales/ru/ru.json")
            else:
                url_base = posixpath.join(server_url, "locales/en/en.json")
        except Exception:
            # if there is no locale file use english by default.
            url_base = posixpath.join(server_url, "locales/en/en.json")
        translation = httpx.get(url_base).json()

        error_message = json_data["errors"][0]["message"].split(",")[0]

        try:
            message_type, message_value = error_message.split(".")
        except Exception:
            raise Exception(error_message) from None

        if message_type not in translation:
            raise Exception(message_type)

        formatted_translated_message = translation[message_type][message_value]
        if (
            ("extensions" in json_data["errors"][0])
            and ("params" in json_data["errors"][0]["extensions"][error_message])
            and (json_data["errors"][0]["extensions"][error_message]["params"] is not None)
        ):
            raise Exception(
                formatted_translated_message.format().format(
                    **json_data["errors"][0]["extensions"][error_message]["params"]
                )
            )
        raise Exception(formatted_translated_message)

    if json_response:
        return json_data["data"]
    else:
        return op + json_data
