from agptools.helpers import (
    I,
    DATE,
    FLOAT,
    SAFE_STR,
)

from syncmodels.mapper import Mapper

from ...model.weather.meteo import (
    MeteorologicalStation,
    MeteorologicalStationStats,
    MeteorologicalWarning,
)


class MeteorologicalStationStatsMapper(Mapper):
    """Identity, no mapping needed"""

    PYDANTIC = MeteorologicalStationStats


class MeteorologicalStationMapper(Mapper):
    """Identity, no mapping needed"""

    PYDANTIC = MeteorologicalStation
