"""Save and update data."""

import json
from datetime import date
from typing import Any, Optional

from requests import Session, Response


def _update_data(
    session: Session,
    base_url: str,
    endpoint: str,
    data: dict[str, Any],
    data_id: int,
    headers: Optional[dict[str, str]] = None,
) -> Response:
    if not headers:
        headers = {"accept": "application/json", "Content-Type": "application/json"}

    url = f"{base_url}/{endpoint}/{data_id}"
    for key, val in data.items():
        if isinstance(val, date):
            data[key] = val.isoformat()
    data_json = json.dumps(data)
    response = session.patch(url, data_json, headers=headers)
    return response


def _update_cr_format(
    session: Session,
    base_url: str,
    data: dict[str, Any],
    data_id: int,
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _update_data(session, base_url, "cr_format", data, data_id, headers)


def _update_metadata(
    session: Session,
    base_url: str,
    data: dict[str, Any],
    data_id: int,
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _update_data(session, base_url, "revised_data", data, data_id, headers)


def _update_formation(
    session: Session,
    base_url: str,
    data: dict[str, Any],
    data_id: int,
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _update_data(
        session, base_url, "revised_formation_top", data, data_id, headers
    )
