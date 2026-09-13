"""Log in to ITMO and fetch a schedule."""

import base64
import hashlib
import html
import json
import re
import secrets
from datetime import datetime
from urllib.parse import parse_qs, urljoin, urlsplit

import httpx

from .models import Schedule
from .parsing import parse_schedule

_PROVIDER = "https://id.itmo.ru/auth/realms/itmo"
_CALLBACK = "https://my.itmo.ru/login/callback"
_CLIENT_ID = "student-personal-cabinet"


async def _login(http: httpx.AsyncClient, username: str, password: str) -> str:
    verifier = secrets.token_urlsafe(48)
    state = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
    response = await http.get(
        f"{_PROVIDER}/protocol/openid-connect/auth",
        params={
            "client_id": _CLIENT_ID,
            "redirect_uri": _CALLBACK,
            "response_type": "code",
            "scope": "openid",
            "state": state,
            "code_challenge": challenge.decode().rstrip("="),
            "code_challenge_method": "S256",
        },
    )
    response.raise_for_status()

    match = re.search(r'"loginAction"\s*:\s*("(?:[^"\\]|\\.)*")', response.text)
    if not match:
        raise ValueError("Login form error")

    action = urljoin(str(response.url), html.unescape(json.loads(match.group(1))))

    target = urlsplit(action)
    if (target.scheme, target.netloc) != (
        "https",
        "id.itmo.ru",
    ) or not target.path.startswith("/auth/realms/itmo/"):
        raise ValueError("Wrong login destination")

    response = await http.post(
        action, data={"username": username, "password": password}
    )
    if response.status_code not in (302, 303):
        raise ValueError("Authentication error")

    callback = urlsplit(response.headers["location"])
    if (callback.scheme, callback.netloc, callback.path) != (
        "https",
        "my.itmo.ru",
        "/login/callback",
    ) or callback.fragment:
        raise ValueError("Login callback error")

    query = parse_qs(callback.query)
    if query.get("state") != [state] or len(query.get("code", [])) != 1:
        raise ValueError("Authentication error")

    response = await http.post(
        f"{_PROVIDER}/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",
            "client_id": _CLIENT_ID,
            "redirect_uri": _CALLBACK,
            "code": query["code"][0],
            "code_verifier": verifier,
        },
    )
    response.raise_for_status()

    token = response.json()["access_token"]
    if not isinstance(token, str) or not token:
        raise ValueError("Invalid access token")

    return token


async def get_schedule(
    username: str, password: str, start: datetime, end: datetime
) -> Schedule:
    """Log in and return classes in [start, end)."""
    if not username.strip() or not password:
        raise ValueError("Set ITMOM_USERNAME and ITMOM_PASSWORD")

    async with httpx.AsyncClient(timeout=15) as http:
        token = await _login(http, username, password)
        response = await http.get(
            "https://my.itmo.ru/api/schedule/schedule/personal",
            params={"date_start": start.strftime("%Y-%m-%d"), "date_end": end.strftime("%Y-%m-%d")},
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        payload = response.json()

        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")

        payload["data"] = [
            day
            for day in payload["data"]
            if start_str <= day["date"][:10] < end_str
        ]

        return (await parse_schedule(payload))
