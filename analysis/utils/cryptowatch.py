import json
import requests
import pandas as pd


def get_ohlcv(exchange, symbol):
    query: dict[str, str] = {}
    url = "https://api.cryptowat.ch/markets/" + exchange + "/" + symbol + "/ohlc"
    ohlcvs = json.loads(requests.get(url, query).text)["result"]
    for k in ohlcvs.keys():
        df = pd.DataFrame(ohlcvs[k], columns=['timestamp','open','high','low','close','amount','volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
        df = df.set_index('timestamp')
        ohlcvs[k] = df
    return ohlcvs