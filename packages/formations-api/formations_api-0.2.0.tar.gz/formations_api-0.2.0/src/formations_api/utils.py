"""Utilities to manage data."""

from typing import Union, List

from pandas import DataFrame
from pydantic import BaseModel


def metadata_to_df(metadata: BaseModel) -> DataFrame:
    """Display metadata parameters as DataFrame.

    Parameters
    ==========
    metadata : pydantic.BaseModel
        Metadata object.

    Returns
    =======
    DataFrame
    """

    data = metadata.model_dump()
    for key in ["date", "reviser", "revised", "formations", "cr_format_id", "id"]:
        try:
            data.pop(key)
        except KeyError:
            pass
    return DataFrame([data])


def formations_to_df(formations: Union[List[BaseModel], None]) -> DataFrame:
    """Convert the formations BaseModel to DataFrame.

    Parameters
    ==========
    formations : [pydantic.BaseModel] | None
        formations entities.

    Returns
    =======
    pandas.DataFrame
        Formations data.
    """
    if formations is None:
        raise ValueError("There aren't entries (TODO a blank table)")

    data = [formation.model_dump() for formation in formations]
    data = DataFrame(data)
    data = data.set_index("id")
    return data
