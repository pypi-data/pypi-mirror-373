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
    MeteorologicalWarning,
)


class AEMETMeteorologicalStationMapper(Mapper):
    PYDANTIC = MeteorologicalStation

    id = "idema", I, None
    device_id = "idema", I, None
    device_name = "name", I, None

    # lon = "lon", FLOAT, None

    datetime = "fint", DATE, None
    level = "nivel", I, None
    event = "fenomeno|fenómeno", I, None

    # geometry is handled by AEMETObservationGeospec
    # geometry = ("lon", "lat"), GEOPOINT
    altitude = "alt", FLOAT, None

    ubication = "ubi", SAFE_STR, None

    precipitation = "prec", FLOAT, None

    air_temperature = "ta", FLOAT, None
    air_temperature_max = "tamax", FLOAT, None
    air_temperature_min = "tamin", FLOAT, None
    air_dew_point = "tpr", FLOAT, None
    air_humidity = "hr", FLOAT, None

    wind_speed_max = "vmax", FLOAT, None
    wind_speed = "vv", FLOAT, None
    wind_speed_deviation = "stdvv", FLOAT, None
    wind_direction = "dv", FLOAT, None
    wind_direction_max = "dmax", FLOAT, None
    wind_direction_deviation = "stddv", FLOAT, None

    wind_distance = "rviento", FLOAT, None

    wind_speed_max_ultrasonic = "vmaxu", FLOAT, None
    wind_speed_average_ultrasonic = "vvu", FLOAT, None
    wind_speed_deviation_ultrasonic = "stdvvu", FLOAT, None

    wind_direction_ultrasonic = "dvu", FLOAT, None
    wind_direction_max_ultrasonic = "dmaxu", FLOAT, None
    wind_direction_deviation_ultrasonic = "stddvu", FLOAT, None

    pressure = "pres", FLOAT, None
    pressure_sea = "pres_nmar", FLOAT, None

    ground_temperature = "ts", FLOAT, None
    ground_temperature_5 = "tss5cm", FLOAT, None
    ground_temperature_20 = "tss20cm", FLOAT, None

    snow = "nieve", FLOAT, None

    insolation = "UV", FLOAT, None
    visibility = "vis", FLOAT, None  # TODO: ago find out


class MeteorologicalWarningAreaMapper(Mapper):
    PYDANTIC = MeteorologicalWarning

    id = "geocode.value", I

    area_name = "areaDesc", I
    # polygon = I, I
    # area_code = "geocode.value", I


class MeteorologicalWarningDataMapper(MeteorologicalWarningAreaMapper):
    PYDANTIC = MeteorologicalWarning

    identifier = "identifier", I, None
    source = "sender", I, None
    sent = "sent", DATE, None
    status = "status", I, None
    event_type = "msgType", I, None
    audience = "scope", I, None
    language = "language", I, None
    category = "category", I, None
    event_text = "event", I, None
    urgency = "urgency", I, None
    severity = "severity", I, None
    certainty = "certainty", I, None
    effective = "effective", DATE, None
    onset = "onset", DATE, None
    expires = "expires", DATE, None
    # headline = "headline", I, None
    # web = "web", I, None
    # contact = "contact", I, None
    level = "parameter.value", I, None
    event_code = "eventCode.value", I, None
    zone = "zona", I, None
