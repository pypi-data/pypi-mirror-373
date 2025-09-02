from syncmodels.mapper import Mapper

from ..model.weather.pollutants import AirPollutants, AirPollutantsStats


# TODO: review this file location (comfort?)


class AirPollutantsMapper(Mapper):
    """Identity, no mapping needed"""

    PYDANTIC = AirPollutants


class AirPollutantsStatsMapper(Mapper):
    """Identity, no mapping needed"""

    PYDANTIC = AirPollutantsStats
