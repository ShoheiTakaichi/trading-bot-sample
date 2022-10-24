from typing import Optional
from uuid import UUID

from botframelib.EventSourcing import IEvent


class BotDoOrder(IEvent):
    id_: UUID
    action: str
    wsengine_name: str
    symbol: str
    side: Optional[str]
    amount: Optional[float]
    price: Optional[float]
    timestamp: str
