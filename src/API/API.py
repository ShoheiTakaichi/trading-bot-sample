from queue import Queue
from threading import Thread

import uvicorn
from API.APIBodyBase import APIBodyBase
from API.ApiConverter import toBalanceResponse
from ccxws.models import balance, execution, user_execution
from Event import *
from Model import Symbol
from botframelib.Event import *
from botframelib.EventSourcing import IWorker

# TODO migrate to env file
origins = ["http://18.179.24.225/", "http://localhost:3000"]


class CreateRequestBody(BaseModel):
    # base
    exchange: str
    symbol: Symbol
    # decision logic params
    rangeMin: int
    rangeMax: int
    amountMin: int
    amountMax: int
    # execution logic params
    perMin: int
    remainTime: int
    nUpdate: int


class OrderHistElement(BaseModel):
    id: UUID
    action: str
    wsengineName: str
    symbol: str
    side: Optional[str]
    amount: Optional[float]
    price: Optional[float]
    timestamp: str


class APIBody(APIBodyBase):
    def __init__(self, eventStory: Queue):
        super().__init__(eventStory, botMode="lp", exchange="bitfinex")

    def run(self):
        self.definition()
        self.afterApiDefinition()
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="warning")

    def definition(self):
        @self.prefix_router.post("/create")
        async def create(request: CreateRequestBody) -> None:
            self.eventStory.put(CreateBot(
                exchange=request.exchange,
                symbol=request.symbol,
                range_min=request.rangeMin,
                range_max=request.rangeMax,
                amount_min=request.amountMin,
                amount_max=request.amountMax,
                per_min=request.perMin,
                remain_time=request.remainTime,
                n_update=request.nUpdate,
            ))

        @self.prefix_router.post("/stop")
        async def stop() -> None:
            self.eventStory.put(StopBot())

        @self.prefix_router.get("/balance")
        async def getBalance():
            return toBalanceResponse(self.balanceDict, self.initialBalanceDict)

        @self.prefix_router.get("/userExecutionList")
        async def getUserExecutionList() -> list[user_execution]:
            return self.userExecutionList

        @self.prefix_router.get("/orderHist")
        async def getOrderHist() -> list[OrderHistElement]:
            # TODO: イケてない、pyserdeとかで直したい
            orderHist = [
                OrderHistElement(
                    id=o.id_,
                    action=o.action,
                    wsengineName=o.wsengine_name,
                    symbol=o.symbol,
                    side=o.side,
                    amount=o.amount,
                    price=o.price,
                    timestamp=o.timestamp,
                )
                for o in self.orderHist
            ]
            return orderHist


class API(IWorker):
    def __init__(self):
        IWorker.__init__(self)
        # self.api = MockBody()
        self.api = APIBody(self.eventStory)

    def setEventstory(self, eventStory):
        self.eventStory = eventStory
        self.api.eventStory = eventStory

    def preprocess(self):
        self.api.start()

    def onUpdateOrderBook(self, event):
        orderbook = event.orderbook
        if type(self.api.orderbook.get(orderbook.exchange)) != dict:
            self.api.orderbook[orderbook.exchange] = {orderbook.symbol: orderbook}
        else:
            self.api.orderbook[orderbook.exchange][orderbook.symbol] = orderbook

    def onUpdateExecution(self, event: UpdateExecution):
        execution = event.execution
        if type(self.api.execution.get(execution.exchange)) != dict:
            self.api.execution[execution.exchange] = {execution.symbol: execution}
        else:
            self.api.execution[execution.exchange][execution.symbol] = execution

    def onUpdateUserExecution(self, event: UpdateUserExecution):
        userexecution = event.user_execution
        if event.wsengine_name not in self.api.userExecutionList.keys():
            self.api.userExecutionList[event.wsengine_name] = []
        self.api.userExecutionList[event.wsengine_name].insert(0, userexecution)
        if len(self.api.userExecutionList[event.wsengine_name]) > 50:
            self.api.userExecutionList[event.wsengine_name].pop()

    def onUpdateUserOrder(self, event: UpdateUserOrder):
        self.api.userorder[event.wsengine_name] = event.user_order_list

    def onBotDoOrder(self, event: BotDoOrder):
        self.api.orderHist.append(event)

    def onUpdateBalance(self, event: UpdateBalance):
        self.api.balanceDict[event.wsengine_name] = event.balance

    def onSODBalance(self, event: SODBalance):
        self.api.initialBalanceDict[event.wsengine_name] = event.balance

    def onUpdateTotalVolume(self, event):
        self.api.totalVolume = event.totalVolume
