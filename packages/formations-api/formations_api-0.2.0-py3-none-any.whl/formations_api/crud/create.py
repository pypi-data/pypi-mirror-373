"""Create new data."""

import json
from datetime import date
from typing import Any, Optional

from requests import Session, Response


def _save_data(
    session: Session,
    base_url: str,
    endpoint: str,
    data: dict[str, Any],
    headers: Optional[dict[str, str]] = None,
) -> Response:
    if not headers:
        headers = {"accept": "application/json", "Content-Type": "application/json"}

    url = f"{base_url}/{endpoint}"
    for key, val in data.items():
        if isinstance(val, date):
            data[key] = val.isoformat()
    data_json = json.dumps(data)
    response = session.post(url, data_json, headers=headers)
    return response


def _save_formation(
    session: Session,
    base_url: str,
    data: dict[str, Any],
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _save_data(session, base_url, "revised_formation_top", data, headers)


def _save_reviewer_bip(
    session: Session,
    base_url: str,
    data: dict[str, Any],
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _save_data(session, base_url, "reviewer_bip", data, headers)


def _save_reviser(
    session: Session,
    base_url: str,
    data: dict[str, Any],
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _save_data(session, base_url, "reviser", data, headers)
