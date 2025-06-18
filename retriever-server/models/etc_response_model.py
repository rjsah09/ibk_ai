from pydantic import BaseModel

class EtcResponseModel(BaseModel):
    asset_kind: str
    job_code: str