import pandas as pd
import numpy as np
import talib
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_ohlcv(ohlcv):
    assert 'open' in ohlcv.columns
    assert 'high' in ohlcv.columns
    assert 'low' in ohlcv.columns
    assert 'close' in ohlcv.columns
    assert 'volume' in ohlcv.columns
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_width=[0.2, 0.7],
        x_title="Date")
    # Candlestick 
    fig.add_trace(
        go.Candlestick(
            x=ohlcv.index,
            open=ohlcv["open"],
            high=ohlcv["high"],
            low=ohlcv["low"],
            close=ohlcv["close"], showlegend=False),
        row=1, col=1
    )

    # Volume
    fig.add_trace(
        go.Bar(x=ohlcv.index, y=ohlcv["volume"], showlegend=False),
        row=2, col=1
    )

    fig.update_layout(
        title={
            "text": "ohlcv",
            "y":0.9,
            "x":0.5,
        },
    )

    fig.update_xaxes( # 日付のフォーマット変更
    )

    fig.update_yaxes(separatethousands=True, title_text="price", row=1, col=1) 
    fig.update_yaxes(title_text="volume", row=2, col=1)
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show()

def plot_ohlcv_with_RSI(ohlcv,rsi):
    assert 'open' in ohlcv.columns
    assert 'high' in ohlcv.columns
    assert 'low' in ohlcv.columns
    assert 'close' in ohlcv.columns
    assert 'volume' in ohlcv.columns
    assert 'RSI' in rsi.columns

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_width=[0.2, 0.2, 0.7], 
        x_title="Date")
    # Candlestick 
    fig.add_trace(
        go.Candlestick(
            x=ohlcv.index,
            open=ohlcv["open"],
            high=ohlcv["high"],
            low=ohlcv["low"],
            close=ohlcv["close"], showlegend=False),
        row=1, col=1
    )

    # Volume
    fig.add_trace(
        go.Bar(x=ohlcv.index, y=ohlcv["volume"], showlegend=False),
        row=2, col=1
    )

    fig.update_layout(
        title={
            "text": "ohlcv",
            "y":0.9,
            "x":0.5,
        },
    )

    # Volume
    fig.add_trace(
        go.Scatter(x=rsi.index, y=rsi["RSI"], showlegend=False),
        row=3, col=1
    )

    fig.update_layout(
        title={
            "text": "ohlcv",
            "y":0.9,
            "x":0.5,
        },
    )
    fig.update_xaxes( # 日付のフォーマット変更
    )

    fig.update_yaxes(separatethousands=True, title_text="price", row=1, col=1) 
    fig.update_yaxes(title_text="volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show()

def plot_backtest_result(ohlcv, result):
    assert 'open' in ohlcv.columns
    assert 'high' in ohlcv.columns
    assert 'low' in ohlcv.columns
    assert 'close' in ohlcv.columns
    assert 'volume' in ohlcv.columns
    assert 'asset' in result.columns
    assert 'pl' in result.columns
    assert 'position' in result.columns
    assert 'margin' in result.columns
    assert 'rest' in result.columns
    fig = make_subplots(
        rows=2, # candle, position
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_width=[0.2, 0.7],
        x_title="Date")
    # Candlestick 
    fig.add_trace(
        go.Candlestick(
            x=ohlcv.index,
            open=ohlcv["open"],
            high=ohlcv["high"],
            low=ohlcv["low"],
            close=ohlcv["close"], showlegend=False),
        row=1, col=1
    )
    # asset
    fig.add_trace(go.Scatter(x=ohlcv.index, y=result["asset"], name="asset", mode="lines"), row=1, col=1)

    # position
    fig.add_trace(go.Scatter(x=ohlcv.index, y=result["position"], mode="lines", showlegend=False), row=2, col=1)
    fig.update_layout(
        title={
            "text": "ohlcv",
            "y":0.9,
            "x":0.5,
        },
    )
    fig.update_xaxes( # 日付のフォーマット変更
    )
    fig.update_yaxes(separatethousands=True, title_text="price", row=1, col=1) 
    fig.update_yaxes(title_text="position", row=2, col=1)
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show()