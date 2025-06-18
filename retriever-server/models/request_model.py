from pydantic import BaseModel

class RequestModel(BaseModel):
    collection_name: str
    query: str