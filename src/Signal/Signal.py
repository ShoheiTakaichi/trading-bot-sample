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



class Signal(IWorker):

    def __init__(self):
        IWorker.__init__(self)

    def onCompactionCandle(self, event):
        print(event)

    def onUpdateExecution(self, event):
        print('tt')
        
    def onUpdateBalance(self, event):
        print(event)