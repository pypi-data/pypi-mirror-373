"""Models to create data instances."""

import datetime
from typing import List, Optional

from pandas import concat
from pydantic import BaseModel

from formations_api.utils import formations_to_df, metadata_to_df


class Approved(BaseModel):
    value: str
    id: Optional[int] = None


class Reviser(BaseModel):
    name: str
    id: Optional[int] = None


class ReviewerBip(BaseModel):
    name: str
    id: Optional[int] = None


class CrFormat(BaseModel):
    filename: str
    dir_cr_format: str
    revised_metadata: Optional[bool] = None
    revised_formation_top: Optional[bool] = None
    validated: Optional[bool] = None
    revised_approved: Optional[bool] = None
    id: Optional[int] = None


class RawData(BaseModel):
    wellname: Optional[str] = None
    uwi: Optional[str] = None
    lahee_classification: Optional[str] = None
    md: Optional[str] = None
    units_md: Optional[str] = None
    tvd: Optional[str] = None
    units_tvd: Optional[str] = None
    field: Optional[str] = None
    company: Optional[str] = None
    contract: Optional[str] = None
    target_formation: Optional[str] = None
    final_well_status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    coor_syst: Optional[str] = None
    coor_orig: Optional[str] = None
    x_coor_bottom: Optional[str] = None
    y_coor_bottom: Optional[str] = None
    x_coor_rig: Optional[str] = None
    y_coor_rig: Optional[str] = None
    structure: Optional[str] = None
    rotatory_table: Optional[str] = None
    units_rotatory: Optional[str] = None
    ground_elv: Optional[str] = None
    units_ground: Optional[str] = None
    units_formations: Optional[str] = None
    approved_id: Optional[int] = None
    cr_format_id: Optional[int] = None
    id: Optional[int] = None


class RevisedData(BaseModel):
    date: Optional[datetime.datetime] = None
    reviser_id: Optional[int] = None
    wellname: Optional[str] = None
    uwi: Optional[str] = None
    lahee_classification: Optional[str] = None
    md: Optional[float] = None
    units_md: Optional[str] = None
    tvd: Optional[float] = None
    units_tvd: Optional[str] = None
    field: Optional[str] = None
    company: Optional[str] = None
    contract: Optional[str] = None
    target_formation: Optional[str] = None
    final_well_status: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    coor_syst: Optional[str] = None
    coor_orig: Optional[str] = None
    x_coor_bottom: Optional[float] = None
    y_coor_bottom: Optional[float] = None
    x_coor_rig: Optional[float] = None
    y_coor_rig: Optional[float] = None
    structure: Optional[str] = None
    rotatory_table: Optional[float] = None
    units_rotatory: Optional[str] = None
    ground_elv: Optional[float] = None
    units_ground: Optional[str] = None
    units_formations: Optional[str] = None
    approved_id: Optional[int] = None
    reviewer_bip_id: Optional[int] = None
    cr_format_id: Optional[int] = None
    id: Optional[int] = None


class FormationTop(BaseModel):
    name: Optional[str] = None
    top_md: Optional[str] = None
    top_tvd: Optional[str] = None
    top_tvdss: Optional[str] = None
    base_md: Optional[str] = None
    base_tvd: Optional[str] = None
    base_tvdss: Optional[str] = None
    thickness_md: Optional[str] = None
    thickness_tvd: Optional[str] = None
    thickness_tvdss: Optional[str] = None
    raw_data_id: Optional[int] = None
    id: Optional[int] = None


class RevisedFormationTop(BaseModel):
    date: Optional[datetime.datetime] = None
    reviser_id: Optional[int] = None
    name: Optional[str] = None
    top_md: Optional[float] = None
    top_tvd: Optional[float] = None
    top_tvdss: Optional[float] = None
    base_md: Optional[float] = None
    base_tvd: Optional[float] = None
    base_tvdss: Optional[float] = None
    thickness_md: Optional[float] = None
    thickness_tvd: Optional[float] = None
    thickness_tvdss: Optional[float] = None
    revised: Optional[bool] = None
    revised_data_id: Optional[int] = None
    id: Optional[int] = None


class RawDataFormations(RawData):
    formations: Optional[List[FormationTop]] = None

    @property
    def df(self):
        return metadata_to_df(self)

    @property
    def formations_df(self):
        return formations_to_df(self.formations)  # type: ignore


class RevisedDataFormation(RevisedData):
    formations: Optional[List[RevisedFormationTop]] = None

    @property
    def df(self):
        return metadata_to_df(self)

    @property
    def formations_df(self):
        return formations_to_df(self.formations)  # type: ignore


class CrFormatData(CrFormat):
    raw_data: RawDataFormations
    revised_data: RevisedDataFormation

    @property
    def metadata_df(self):
        raw = self.raw_data.df
        rev = self.revised_data.df
        data = concat([raw, rev], ignore_index=True).T.reset_index()

        return data.rename(columns={"index": self.filename, 0: "Original", 1: "Changes"})
