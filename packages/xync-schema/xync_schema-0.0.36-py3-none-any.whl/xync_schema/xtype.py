from datetime import datetime
from pydantic import BaseModel, model_validator

from xync_schema.enums import AdStatus, OrderStatus
from xync_schema import models


class UnitEx(BaseModel):
    exid: int | str
    ticker: str
    scale: int = None
    rate: float | None = None


class CoinEx(UnitEx):
    p2p: bool = None
    minimum: float | None = None


class CurEx(UnitEx):
    scale: int | None = None
    minimum: int | None = None


class PmExBank(BaseModel):
    # id: int | None = None
    exid: str
    name: str


class BaseAd(BaseModel):
    price: float
    id: int | str = None


class BaseAdIn(BaseAd):
    min_fiat: float
    amount: float
    quantity: float
    max_fiat: float
    direction_id: int
    detail: str | None = None
    auto_msg: str | None = None
    status: AdStatus = AdStatus.active
    maker_id: int = None
    _unq = "exid", "maker_id", "direction_id"

    @model_validator(mode="after")
    def check_a_or_b(self):
        if not self.amount and not self.quantity:
            raise ValueError("either amount or quantity is required")
        return self


class AdBuyIn(BaseAdIn):
    pmexs_: list[models.PmEx]

    class Config:
        arbitrary_types_allowed = True


class AdSaleIn(BaseAdIn):
    credexs_: list[models.CredEx]

    class Config:
        arbitrary_types_allowed = True


class OrderIn(BaseModel):
    exid: int
    amount: float
    created_at: datetime
    ad: models.Ad
    cred: models.Cred
    taker: models.Actor
    id: int = None
    maker_topic: int | None = None
    taker_topic: int | None = None
    status: OrderStatus = OrderStatus.created
    payed_at: datetime | None = None
    confirmed_at: datetime | None = None
    appealed_at: datetime | None = None
    _unq = "id", "exid", "amount", "maker_topic", "taker_topic", "ad", "cred", "taker"

    class Config:
        arbitrary_types_allowed = True
