# tokens
# TODO: split into several files as the number of tokens grow

from enum import Enum


class StrEnum(str, Enum):
    """Enum where members are also (and must be) str"""


class NAMESPACES(StrEnum):
    COMFORT = "comfort"
    CONSUMPTION = "consumption"
    CONTACT = "contact"
    ENERGY = "energy"  # is consumption?
    INFRASTRUCTURE = "infrastructure"
    RADIATION = "radiation"  # is a TYPE?
    SOCIAL_MEDIA = "social_media"
    TRACKING = "tracking"
    TRAFFIC = "traffic"
    WARNINGS = "warning"
    WASTE = "waste"
    WATERING = "watering"  # is a TYPE?
    WEATHER = "weather"


class TYPES(StrEnum):
    AIR = "air"
    BUILDING = "building"
    CONTAINER = "container"
    CONTENT = "content"
    EARTHQUAKE = "earthquake"
    ELECTRICITY = "electricity"
    ELECTROMAGNETIC = "electromagnetic"
    FLOOD = "flood"
    LIGHTHING = "lighting"
    METEOROLOGICAL = "meteorological"
    NOISE = "noise"
    OCCUPANCY = "occupancy"
    PERSON = "people"
    POLLUTANTS = "pollutants"
    SOLAR = "solar"
    STRUCTURE = "structure"
    WATER = "water"
    XYLOPHAGES = "xylophages"
    ANALYTICS = "analytics"
    DATA = "data"
    METRICS = "metrics"


class LOCATION(StrEnum):
    ANY = "any"
    BUILDING = "building"
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    PARKING = "parking"


class METHOD(StrEnum):
    CAMARA = "camara"
    IRRIGATION = "irrigation"
    MOBILE = "mobile"
    RSSI = "rssi"


class ASPECT(StrEnum):
    ANALYTICS = "analytics"
    CAMPAIGN = "campaign"
    COMMENT = "comment"
    EMAIL = "email"
    GENERAL = "general"
    INFO = "info"
    POST = "post"
    QUALITY = "quality"
    STORY = "story"
    SURVEY = "survey"
    TICKETING = "ticketing"
    VIDEO = "video"
    CLASSIFICATION = "clasificacion"


class APPLICATION(StrEnum):
    BOOKING = "booking"
    COMMONS = "commons"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    ODOO = "odoo"
    TIKTOK = "tiktok"
    TRIPADVISOR = "tripadvisor"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
