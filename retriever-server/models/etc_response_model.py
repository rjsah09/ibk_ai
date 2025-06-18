from pydantic import BaseModel

class EtcResponseModel(BaseModel):
    etc_string: str
    asset_kind: str
    job_code: str