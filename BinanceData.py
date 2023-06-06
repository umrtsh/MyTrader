import requests
import json
import pandas as pd
import datetime as dt


def get_binance_bars(symbol, interval, startTime, endTime):
    url = "https://api.binance.com/api/v3/klines"

    startTime = str(int(startTime.timestamp() * 1000))
    endTime = str(int(endTime.timestamp() * 1000))
    limit = "1000"

    req_params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": startTime,
        "endTime": endTime,
        "limit": limit,
    }
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890",
    }
    response = requests.get(url, params=req_params, proxies=proxies)
    data = json.loads(response.text)
    df = pd.DataFrame(data)

    if len(df.index) == 0:
        return None

    df = df.iloc[:, 0:6]
    df.columns = ["datetime", "open", "high", "low", "close", "volume"]

    df.open = df.open.astype("float")
    df.high = df.high.astype("float")
    df.low = df.low.astype("float")
    df.close = df.close.astype("float")
    df.volume = df.volume.astype("float")

    # df["adj_close"] = df["close"]

    df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.datetime]

    return df


def get_binance_data(symbol=None, interval=None, fromDate=None):
    df_list = []
    # 数据起点时间
    last_datetime = fromDate or dt.datetime(2023, 1, 1)
    symbol = symbol or "BTCUSDT"
    interval = interval or "1h"
    while True:
        new_df = get_binance_bars(
            symbol, interval, last_datetime, dt.datetime.now()
        )  # 获取1分钟k线数据

        if new_df is None:
            break
        df_list.append(new_df)
        last_datetime = max(new_df.index) + dt.timedelta(0, 1)

    return pd.concat(df_list)
