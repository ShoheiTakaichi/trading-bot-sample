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
    全体の流れ
    1. Clientからリクエストがくる
    2. このBOTが稼働状態になる
    3. 00秒に以下が`per_min`*(BUY,SELL)分実行される
        - create, edit(複数回), cancelの注文をキューに入れる
        - それらを呼び出すためのCutomIntervalを作成する
    4. CustomIntervalが呼ばれるたびにキューが一つずつ実行される
    5. 最後のcancelが呼ばれたときにCustomIntervalを止める
    """

    def __init__(self):
        IWorker.__init__(self)
        self.exchange: Optional[str] = None
        self.symbol: Optional[Symbol] = None
        self.orderQueue: dict[uuid.UUID, list[Tuple]] = {}
        self.balance = {}
        self.orderbook = {}
        self.bestask = {}
        self.bestbid = {}
        self.is_working = False
        self.precision = {
            "bitfinex": 0.00001,
        }

    def onCreateBot(self, event: CreateBot):
        """
        Botを開始する関数。
        稼働してるBotがない時に呼び出されることを想定。
        """
        if self.is_working:
            logger.warning(
                "you should 'Stop' the bot that is running now before you 'Start'."
            )
            return

        self.is_working = True
        self.exchange = event.exchange
        self.symbol = event.symbol
        self.range_min = event.range_min
        self.range_max = event.range_max
        self.amount_min = event.amount_min
        self.amount_max = event.amount_max
        self.per_min = event.per_min
        self.remain_time = event.remain_time
        self.n_update = event.n_update

    def onStopBot(self, event: StopBot):
        """
        Botを停止する関数。
        稼働してるBotがある時に呼び出されることを想定。
        """
        if not self.is_working:
            logger.warning("you should run 'Start' first.")
            return
        self.is_working = False

    def onEveryMinute(self, event: EveryMinute):
        if not self.is_working:
            return

        # ex) if k=4, then [5, 21, 37, 57]
        rand_secs = sorted(random.sample(range(5, 59), k=self.per_min))

        for rand_sec in rand_secs:
            self._CreateEditCancelOneBot(Side.BUY, rand_sec)
            self._CreateEditCancelOneBot(Side.SELL, rand_sec)

    def onCustomInterval(self, event: CustomInterval):
        if len(self.orderQueue[event.id]) == 0:
            return

        order_event, hist_event = self.orderQueue[event.id].pop(0)
        self.eventStory.put(order_event)
        self.eventStory.put(hist_event)

    def onUpdateOrderBook(self, event: UpdateOrderBook):
        try:
            self.orderbook = event.orderbook
            if len(self.orderbook.asks):
                self.bestask[self.orderbook.exchange] = min(self.orderbook.asks)
            if len(self.orderbook.bids):
                self.bestbid[self.orderbook.exchange] = max(self.orderbook.bids)
        except Exception as e:
            print("gip sort error")
            print(e, e.args)

    def onCancelOrder(self, event: CancelOrder):
        """1Botを最後cancelするときにCustomIntervalをストップする。"""
        self.eventStory.put(StopCustomInterval(id=event.id_))

    def _CreateEditCancelOneBot(self, side: Side, start_sec: int):
        """一つのbotのcreateから複数回のedit、cancelまでを担うメソッド。
        この一つ一つにidを発行して管理する。
        create->edit(複数回)->cancelの注文をorderQueueに予約して最後にcustomIntervalを作成する。
        """
        id_ = uuid.uuid4()

        quote_ = self._GenerateRandomOrder(side)
        # create
        order_queue: list[Tuple] = []
        order_queue.append((
            CreateLimitOrder(
                id_=id_,
                wsengine_name=self.exchange,
                symbol=self.symbol.to_str(),
                amount=quote_.amount,
                price=quote_.price,
                side=side.value,
            ),
            BotDoOrder(
                id_=id_,
                action="create",
                wsengine_name=self.exchange,
                symbol=self.symbol.to_str(),
                amount=quote_.amount,
                price=quote_.price,
                side=side.value,
                timestamp=now,
            )
        ))

        # edit
        for _ in range(self.n_update):
            quote_ = self._GenerateRandomOrder(side)
            order_queue.append((
                EditOrder(
                    id_=id_,
                    wsengine_name=self.exchange,
                    symbol=self.symbol.to_str(),
                    amount=quote_.amount,
                    price=quote_.price,
                    side=side.value,
                ),
                BotDoOrder(
                    id_=id_,
                    action="edit",
                    wsengine_name=self.exchange,
                    symbol=self.symbol.to_str(),
                    amount=quote_.amount,
                    price=quote_.price,
                    side=side.value,
                    timestamp=now,
                )
            ))

        # cancel
        order_queue.append((
            CancelOrder(
                id_=id_,
                wsengine_name=self.exchange,
                symbol=self.symbol.to_str(),
            ),
            BotDoOrder(
                id_=id_,
                action="cancel",
                wsengine_name=self.exchange,
                symbol=self.symbol.to_str(),
                timestamp=now,
            )
        ))

        self.orderQueue[id_] = order_queue
        self.eventStory.put(
            CreateCustomIntervalWithOffset(
                id=id_,
                interval=self.remain_time,
                offset=start_sec,
            )
        )

    def _GenerateRandomOrder(self, side: Side) -> quote:
        """ランダムな注文を生成するメソッド。
        Limit orderの価格と量を返す。
        """
        exchange = self.exchange
        precision = self.precision[exchange]

        match side:
            case Side.BUY:
                best_price = self.bestbid[exchange].price
                plus_minus = -1
                orderbook = self.orderbook.bids
            case Side.SELL:
                best_price = self.bestask[exchange].price
                plus_minus = +1
                orderbook = self.orderbook.asks

        # ex) if side = Side.BUY, best_price = 100, rangeMin = 2, rangeMax = 4, then min_ = 98, max_ = 96
        #     if side = Side.SELL, best_price = 100, rangeMin = 2, rangeMax = 4, then min_ = 102, max_ = 104
        min_ = best_price * (1 + self.range_min / 100 * plus_minus)
        max_ = best_price * (1 + self.range_max / 100 * plus_minus)

        # subtract the amount of precision from the middle (min_ask, max_bid)
        prices = [
            min_ + i * precision * plus_minus
            for i in range(int(abs(max_ - min_) // precision))
        ]

        # delete prices that already exist in the order book
        prices_existing = [q.price for q in orderbook]
        prices = [p for p in prices if p not in prices_existing]

        price = random.choice(prices)

        amount = random.uniform(self.amount_min, self.amount_max)

        return quote(price=price, amount=amount)
