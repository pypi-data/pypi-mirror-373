"""
Example of configuration preferences for smartmodels service.
"""

from datetime import datetime, timedelta
from dateutil.parser import parse

from typing import Union, List, Tuple
from typing_extensions import Annotated


from syncmodels.model import BaseModel, field_validator, Field
from syncmodels.mapper import *

# from models.generic.price import PriceSpecification
# from models.generic.schedules import OpeningHoursSpecificationSpec

# from ..ports import *

# TODO: extend model corpus classes, a.k.a: the pydantic based thesaurus foundations classes
# TODO: this classes may be included in the main thesaurus when project is stable
# TODO: and others projects can benefit from them, making the thesaurus bigger and more powerful


# ---------------------------------------------------------
# Foundations Model classes
# (maybe from global model repository)
# ---------------------------------------------------------
class SmartmodelsPreferences(BaseModel):
    """Example of Backend Preferences
    You may create your own preferences for smartmodels"""

    publish_rate: int = Field(
        240,
        description="Number of seconds between publishing stored data",
        examples=[240, 300],
    )
    publish_on_start: bool = Field(
        True,
        description="If app will publish non-flushed data when application starts",
        examples=[True, False],
    )
    publish_on_stop: bool = Field(
        True,
        description="If app may try to publish non-flushed data before application closes",
        examples=[True, False],
    )
    publish_timeout: int = Field(
        5,
        description="Number of seconds to consider the server is not responding",
        examples=[5, 8],
    )
    publish_max_traces: int = Field(
        50,
        description="Maximum number of beacon traces sent in single message",
        examples=[50, 100],
    )
