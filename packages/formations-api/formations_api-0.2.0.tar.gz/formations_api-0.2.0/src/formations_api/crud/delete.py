"""Delete data from API."""

from typing import Optional

from requests import Session, Response


def _delete_data(
    session: Session,
    base_url: str,
    endpoint: str,
    data_id: int,
    headers: Optional[dict[str, str]] = None,
) -> Response:
    if not headers:
        headers = {"accept": "application/json", "Content-Type": "application/json"}

    url = f"{base_url}/{endpoint}/{data_id}"
    response = session.delete(url, headers=headers)
    return response


def _delete_formation(
    session: Session,
    base_url: str,
    data_id: int,
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _delete_data(session, base_url, "revised_formation_top", data_id, headers)


def _delete_reviewer_bip(
    session: Session,
    base_url: str,
    data_id: int,
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _delete_data(session, base_url, "reviewer_bip", data_id, headers)


def _delete_reviser(
    session: Session,
    base_url: str,
    data_id: int,
    headers: Optional[dict[str, str]] = None,
) -> Response:
    return _delete_data(session, base_url, "reviser", data_id, headers)
