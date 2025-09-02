from typing import Optional

from agptools.helpers import I

# from syncmodels.definitions import UID_TYPE

# from syncmodels.mapper import Mapper
from syncmodels.model import BaseModel, Field
from syncmodels.model.model import Datetime, GeoModel, DeviceModel

# TODO: review this file location (comfort?)


class AirPollutants(DeviceModel):

    # id: UID_TYPE = Field(
    #     description="Indicativo climatógico de la estación meteorológia",
    # )
    # TODO: use more 'normalized' names based on meta-info provided by AEMET

    # geospatial
    # geometry: Point

    CO2: Optional[float] = Field(
        None,
        description="""El dióxido de carbono es un gas inodoro, incoloro, ligeramente ácido y no inflamable""",
    )

    CO2_max: Optional[float] = Field(
        None,
        description="""Valor máximo de ióxido de carbono""",
    )

    CO2_min: Optional[float] = Field(
        None,
        description="""Valor minimo de ióxido de carbono""",
    )

    CO: Optional[float] = Field(
        None,
        description="""Gas venenoso que no tiene olor ni color. Lo emite la quema de combustible (como en el caso
        del escape de los automóviles o las chimeneas domésticas) y de productos del tabaco. El monóxido de carbono
         impide que los glóbulos rojos lleven suficiente oxígeno para que las células y los tejidos puedan vivir""",
    )

    CO_max: Optional[float] = Field(
        None,
        description="""máxima condentración de monoxido de carbono""",
    )

    CO_min: Optional[float] = Field(
        None,
        description="""minima condentración de monoxido de carbono""",
    )

    SO2: Optional[float] = Field(
        None,
        description="""Es un gas que se origina sobre todo durante la combustión de carburantes fósiles que
        contienen azufre (petróleo, combustibles sólidos), llevada a cabo sobre todo en los procesos industriales
        de alta temperatura y de generación eléctrica.
        """,
    )
    SO2_max: Optional[float] = Field(
        None,
        description="""maxima concentración de dioxido de azufre.""",
    )

    SO2_min: Optional[float] = Field(
        None,
        description="""minima concentración de dioxido de azufre.""",
    )

    NO2: Optional[float] = Field(
        None,
        description="""es un contaminante atmosférico, de origen principalmente antropogénico, cuyas fuentes
        fundamentales son el tráfico rodado, así como las emisiones de determinadas industrias y grandes instalaciones
         de combustión
    """,
    )

    NO2_max: Optional[float] = Field(
        None,
        description="""maxima concentracion de dioxido de nitrogeno""",
    )

    NO2_min: Optional[float] = Field(
        None,
        description="""minima concentracion de dioxido de nitrogeno
    """,
    )

    NOX: Optional[float] = Field(
        None,
        description="""TBD""",
    )

    NOX_max: Optional[float] = Field(
        None,
        description="""TBD""",
    )

    NOX_min: Optional[float] = Field(
        None,
        description="""TBD""",
    )

    H2S: Optional[float] = Field(
        None,
        description="""El ácido sulfhídrico (H2S) es un gas incoloro inflamable, de sabor algo dulce y olor a huevos
        podridos; en altas concentraciones puede ser venenoso. Otros nombres con los que se conoce incluyen ácido
        hidrosulfúrico, gas de alcantarilla y sulfuro de hidrógeno.
    """,
    )

    H2S_max: Optional[float] = Field(
        None,
        description="""maxima concentracion de acido sulfhidrico.
    """,
    )

    H2S_min: Optional[float] = Field(
        None,
        description="""minima concentracion de acido sulfhidrico.
        """,
    )

    NO: Optional[float] = Field(
        None,
        description="""es un gas incoloro con un olor dulce y ligeramente tóxico, con efecto anestésico y
        disociativo.2​ No es inflamable ni explosivo, pero soporta la combustión tan activamente como el oxígeno
         cuando está presente en concentraciones apropiadas con anestésicos o material inflamable. Al ser el tercer
         gas de efecto invernadero de larga duración más importante, el óxido nitroso contribuye al calentamiento
         global y es una sustancia que agota sustancialmente el ozono estratosférico
.
        """,
    )
    NO_max: Optional[float] = Field(
        None,
        description="""maxima concentracion de óxido de nitrogeno
    .
            """,
    )

    NO_min: Optional[float] = Field(
        None,
        description="""minima concentracion de óxido de nitrogeno
            """,
    )

    O3: Optional[float] = Field(  # TODO: agp: O3???
        None,
        description="""Ozono: Estado alotrópico del oxígeno, que se forma de manera natural en la atmósfera por
         las descargas eléctricas producidas durante las tormentas; es muy oxidante y se utiliza, entre otros usos,
         como índice de contaminación atmosférica. (Símbolo O
            """,
    )
    O3_max: Optional[float] = Field(
        None,
        description="""minima concentracion de ozono
            """,
    )

    O3_min: Optional[float] = Field(
        None,
        description="""minima concentracion de ozono
            """,
    )

    PM1: Optional[float] = Field(
        None,
        description="""Partículas muy pequeñas en el aire que tiene un diámetro de 1 micrómetros""",
    )
    PM1_max: Optional[float] = Field(
        None, description="""maxima concentracion de pm1"""
    )

    PM1_min: Optional[float] = Field(
        None, description="""minima concentracion de pm1"""
    )

    PM25: Optional[float] = Field(
        None,
        description="""Partículas muy pequeñas en el aire que tiene un diámetro de 2.5 micrómetros (aproximadamente
        1 diezmilésimo de pulgada) o menos de diámetro""",
    )

    PM25_max: Optional[float] = Field(
        None, description="""maxima concentracion de pm25"""
    )

    PM25_min: Optional[float] = Field(
        None, description="""minima concentracion de pm25"""
    )

    PM10: Optional[float] = Field(
        None,
        description="""Partículas muy pequeñas en el aire que tiene un diámetro de 10 micrómetros""",
    )
    PM10_max: Optional[float] = Field(
        None,
        description="""maxima concentracion de PM10""",
    )

    PM10_min: Optional[float] = Field(
        None,
        description="""minima concentracion de PM10""",
    )

    VOC: Optional[float] = Field(
        None,
        description="""Compuestos Organicos Volatiles """,
    )
    VOC_max: Optional[float] = Field(
        None,
        description="""maxima concentracion de PM10""",
    )

    VOC_min: Optional[float] = Field(
        None,
        description="""minima concentracion de PM10""",
    )


