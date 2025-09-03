"""A function for decrypting an odds portal dat file."""

# pylint: disable=too-many-locals
import base64
import binascii
import json
import logging
import urllib.parse
from typing import Any

import requests
from bs4 import BeautifulSoup
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from scrapesession.scrapesession import ScrapeSession  # type: ignore


def _find_decryption_data(
    session: ScrapeSession,
    soup: BeautifulSoup,
    referer_url: str,
    user_agent: str | None = None,
) -> tuple[bytes, bytes]:
    salt: bytes | None = None
    password: bytes | None = None
    for script in soup.find_all("script"):
        src = script.get("src")
        if src is None:
            continue
        if ("/app-" in src and src.endswith(".js")) or "/app.js" in src:
            src_url = urllib.parse.urljoin(referer_url, src)
            headers = {}
            if user_agent is not None:
                headers["User-Agent"] = user_agent
            with session.wayback_disabled():
                src_response = session.get(src_url, headers=headers)
            src_response.raise_for_status()
            variables = src_response.text
            sentinel = 'break}return e.next=9,g(r.data,"'
            variables = variables[variables.find(sentinel) + len(sentinel) :]
            variables = variables[
                : variables.find('");case 9:return s=e.sent,l=JSON.parse(s),e.abrupt')
            ]
            try:
                password_str, salt_str = variables.split('","')
            except ValueError:
                sentinel = "YupiOddsPortal"
                variables = src_response.text
                variables = variables[: variables.find(sentinel) + len(sentinel)]
                variables = '"'.join(variables.split('"')[-3:])
                password_str, salt_str = variables.split('","')
            salt = str.encode(salt_str)
            password = str.encode(password_str)
            break
    if salt is None:
        raise ValueError(f"salt is null for {referer_url}.")
    if password is None:
        raise ValueError("password is null.")
    return salt, password


def fetch_data(
    url: str,
    session: ScrapeSession,
    referer_url: str,
    soup: BeautifulSoup,
    user_agent: str | None = None,
) -> dict[str, Any]:
    """Fetch the data from the URL and decrypt it."""
    salt, password = _find_decryption_data(
        session, soup, referer_url, user_agent=user_agent
    )
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": referer_url,
    }
    if user_agent is not None:
        headers["User-Agent"] = user_agent
    response = session.get(
        url,
        headers=headers,
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        logging.error("HTTP error: %s for URL: %s", str(exc), referer_url)
        raise exc

    try:
        decoded_data = base64.b64decode(response.content).decode()
    except (UnicodeDecodeError, binascii.Error) as exc:
        logging.error("URL: %s", url)
        logging.error("Error base64 decoding payload: %s", response.content)
        raise exc
    encrypted, key = decoded_data.split(":")
    encrypted_bytes = base64.urlsafe_b64decode(encrypted)
    key_bytes = bytes.fromhex(key)
    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32,
        salt=salt,
        iterations=1000,
        backend=default_backend(),
    )
    aes_key = kdf.derive(password)
    cipher = Cipher(
        algorithms.AES(aes_key), modes.CBC(key_bytes), backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted_bytes = decryptor.update(encrypted_bytes) + decryptor.finalize()
    decrypted_data = decrypted_bytes.decode("utf-8")
    end_of_json = decrypted_data.rfind("}")
    if end_of_json != -1:
        decrypted_data = decrypted_data[: end_of_json + 1]
    return json.loads(decrypted_data)
