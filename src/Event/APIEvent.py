from Model import Symbol
from botframelib.EventSourcing import IEvent
from pydantic import BaseModel

class StopBot(IEvent):
    pass
