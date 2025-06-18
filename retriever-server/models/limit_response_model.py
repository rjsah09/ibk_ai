from pydantic import BaseModel
from models.limit_item import LimitItem
from typing import List

class LimitResponseModel(BaseModel):
    limitations: List[LimitItem]