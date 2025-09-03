from typing import Optional
from pydantic import BaseModel

class PmE(BaseModel):
    id: Optional[int] = None
    payMethodId: str = ""
    payAccount: Optional[str] = None
    payBank: Optional[str] = None
    paySubBank: Optional[str] = None
    payType: Optional[str] = None
    identifier: str
    iconUrlColor: str
    tradeMethodName: str
    tradeMethodShortName: Optional[str] = None
    tradeMethodBgColor: str