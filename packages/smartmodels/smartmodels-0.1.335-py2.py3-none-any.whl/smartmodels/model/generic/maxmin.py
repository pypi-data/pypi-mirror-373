from typing import Optional

from agptools.helpers import I
from syncmodels.definitions import UID_TYPE
from syncmodels.mapper import Mapper
from syncmodels.model import BaseModel, Enum, Field
from syncmodels.model.model import Datetime


# ----------------------------------------------------------
# Particle Mappers
# TODO: move Pydantic model to smart models
# TODO: mapper can be local to a project and
# TODO: can be either in this unit or
# TODO in smartmodels as well
# ----------------------------------------------------------


class MaxMinValue(BaseModel):
    id: str
    datetime: Optional[Datetime] = Field(
        description="regular datetime",
        # pattern=r"\d+\-\d+\-\d+T\d+:\d+:\d+",  # is already a datetime
    )
    max_value: Optional[float] = Field(
        description="max value",
    )
    min_value: Optional[float] = Field(
        description="min value",
    )
    max_datetime: Optional[Datetime] = Field(
        description="max datetime",
        # pattern=r"\d+\-\d+\-\d+T\d+:\d+:\d+",  # is already a datetime
    )
    min_datetime: Optional[Datetime] = Field(
        description="min datetime",
        # pattern=r"\d+\-\d+\-\d+T\d+:\d+:\d+",  # is already a datetime
    )


class MaxMinValueMapper(Mapper):
    """
    Example:
    data
    {'wave__': 1731943172323333600,
     'datetime': '2024-07-09 19:00:00+00:00',
     'geojson': {'type': 'Point',
                 'coordinates': [-4.541829792795646, 36.739438815504194]},
     'id': '9',
     'geokey': '9',
     'max_WS_value': 3.6,
     'max_WS_ts': '2024-07-09 16:59:26+00:00',
     'min_WS_value': 1.7,
     'min_WS_ts': '2024-07-09 15:06:19+00:00'}
    """

    PYDANTIC = MaxMinValue

    id = r"id|devEUI|deviceId|entity_id", I
    datetime = (r"entity_ts|ts|datetime", I)
    geojson = r"geojson|geometry", I  # TODO: specific GEOJSON() casting helper?
    wave__ = "wave_.*", I

    max_value = r"max.*value", I
    min_value = r"min.*value", I

    max_datetime = r"max.*ts", I
    min_datetime = r"min.*ts", I
