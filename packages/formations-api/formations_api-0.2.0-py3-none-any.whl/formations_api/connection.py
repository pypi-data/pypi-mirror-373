"""Data management instance."""

from typing import Any, Optional

from pandas import DataFrame
from requests import Session, Response

from formations_api.models import CrFormatData
from formations_api.crud.create import _save_formation, _save_reviewer_bip, _save_reviser
from formations_api.crud.read import _get_dataframe, _get_entry, _get_users, _get_approved, _get_users_bip
from formations_api.crud.update import (
    _update_cr_format,
    _update_metadata,
    _update_formation,
)
from formations_api.crud.delete import _delete_formation, _delete_reviewer_bip, _delete_reviser


class FormationsAPI:
    """Class to handle data operations using Formations API."""

    def __init__(self, url: str, headers: Optional[dict[str, str]] = None):
        """Create a FormationsAPI instance with the API URL.

        Parameters
        ==========
        url : str
            API Url.

        Returns
        =======
        FormationsAPI
            Data management interface.
        """
        self.session = Session()
        self.base_url = url
        self.headers = headers

    def __getitem__(self, cr_id: int) -> CrFormatData:
        entry = _get_entry(self.session, self.base_url, cr_id)
        return CrFormatData(**entry)

    @property
    def files(self) -> DataFrame:
        """Return all cr_format file entries."""
        return _get_dataframe(self.session, self.base_url)

    @property
    def reviser_dataframe(self) -> DataFrame:
        """Return reviser entries dataframe."""
        return _get_users(self.session, self.base_url)

    @property
    def reviewer_bip_dataframe(self) -> DataFrame:
        """Return reviewer bip entries dataframe."""
        return _get_users_bip(self.session, self.base_url)

    @property
    def approved_dataframe(self) -> DataFrame:
        """Return approved entries dataframe."""
        return _get_approved(self.session, self.base_url)

    def update_cr_format(self, data: dict[str, Any], cr_id: int) -> Response:
        """Update 6CR Format entry.

        Parameters
        ==========
        data : dict[str, Any]
            A dictionary containing the data to update. The valid (not required) keys are:
            filename [str], dir_cr_format [str], revised_metadata [bool], revised_formation_top [bool],
            validate [bool].

        cr_id : int
            CR Format entry to update ID.

        Returns
        =======
        Response
            requests.Response operation.
        """
        return _update_cr_format(self.session, self.base_url, data, cr_id, self.headers)

    def update_metadata(self, data: dict[str, Any], rev_id: int) -> Response:
        """Update Revised Data entry.

        Parameters
        ==========
        data : dict[str, Any]
            A dictionary containing the data to update. The valid (not required) keys are:
            reviser [int], wellname [str], field [str], company [str], contract [str],
            start_date [datetime.date], end_date [datetime.date], x_coor_bottom [float],
            y_coor_bottom [float], x_coor_rig [float], y_coor_rig [float], structure [str],
            revised [bool].

        rev_id : int
            Revised Data entry to update ID.

        Returns
        =======
        Response
            requests.Response operation.
        """
        return _update_metadata(self.session, self.base_url, data, rev_id, self.headers)

    def create_formation(self, data: dict[str, Any], rev_id: int) -> Response:
        """Create a Revised Formation Top entry.

        Parameters
        ==========
        data : dict[str, Any]
            A dictionary containing the data to create. The valid (not required) keys are:
            reviser [float], name [dtr], top_md [float], top_tvd [float], top_tvdss [float],
            base_md [float], base_tvd [float], base_tvdss [float], thickness_md [float],
            thickness_tvd [float], thickness_tvdss [float], revised [bool],1
            revised_data_id [int].

        rev_id : int
            Metadata associated ID.

        Returns
        =======
        Response
            requests.Response operation.
        """
        data["revised_data_id"] = rev_id
        return _save_formation(self.session, self.base_url, data, self.headers)

    def update_formation(self, data: dict[str, Any], for_id: int) -> Response:
        """Update a Revised Formation Top entry.

        Parameters
        ==========
        data : dict[str, Any]
            A dictionary containing the data to create. The valid (not required) keys are:
            reviser [float], name [dtr], top_md [float], top_tvd [float], top_tvdss [float],
            base_md [float], base_tvd [float], base_tvdss [float], thickness_md [float],
            thickness_tvd [float], thickness_tvdss [float], revised [bool],

        for_id: int
            Revised Formation Top entry to update ID.

        Returns
        =======
        Response
            requests.Response operation.
        """
        return _update_formation(self.session, self.base_url, data, for_id, self.headers)

    def delete_formation(self, for_id: int) -> Response:
        """Delete a Revised Formation Top entry.

        Parameters
        ==========
        for_id: int
            Revised Formation Top entry to delete ID.

        Returns
        =======
        Response
            requests.Response operation.
        """
        return _delete_formation(self.session, self.base_url, for_id, self.headers)

    def review_metadata(self, cr_id: int, metadata_status: bool = True) -> Response:
        """Set metadata review status.

        Parameters
        ==========
        cr_id : int
            CR Format entry to update ID.
        metadata_status : bool
            Metadata status to set. Default is True.

        Returns
        =======
        Response
            requests.Response operation.
        """
        data = {"revised_metadata": metadata_status}
        return _update_cr_format(self.session, self.base_url, data, cr_id, self.headers)

    def review_formations(self, cr_id: int, formations_status: bool = True) -> Response:
        """Set formations review status.

        Parameters
        ==========
        cr_id : int
            CR Format entry to update ID.
        formations_status : bool
            Formations status to set. Default is True.

        Returns
        =======
        Response
            requests.Response operation.
        """
        data = {"revised_formation_top": formations_status}
        return _update_cr_format(self.session, self.base_url, data, cr_id, self.headers)

    def validate_format(self, cr_id: int, validate: bool = True) -> Response:
        """Set cr_format validate status.

        Parameters
        ==========
        cr_id : int
            CR Format entry to update ID.
        validate : bool
            Validate status to set. Default is True.

        Returns
        =======
        Response
            requests.Response operation.
        """
        data = {"validate": validate}
        return _update_cr_format(self.session, self.base_url, data, cr_id, self.headers)

    def review_approved(self, cr_id: int, approved_status: bool = True) -> Response:
        """Set approved review status.

        Parameters
        ==========
        cr_id : int
            CR Format entry to update ID.
        approved_status : bool
            Approved status to set. Default is True.

        Returns
        =======
        Response
            requests.Response operation.
        """
        data = {"revised_approved": approved_status}
        return _update_cr_format(self.session, self.base_url, data, cr_id, self.headers)

    def create_reviewer_bip(self, reviewer_bip_name: str) -> Response:
        """Create a Reviewer BIP entry.

        Parameters
        ==========
        data : dict[str, Any]
            A dictionary containing the data to create. The valid (not required) keys are:
            name [str], email [str], company [str], phone [str].

        Returns
        =======
        Response
            requests.Response operation.
        """
        return _save_reviewer_bip(self.session, self.base_url, {"name": reviewer_bip_name}, self.headers)

    def delete_reviewer_bip(self, reviewer_bip_id: int) -> Response:
        """Delete a Reviewer BIP entry.

        Parameters
        ==========
        reviewer_bip_id: int
            Reviewer BIP entry to delete ID.

        Returns
        =======
        Response
            requests.Response operation.
        """
        return _delete_reviewer_bip(self.session, self.base_url, reviewer_bip_id, self.headers)

    def create_reviser(self, reviser_name: str) -> Response:
        """Create a Reviser entry.

        Parameters
        ==========
        data : dict[str, Any]
            A dictionary containing the data to create. The valid (not required) keys are:
            name [str], email [str], company [str], phone [str].

        Returns
        =======
        Response
            requests.Response operation.
        """
        return _save_reviser(self.session, self.base_url, {"name": reviser_name}, self.headers)

    def delete_reviser(self, reviser_id: int) -> Response:
        """Delete a Reviser entry.

        Parameters
        ==========
        reviser_id: int
            Reviser entry to delete ID.

        Returns
        =======
        Response
            requests.Response operation.
        """
        return _delete_reviser(self.session, self.base_url, reviser_id, self.headers)

    def approve_metadata(self, rev_id: int, approved_id: int, reviewer_bip_id: int) -> Response:
        """Set metadata approver.

        Parameters
        ==========
        rev_id : int
            Revised Data entry to update ID.
        approved_id : int
            Approved entry ID.
         reviewer_bip_id : int
            Reviewer BIP entry ID.

        Returns
        =======
        Response
            requests.Response operation.
        """
        data = {"approved_id": approved_id, "reviewer_bip_id": reviewer_bip_id}
        return _update_metadata(self.session, self.base_url, data, rev_id, self.headers)


def main():
    """Testing."""
    url = "http://127.0.0.1:3838/formations-api"
    conn = FormationsAPI(url)
    print(conn.reviser_dataframe)


if __name__ == "__main__":
    main()
