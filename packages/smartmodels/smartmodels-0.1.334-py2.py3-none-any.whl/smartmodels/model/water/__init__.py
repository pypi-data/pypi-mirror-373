from pydantic import Field, PositiveFloat
from smartmodels.model.fiware import FIWAREBase


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
        description="water presure",
        examples=[
            0.20742187,
        ],
    )
