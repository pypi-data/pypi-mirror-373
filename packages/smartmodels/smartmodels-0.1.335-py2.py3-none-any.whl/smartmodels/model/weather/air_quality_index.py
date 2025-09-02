from typing import Optional

from agptools.helpers import I
from syncmodels.definitions import UID_TYPE

# from syncmodels.mapper import Mapper
from syncmodels.model import BaseModel, Field
from syncmodels.model.model import Datetime, GeoModel


class AirQualityIndex(GeoModel):

    # id: UID_TYPE = Field(
    #     description="Indicativo climatógico de la estación meteorológia",
    # )
    # TODO: use more 'normalized' names based on meta-info provided by AEMET

    # geospatial
    # geometry: Point
    altitude: Optional[float] = Field(
        None,
        description="Altitud de la estación en metros",
    )

    # location
    ubication: Optional[str] = Field(
        None, description="Ubicación de la estación o Nombre de la estación"
    )

    # time
    datetime: Optional[Datetime] = Field(
        description="Fecha hora final del período de observación, se trata de "
        "datos del periodo de la hora anterior a la indicada por este "
        "campo (hora UTC)",
        # pattern=r"\d+\-\d+\-\d+T\d+:\d+:\d+",  # is already a datetime
    )

    air_quality_index: Optional[str] = Field(
        None,
        description="""Indice de calidad del aire""",
    )
