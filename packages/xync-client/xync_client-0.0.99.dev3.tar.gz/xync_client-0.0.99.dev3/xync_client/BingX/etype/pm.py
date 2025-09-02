from pydantic import BaseModel

class PmE(BaseModel):
    id: int
    name: str
    mainColor: str
    icon: str
    number: int