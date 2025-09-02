from agptools.helpers import (
    I,
    DATE,
    FLOAT,
    SAFE_STR,
)

from syncmodels.mapper import Mapper

from ...model.weather.air_quality_index import AirQualityIndex


class AirQualityIndexMapper(Mapper):
    """Identity, no mapping needed"""

    PYDANTIC = AirQualityIndex