class AirPollutantsStats(DeviceModel):

    # -----------------------------------------------

    CO2_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    CO2_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    CO2_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    CO2_min_value: Optional[float] = Field(
        None,
        description="",
    )

    CO2_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------

    CO_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    CO_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    CO_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    CO_min_value: Optional[float] = Field(
        None,
        description="",
    )

    CO_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # ------------------------------------------------------

    SO2_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    SO2_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    SO2_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    SO2_min_value: Optional[float] = Field(
        None,
        description="",
    )

    SO2_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------

    NO2_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    NO2_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    NO2_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    NO2_min_value: Optional[float] = Field(
        None,
        description="",
    )

    NO2_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------

    H2S_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    H2S_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    H2S_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    H2S_min_value: Optional[float] = Field(
        None,
        description="",
    )

    H2S_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------

    NO_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    NO_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    NO_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    NO_min_value: Optional[float] = Field(
        None,
        description="",
    )

    NO_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------

    O3_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    O3_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    O3_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    O3_min_value: Optional[float] = Field(
        None,
        description="",
    )

    O3_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------

    PM1_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    PM1_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    PM1_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    PM1_min_value: Optional[float] = Field(
        None,
        description="",
    )

    PM1_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------

    PM25_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    PM25_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    PM25_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    PM25_min_value: Optional[float] = Field(
        None,
        description="",
    )

    PM25_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------

    PM10_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    PM10_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    PM10_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    PM10_min_value: Optional[float] = Field(
        None,
        description="",
    )

    PM10_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------

    VOC_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    VOC_max_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    VOC_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    VOC_min_value: Optional[float] = Field(
        None,
        description="",
    )

    VOC_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # -------------------------------------


# Warning Data Model
class AirPollutantsWarning(BaseModel):
    """
    TBD
    """

    id: str
    area_name: str = Field(
        description="Name of the Area",
        examples=["Cuenca del Genil", "Antequera", "Grazalema"],
    )
    # level
    level: Optional[str] = Field(
        None,
        description="Nivel de la alerta",
        examples=["verde", "amarilla", "naranja"],
    )
    # event
    event: Optional[str] = Field(
        None,
        description="Tipo de fenómeno o evento asociado a la alerta",
        examples=["máximas"],
    )
    # zone
    zone: str = Field(
        description="Código de la zona asociada a la aterta",
        examples=["611101"],
    )

    source: str
    sent: Datetime
    status: str
    event_type: str
    audience: str
    language: str
    category: str
    event_code: str
    event_text: str
    urgency: str
    severity: str
    certainty: str
    effective: Datetime
    onset: Datetime
    expires: Datetime
    # headline: str
    # web: str
    # contact: str
    # level: str
    # areas: List[MeteorologicalWarning]
