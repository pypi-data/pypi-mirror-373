"""
This file supports Inventory Pattern for smartmodels
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

from .base import *

# TODO: extend model corpus classes, a.k.a: the pydantic based thesaurus foundations classes
# TODO: this classes may be included in the main thesaurus when project is stable
# TODO: and others projects can benefit from them, making the thesaurus bigger and more powerful


# ---------------------------------------------------------
# SmartmodelsItem
# ---------------------------------------------------------
# TODO: Inherit from smartmodels.model.app (or similar)
class SmartmodelsItem(Item):
    """A Smartmodels Item model"""

    pass


# ---------------------------------------------------------
# A base SmartmodelsRequest
# ---------------------------------------------------------
class SmartmodelsRequest(Request):
    """A Smartmodels request to task manager.
    Contains all query data and search parameters.
    """

    pass


# ---------------------------------------------------------
# A base SmartmodelsResponse
# ---------------------------------------------------------
class SmartmodelsResponse(Response):
    """A Smartmodels response to task manager.
    Contains the search results given by a request.
    """

    data: Dict[UID_TYPE, Item] = {}


# ---------------------------------------------------------
# SmartmodelsApp
# ---------------------------------------------------------
# TODO: Inherit from smartmodels.model.app (or similar)
class SmartmodelsApp(Item):
    """A Smartmodels App model"""

    pass
