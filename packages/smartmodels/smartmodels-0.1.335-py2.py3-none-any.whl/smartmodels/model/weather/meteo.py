from typing import Optional

from agptools.helpers import I

# from syncmodels.definitions import UID_TYPE
# from syncmodels.mapper import Mapper
from syncmodels.model import BaseModel, Field
from syncmodels.model.model import Datetime, DeviceModel


class MeteorologicalStation(DeviceModel):
    """
    MeteorologicalStation Model
    """

    # geospatial
    # geometry: Point
    altitude: Optional[float] = Field(
        None,
        description="Altitud de la estación en metros",
        gt=-1000,
        lt=4000.0,
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

    # rain
    precipitation: Optional[float] = Field(
        None,
        description="Precipitación acumulada, medida por el pluviómetro, durante "
        "los 60 minutos anteriores a la hora indicada por el período "
        "de observación 'datetime' (mm, equivalente a l/m2)",
        ge=0,
        lt=500.0,
    )
    precipitation_disdrometer: Optional[float] = Field(
        None,
        description="Precipitación acumulada, medida por el disdrómetro, durante "
        "los 60 minutos anteriores a la hora indicada por el período "
        "de observación 'datetime' (mm, equivalente a l/m2)",
        ge=0,
        lt=500.0,
    )
    # air
    air_temperature: Optional[float] = Field(
        None,
        description="Temperatura instantánea del aire correspondiente a la fecha "
        "dada por 'datetime' (grados Celsius)",
        gt=-50,
        lt=75.0,
    )
    air_temperature_max: Optional[float] = Field(
        None,
        description="Temperatura máxima del aire, valor máximo de los 60 valores "
        "instantáneos de 'air_temperature' medidos en el período de 60 minutos "
        "anteriores a la hora indicada por el período de observación "
        "'datetime' (grados Celsius)",
        gt=-50,
        lt=75.0,
    )
    air_temperature_min: Optional[float] = Field(
        None,
        description="Temperatura mínima del aire, valor mínimo de los 60 valores "
        "instantáneos de 'air_temperature' medidos en el período de 60 minutos "
        "anteriores a la hora indicada por el período de observación "
        "'datetime' (grados Celsius)",
        gt=-50,
        lt=75.0,
    )
    air_dew_point: Optional[float] = Field(
        None,
        description="Temperatura del punto de rocío calculado correspondiente a "
        "la fecha 'datetime' (grados Celsius)",
        gt=-50,
        lt=75.0,
    )
    air_humidity: Optional[float] = Field(
        None,
        description="Humedad relativa instantánea del aire correspondiente a la "
        "fecha dada por 'datetime' (%)",
        ge=0,
        lt=100.0,
    )

    # wind
    wind_speed_max: Optional[float] = Field(
        None,
        description="Velocidad máxima del viento, valor máximo del viento "
        "mantenido 3 segundos y registrado en los 60 minutos "
        "anteriores a la hora indicada por el período de observación "
        "'datetime' (m/s)",
        ge=0,
        lt=250.0,
    )
    wind_speed: Optional[float] = Field(
        None,
        description="Velocidad media del viento, media escalar de las muestras "
        "adquiridas cada 0,25 ó 1 segundo en el período de 10 minutos "
        "anterior al indicado por 'datetime' (m/s)",
        ge=0,
        lt=250.0,
    )
    wind_speed_deviation: Optional[float] = Field(
        None,
        description="Desviación estándar de las muestras adquiridas de velocidad "
        "del viento durante los 10 minutos anteriores a la fecha dada "
        "por 'datetime' (m/s)",
        ge=0,
        lt=150.0,
    )
    wind_direction: Optional[float] = Field(
        None,
        description="Dirección media del viento, en el período de 10 minutos "
        "anteriores a la fecha indicada por 'datetime' (grados)",
        ge=0,
        lt=360.0,
    )
    wind_direction_max: Optional[float] = Field(
        None,
        description="Dirección del viento máximo registrado en los 60 minutos "
        "anteriores a la hora indicada por 'datetime' (grados)",
        ge=0,
        lt=360.0,
    )
    wind_direction_deviation: Optional[float] = Field(
        None,
        description="Desviación estándar de las muestras adquiridas de la "
        "dirección del viento durante los 10 minutos anteriores a la "
        "fecha dada por 'datetime' (grados)",
        ge=0,
        lt=360.0,
    )
    wind_distance: Optional[float] = Field(
        None,
        description="Recorrido del viento durante los 60 minutos anteriores a la "
        "fecha indicada por 'datetime' (Hm)",
        ge=0,
        lt=200.0,
    )
    # wind by ultrasonic sensor
    wind_speed_max_ultrasonic: Optional[float] = Field(
        None,
        description="Velocidad máxima del viento (sensor ultrasónico), media "
        "escalar en el periódo de 10 minutos anterior al indicado por "
        "'datetime' de las muestras adquiridas cada 0,25 ó 1 segundo "
        "(m/s)",
        ge=0,
        lt=250.0,
    )
    wind_speed_average_ultrasonic: Optional[float] = Field(
        None,
        description="Velocidad máxima del viento (sensor ultrasónico), valor "
        "máximo del viento mantenido 3 segundos y registrado en los "
        "60 minutos anteriores a la hora indicada por el período de "
        "observación 'datetime' (m/s)",
        ge=0,
        lt=250.0,
    )

    wind_speed_deviation_ultrasonic: Optional[float] = Field(
        None,
        description="Desviación estándar de las muestras adquiridas de velocidad "
        "del viento durante los 10 minutos anteriores a la fecha dada "
        "por 'datetime' obtenido del sensor ultrasónico de viento "
        "instalado junto al convencional (m/s)",
        ge=0,
        lt=250.0,
    )
    wind_direction_ultrasonic: Optional[float] = Field(
        None,
        description="Dirección media del viento (sensor ultrasónico), en el "
        "período de 10 minutos anteriores a la fecha indicada por "
        "'datetime' (grados)",
    )
    wind_direction_max_ultrasonic: Optional[float] = Field(
        None,
        description="Dirección del viento máximo registrado en los 60 minutos "
        "anteriores a la hora indicada por 'datetime' por el sensor "
        "ultrasónico (grados)",
        ge=0,
        lt=250.0,
    )
    wind_direction_deviation_ultrasonic: Optional[float] = Field(
        None,
        description="Desviación estándar de las muestras adquiridas de la "
        "dirección del viento durante los 10 minutos anteriores a la "
        "fecha dada por 'datetime' obtenido del sensor ultrasónico de "
        "viento instalado junto al convencional (grados)",
        ge=0,
        lt=250.0,
    )

    # pressure
    pressure: Optional[float] = Field(
        None,
        description="Presión instantánea al nivel en el que se encuentra "
        "instalado el barómetro y correspondiente a la fecha dada por "
        "'datetime' (hPa)",
        gt=900,
        lt=1150.0,
    )
    pressure_sea: Optional[float] = Field(
        None,
        description="Valor de la presión reducido al nivel del mar para aquellas "
        "estaciones cuya altitud es igual o menor a 750 metros y "
        "correspondiente a la fecha indicada por 'datetime' (hPa)",
        gt=900,
        lt=1150.0,
    )

    # ground
    ground_temperature: Optional[float] = Field(
        None,
        description="Temperatura suelo, temperatura instantánea junto al suelo y "
        "correspondiente a los 10 minutos anteriores a la fecha dada "
        "por 'datetime' (grados Celsius)",
        gt=-25,
        lt=75.0,
    )
    ground_temperature_5: Optional[float] = Field(
        None,
        description="Temperatura subsuelo 5 cm, temperatura del subsuelo a una "
        "profundidad de 5 cm y correspondiente a los 10 minutos "
        "anteriores a la fecha dada por 'datetime' (grados Celsius)",
        gt=-25,
        lt=50.0,
    )
    ground_temperature_20: Optional[float] = Field(
        None,
        description="Temperatura subsuelo 20 cm, temperatura del subsuelo a una "
        "profundidad de 20 cm y correspondiente a los 10 minutos "
        "anteriores a la fecha dada por 'datetime' (grados Celsius)",
        gt=-25,
        lt=50.0,
    )

    # snow
    snow: Optional[float] = Field(
        None,
        description="Espesor de la capa de nieve medida en los 10 minutos "
        "anteriores a la a la fecha indicada por 'datetime' (cm)",
        ge=0,
        lt=1000.0,
    )

    # visibility
    visibility: Optional[float] = Field(
        None,
        description="Visibilidad, promedio de la medida de la visibilidad "
        "correspondiente a los 10 minutos anteriores a la fecha dada "
        "por 'datetime' (Km)",
        ge=0,
        lt=35.0,
    )
    # radiation
    insolation: Optional[float] = Field(
        None,
        description="Duración de la insolación durante los 60 minutos anteriores "
        "a la hora indicada por el período de observación 'datetime' "
        "(horas)",
        ge=0,
        lt=60.0,
    )


class MeteorologicalStationStats(DeviceModel):
    """
    MeteorologicalStationStats Model
    """

    # time
    datetime: Optional[Datetime] = Field(
        description="Fecha hora final del período de observación, se trata de "
        "datos del periodo de la hora anterior a la indicada por este "
        "campo (hora UTC)",
        # pattern=r"\d+\-\d+\-\d+T\d+:\d+:\d+",  # is already a datetime
    )

    air_humidity_average_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=0,
        lt=100.0,
    )
    air_humidity_max_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=0,
        lt=100.0,
    )
    air_humidity_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )
    air_humidity_min_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=0,
        lt=100.0,
    )
    air_humidity_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    air_temperature_average_value: Optional[float] = Field(
        None,
        description="TBD",
        gt=-50,
        lt=75.0,
    )
    air_temperature_max_value: Optional[float] = Field(
        None,
        description="Temperatura máxima del aire, valor máximo de los 60 valores "
        "instantáneos de 'air_temperature' medidos en el período de 60 minutos "
        "anteriores a la hora indicada por el período de observación "
        "'datetime' (grados Celsius)",
        gt=-50,
        lt=75.0,
    )
    air_temperature_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )
    air_temperature_min_value: Optional[float] = Field(
        None,
        description="Temperatura mínima del aire, valor mínimo de los 60 valores "
        "instantáneos de 'air_temperature' medidos en el período de 60 minutos "
        "anteriores a la hora indicada por el período de observación "
        "'datetime' (grados Celsius)",
        gt=-50,
        lt=75.0,
    )
    air_temperature_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    insolation_average_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=0,
        lt=3000.0,
    )
    insolation_max_value: Optional[float] = Field(
        None,
        description="Duración de la insolación durante los 60 minutos anteriores "
        "a la hora indicada por el período de observación 'datetime' "
        "(horas)",
        ge=0,
        lt=60.0,
    )
    insolation_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )
    insolation_min_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=0,
        lt=3000.0,
    )
    insolation_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
        ge=0,
        lt=3000.0,
    )

    # rain
    precipitation_average_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=0,
        lt=500.0,
    )
    precipitation_max_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=0,
        lt=500.0,
    )
    precipitation_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    precipitation_min_value: Optional[float] = Field(
        None,
        description="Precipitación acumulada, medida por el pluviómetro, durante "
        "los 60 minutos anteriores a la hora indicada por el período "
        "de observación 'datetime' (mm, equivalente a l/m2)",
        ge=0,
        lt=500.0,
    )

    precipitation_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # pressure
    pressure_average_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=900,
        lt=1150.0,
    )
    pressure_max_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=900,
        lt=1150.0,
    )
    pressure_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )
    pressure_min_value: Optional[float] = Field(
        None,
        description="TBD",
        gt=900,
        lt=1150.0,
    )
    pressure_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    # wind
    wind_speed_average_value: Optional[float] = Field(
        None,
        description="TBD",
    )
    wind_speed_max_value: Optional[float] = Field(
        None,
        description="Velocidad máxima del viento, valor máximo del viento "
        "mantenido 3 segundos y registrado en los 60 minutos "
        "anteriores a la hora indicada por el período de observación "
        "'datetime' (m/s)",
        ge=0,
        lt=250.0,
    )
    wind_speed_max_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
        ge=0,
        lt=250.0,
    )
    wind_speed_min_value: Optional[float] = Field(
        None,
        description="TBD",
        ge=0,
        lt=250.0,
    )
    wind_speed_min_datetime: Optional[Datetime] = Field(
        None,
        description="TBD",
    )

    wind_direction_freq_value: Optional[float] = Field(
        None,
        description="Valor cuantizado que se repite más (max historgram)",
        ge=0,
        lt=360.0,
    )


#


# Warning Data Model
class MeteorologicalWarning(BaseModel):
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
