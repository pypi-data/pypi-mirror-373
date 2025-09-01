from typing import List
from pydantic import BaseModel, Field, PositiveFloat


class FIWAREBase(BaseModel):
    """
    Note: from centesimal we have these data
    {
    'ts': 1712818589000,
    'entity_location': [0.0, 0.0],
    'battery_voltage': 3.5626464,
    'contador': 1579.647,
    'deviceName': 'water_consumption_01',
    'entity_ts': 1712818589000,
    'wave_uid': 'f035b0f0a0114c3d46a7f4f68c5b1f3744d909d9',
    'pressure': 0.20742187,
    'entity_id': 'f035b0f0a0114c3d46a7f4f68c5b1f3744d909d9',
    'entity_type': 'WaterConsumption',
    'validity_ts': None,
    'measurement': 'MAL023',
    'fiware_service': 'fs_ccoc',
    'fiware_servicepath': '/system12_test',
    'battery_consumption': 9424.0
    }
    """

    id: str

    entity_ts: int = Field(
        description="The timestamp of the water consumption reading as an ISO8601 string",
        examples=[1715806383000],
    )
    entity_location: List[float | float] = Field(
        [0, 0],
        description="Entity Location",
    )
    entity_id: str = Field(
        description="Id fo the entity",
    )
    entity_type: str = Field(
        description="Type fo the entity",
    )
    validity_ts: int | None = Field(
        None,
        description="TBD",  # TODO: determine meaning of this field
    )
    fiware_service: str = Field(
        description="fiware_service",
        examples=["fs_ccoc"],
    )
    fiware_servicepath: str = Field(
        description="fiware_servicepath",
        examples=["/centesimal/system12"],
    )

    name: str = Field(
        "",
        description="The name of the entity",
        examples=["water_consumption_01"],
    )


class WaterConsumptionData(FIWAREBase):

    # TODO: review this field (ubication?)
    measurement: str = Field(
        description="The building the measurement belongs to",
        examples=["MAL168"],
    )

    counter: PositiveFloat = Field(
        description="The cumulative water consumption in a given moment of time",
        examples=[49994861.7],
    )
    pressure: PositiveFloat = Field(
        description="water pressure",
        examples=[
            0.20742187,
        ],
    )
