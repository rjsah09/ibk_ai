from pydantic import BaseModel

class CodeResponseModel(BaseModel):
    code_string: str
    code: str
    similarity: float