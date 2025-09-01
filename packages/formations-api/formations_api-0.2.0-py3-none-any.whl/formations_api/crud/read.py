"""Private operations for connection instance."""

from typing import Any, Optional

from pandas import DataFrame
from requests import Session


def _get_data(
    session: Session,
    base_url: str,
    endpoint: str,
    data_id: Optional[int] = None,
):
    """General method to fetch data from API.

    Parameters
    ==========
    session : requests.Session
        Connection session to fetch data.
    base_url : str
        API url.
    endpoint : str
        Direction to fetch data.
    data_id : int, Optional
        If defined, add id parameter to query.

    Returns
    =======
    dict
        Query response in JSON object.
    """
    url = f"{base_url}/{endpoint}"
    if data_id:
        url += f"/{data_id}"
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def _get_entry(session: Session, base_url: str, cr_id: int) -> dict[str, Any]:
    """Get an entry from cr_format."""
    return _get_data(session, base_url, "cr_format", cr_id)


# def _check_metadata_status(entry: dict) -> Literal[True, False, None]:
#     """Private function to check if metadata was validate."""
#     return entry["revised_data"]["revised"]


# def _check_formations_status(entry: dict) -> bool:
#     """Private function to check if formations were validate."""
#     formations = entry["revised_data"]["formations"]
#     status = [formation["revised"] for formation in formations]
#     return all(status)


# def _check_revised_variables(
#     session: Session, base_url: str, cr_id: int
# ) -> tuple[Literal[True, False, None], bool]:
#     """Private method to check both variables at once."""
#     entry = _get_entry(session, base_url, cr_id)
#     metadata_status = _check_metadata_status(entry)
#     formations_status = _check_formations_status(entry)

#     return metadata_status, formations_status


def _get_cr_format_table(session: Session, base_url: str, table_index: bool = True) -> DataFrame:
    """Private function to fetch cr_format entries."""
    data = _get_data(session, base_url, "cr_format")
    data = DataFrame(data)
    if table_index:
        data = data.set_index("id")
    return data


def _get_dataframe(session: Session, base_url: str) -> DataFrame:
    """private method to get the dataframe with all the data calculated."""
    df = _get_cr_format_table(session, base_url)
    columns = [
        "filename",
        "dir_cr_format",
        "revised_metadata",
        "revised_formation_top",
        "validated",
    ]
    return df[columns]


def _get_users(session: Session, base_url: str) -> DataFrame:
    entries = _get_data(session, base_url, "reviser")
    df = DataFrame(entries)
    df = df.set_index("id")

    return df


def _get_users_bip(session: Session, base_url: str) -> DataFrame:
    entries = _get_data(session, base_url, "reviewer_bip")
    df = DataFrame(entries)
    df = df.set_index("id")

    return df


def _get_approved(session: Session, base_url: str) -> DataFrame:
    entries = _get_data(session, base_url, "approved")
    df = DataFrame(entries)
    df = df.set_index("id")

    return df
