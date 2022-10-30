from typing import Optional
from uuid import UUID

from botframelib.EventSourcing import IEvent


class BuySignal(IEvent):
    timestamp: str

class SellSignal(IEvent):
    timestamp: str