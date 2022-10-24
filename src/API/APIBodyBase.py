import os
from queue import Queue
from threading import Thread
from typing import List

from ccxws import models
from ccxws.models import balance
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# TODO migrate to env file
origins = ["http://localhost:3000"]


class APIBodyBase(Thread):
    def __init__(self, eventStory: Queue, botMode, exchange):
        Thread.__init__(self)
        self.eventStory = eventStory
        # if you want to change these type, please check client too
        self.balanceDict: dict[str, balance] = {}  # {exchange: balance}
        self.initialBalanceDict: dict[str, balance] = {}  # {exchange: balance}
        self.last_event = {}
        self.orderbook = {}
        self.userorder = {}
        self.execution: dict[str, dict[str, models.execution]] = {}
        self.userExecutionList: List[models.user_execution] = []
        self.orderHist: list[BotDoOrder] = []

        self.app = FastAPI()

        # https://fastapi.tiangolo.com/tutorial/cors/
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.prefix_router = APIRouter(
            prefix=f"/api/{botMode}"
        )

        # This is for healthCheck, do not chenge path
        @self.app.get("/")
        async def helthcheck():
            return "OK"

        @self.app.get("/config")
        async def config():
            return {"mode": os.environ.get("BOTMODE")}

    def afterApiDefinition(self):
        self.app.include_router(self.prefix_router)
