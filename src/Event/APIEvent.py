from Model import Symbol
from botframelib.EventSourcing import IEvent
from pydantic import BaseModel


class CreateBot(IEvent):
    exchange: str
    symbol: Symbol
    range_min: int
    range_max: int
    amount_min: int
    amount_max: int
    per_min: int
    remain_time: int
    n_update: int


class StopBot(IEvent):
    pass
