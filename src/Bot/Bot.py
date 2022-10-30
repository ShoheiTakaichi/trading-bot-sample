from datetime import datetime
import time
import uuid
import random
from typing import Optional, Tuple

import numpy as np
from ccxws.models import quote
from Event import *
from loguru import logger
from Model import Side, Symbol
from botframelib.Event import *
from botframelib.EventSourcing import IWorker


now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Bot(IWorker):
    """
    flow
    1. listen signal
    2. create position and set time out
    3.
       a, if oposite signal comes, doten
       b, if time out, clear position

    creating position
    1. create position in n times
    """

    def __init__(self):
        IWorker.__init__(self)
        self.exchange: Optional[str] = None
        self.symbol: Optional[Symbol] = None
        self.orderQueue: dict[uuid.UUID, list[Tuple]] = {}zzzZ
        self.balance = {}
        self.orderbook = {}
        self.bestask = {}
        self.bestbid = {}
        self.is_working = False
        self.precision = {
            "bitfinex": 0.00001,
        }

    def onBuySignal(self, event: BuySignal):
        # self.eventStory.put(SetTimer(uuid.uuid4(), 1))
        return

    def onSellSignal(self, event: SellSignal):
        return
    
    def onTimer(self, event: Timer):
        return
        
    def onUpdateBalance(self, event: UpdateBalance):
        return
    
    def onUpdateOrderBook(self, event: UpdateOrderBook):
        try:
            self.orderbook = event.orderbook
            if len(self.orderbook.asks):
                self.bestask[self.orderbook.exchange] = min(self.orderbook.asks)
            if len(self.orderbook.bids):
                self.bestbid[self.orderbook.exchange] = max(self.orderbook.bids)
        except Exception as e:
            print("bot sort error")
            print(e, e.args)