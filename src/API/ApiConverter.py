from ccxws import models
from ccxws.models.balance import asset, balance


class AssetResponse(models.asset):
    sodAmount: float
    dailyPL: float


def mergeSodBalance(currentAsset: asset, sodAssetList: list[asset]) -> AssetResponse:
    _symbol = currentAsset.symbol
    _sodAsset = None
    for i in sodAssetList:
        if i.symbol == _symbol:
            _sodAsset = i
    _sodAmount = -1 if _sodAsset == None else _sodAsset.amount
    response = {
        **currentAsset.dict(),
        "sodAmount": _sodAmount,
        "dailyPL": (currentAsset.amount - _sodAmount),
        "dailyPLrate": (currentAsset.amount - _sodAmount) / currentAsset.amount,
    }
    return AssetResponse(**response)


def toBalanceResponse(balance: dict[str, balance], sodBalance: dict[str, balance]) -> list[dict[str, object]]:
    response = []
    for exchange in balance.keys():
        assetListInExchange = balance[exchange]
        initialAssetListInExchange = sodBalance.get(exchange)
        assetResponseList = list(
            map(
                lambda x: mergeSodBalance(x, assetListInExchange.balance),
                initialAssetListInExchange.balance,
            )
        )
        response.append(
            {
                "name": exchange,
                "data": {
                    "exchange": initialAssetListInExchange.exchange,
                    "balance": assetResponseList,
                },
            }
        )
    return response


def toUserExecutionResponse(userexecutionList):
    resList = [
        {
            "name": ws_name,
            "data": list(
                map(
                    lambda x: {**x.dict(), "isUserExecution": True},
                    userexecutionList[ws_name],
                )
            ),
        }
        for ws_name in userexecutionList.keys()
    ]
    return {"userExecutionList": resList}
