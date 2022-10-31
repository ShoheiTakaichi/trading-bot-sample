from datetime import datetime
import time
import uuid
import random
from typing import Optional, Tuple
import talib

import numpy as np
from ccxws.models import quote
from Event import *
from loguru import logger
from Model import Side, Symbol
from botframelib.Event import *
from botframelib.EventSourcing import IWorker



class Signal(IWorker):

    def __init__(self):
        IWorker.__init__(self)
        self.compactionCandle5min = []
        self.isFilled = False
        self.signal = 'nutrial'

    def onCompactionCandle5min(self, event):
        ohlcv = [event.time, event.open, event.high, event.low, event.close, 0,event.volume]
        logger.info(ohlcv)
        if len(self.compactionCandle5min) == 0:
            self.compactionCandle5min.append(ohlcv)
        if event.time - self.compactionCandle5min[-1][0] == 300:
            self.compactionCandle5min.append(ohlcv)
        elif event.time - self.compactionCandle5min[-1][0] > 300:
            self.isFilled = False
        else:
            logger.error('conflict on candle stick')
        df = pd.DataFrame(self.compactionCandle5min, columns=['timestamp','open','high','low','close','amount','volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
        logger.info(f"{df.drop('amount',1)}")

    def onCryptoWatch5min(self, event):
        if self.isFilled:
            return
        for o in event.ohlcv:
            o[0] -= 300
        self.compactionCandle5min = event.ohlcv
        self.isFilled = True
        df = pd.DataFrame(self.compactionCandle5min, columns=['timestamp','open','high','low','close','amount','volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
        logger.info(f"{df.drop('amount',1)}")
    
    def onEveryMinute(self, event):
        if not self.isFilled:
            self.eventStory.put(CryptoWatchEvent(exchange='bitflyer', symbol='FX_BTC/JPY'))