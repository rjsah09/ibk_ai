from pydantic import BaseModel

class LimitItem(BaseModel):
    item: str
    limit_code: str
    limit_name: str
    similarity: float