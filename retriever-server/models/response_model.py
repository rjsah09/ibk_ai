from pydantic import BaseModel
from typing import List

class ResponseModel(BaseModel):
    item: str
    metadata: list[dict]
    similarity: float