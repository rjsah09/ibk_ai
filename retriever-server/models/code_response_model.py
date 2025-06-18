from pydantic import BaseModel

class CodeResponseModel(BaseModel):
    code: str