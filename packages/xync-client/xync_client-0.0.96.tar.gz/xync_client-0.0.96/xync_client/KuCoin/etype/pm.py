from pydantic import BaseModel


class PmE(BaseModel):
    legal: str
    payTypeId: str
    payTypeCode: str
    payTypeName: str