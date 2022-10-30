import os
import time

import ccxws
# from API.API import API
# from Bot.Bot import Bot
from botframelib.Event import *
from botframelib.EventSourcing import *
from botframelib.Worker import *

from Signal.Signal import Signal

def main():
    bitflyer = ccxws.bitflyer(
        apiKey='', secret=''
    )
    multiplexer = Multiplexer()
    WorkerList = [
        WsReceiver(bitflyer, "bitflyer"),
        WsSender(bitflyer, "bitflyer"),
        Clock(),
        CustomClock(),
        EventLogger(),
        SOD({"bitflyer": ["FX_BTC/JPY"]}),
        TickerCompaction(),
        Signal(),
        CryptoWatch(),
        CandleStickCompaction(),
        # TradeHistory(),
    ]

    list(map(multiplexer.addWorker, WorkerList))

    multiplexer.start()
    time.sleep(1)
    multiplexer.eventStory.put(SODEvent(time=time.time()))


if __name__ == "__main__":
    main()
