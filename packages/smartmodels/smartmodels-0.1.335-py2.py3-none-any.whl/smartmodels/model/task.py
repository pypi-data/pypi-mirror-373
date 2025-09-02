"""
This file supports Task Pattern for smartmodels
"""

from datetime import datetime, timedelta
import random
import uuid
from dateutil.parser import parse

from typing import Union, List, Tuple, Dict
from typing_extensions import Annotated


from syncmodels.model import BaseModel, field_validator, Field
from syncmodels.mapper import *

# from models.generic.price import PriceSpecification
# from models.generic.schedules import OpeningHoursSpecificationSpec

from smartmodels.definitions import UID_TYPE

from .base import *
from ..ports import *

# TODO: extend model corpus classes, a.k.a: the pydantic based thesaurus foundations classes
# TODO: this classes may be included in the main thesaurus when project is stable
# TODO: and others projects can benefit from them, making the thesaurus bigger and more powerful


# ---------------------------------------------------------
# TaskItem
# ---------------------------------------------------------
class SmartmodelsTask(Task):
    """A Smartmodels Task model"""

    pass


# ---------------------------------------------------------
# TaskRequest
# ---------------------------------------------------------
class SmartmodelsTaskRequest(Request):
    """A Smartmodels request to task manager.
    Contains all query data and search parameters.
    """

    pass


# ---------------------------------------------------------
# TaskResponse
# ---------------------------------------------------------
class SmartmodelsTaskResponse(Response):
    """A Smartmodels response to task manager.
    Contains the search results given by a request.
    """

    data: Dict[UID_TYPE, SmartmodelsTask] = {}
