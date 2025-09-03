from pydantic import BaseModel
from typing import Optional, List

class PaymentConfig(BaseModel):
    type: int
    category: int
    required: bool
    key: str
    title: str
    placeholder: str
    length: Optional[int] = None
    sort: int
    titleTranslationKey: Optional[str] = None
    placeholderTranslationKey: Optional[str] = None

class PmE(BaseModel):
    id: int
    name: str
    nameCn: str
    icon: str
    config: List[PaymentConfig]