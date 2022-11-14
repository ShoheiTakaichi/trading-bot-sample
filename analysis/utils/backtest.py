import pandas as pd
import numpy as np


def doten(ohlcv, signal):
    # type check
    assert 'open' in ohlcv.columns
    assert 'high' in ohlcv.columns
    assert 'low' in ohlcv.columns
    assert 'close' in ohlcv.columns
    assert 'signal' in signal.columns
    assert all(ohlcv.index == signal.index)
    
    open = ohlcv['open'].to_numpy()
    sign = signal['signal'].to_numpy()
    asset = np.zeros(len(open))
    position = np.zeros(len(open))
    pl = np.zeros(len(open))
    rest = np.zeros(len(open))
    margin = np.zeros(len(open))

    # start with ohlcv[0].open
    rest[0] = open[0]
    asset[0] = open[0]
    margin[0] = 0
    
    for i in range(len(open)-1):
        pl[i+1] = pl[i] + (open[i+1] - open[i]) * position[i]
        if sign[i] == 'buy':
            if position[i] <= 0:
                rest[i+1] = rest[i] + margin[i] + pl[i+1]
                position[i+1] = rest[i+1] / open[i+1]
                margin[i+1] = rest[i+1]
                rest[i+1] = 0
                pl[i+1] = 0
            elif position[i] > 0:
                position[i+1] = position[i] + rest[i] / open[i+1]
                margin[i+1] = margin[i] + rest[i]
                rest[i+1] = 0
                
        if sign[i] == 'sell':
            if position[i] >= 0:
                rest[i+1] = rest[i] + margin[i] + pl[i+1]
                position[i+1] = - rest[i+1] / open[i+1]
                margin[i+1] = rest[i+1]
                rest[i+1] = 0
                pl[i+1] = 0
            elif position[i] < 0:
                position[i+1] = position[i] - rest[i] / open[i+1]
                margin[i+1] = margin[i] + rest[i]
                rest[i+1] = 0
                
        if sign[i] == 'neutral':
            position[i+1] = 0
            margin[i+1] = 0
            rest[i+1] = rest[i] + margin[i] + pl[i+1]
            pl[i+1] = 0
            
        if sign[i] == 'keep':
            position[i+1] = position[i]
            margin[i+1] = margin[i]
            rest[i+1] = rest[i]
        
        asset[i+1] = rest[i+1] + margin[i+1] + pl[i+1]
    
    result = pd.DataFrame(index = ohlcv.index)
    result['asset'] = asset
    result['pl'] = pl
    result['margin'] = margin
    result['rest'] = rest
    result['position'] = position
    return result