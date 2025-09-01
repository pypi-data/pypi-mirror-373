from pydantic import BaseModel


class PmE(BaseModel):
    fieldJson: list
    instantSettlePayment: bool
    mainColor: str
    mostUsed: bool
    needVerification: bool
    paymentMethod: str
    paymentMethodDescription: str
    transferSpeed: int
