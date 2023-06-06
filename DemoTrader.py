from __future__ import absolute_import, division, print_function, unicode_literals
import math
import datetime as dt
import pandas as pd
import backtrader as bt
import MyStrategy as mst
import BinanceData
import MyObserver
from datetime import datetime
from MyStrategy import my_strategy_rsiDiv

# from MyStrategy import OrderObserver
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
import backtrader.analyzers as btanalyzers

if __name__ == "__main__":
    # 0. Initialize, Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=True, tradehistory=True)
    cerebro.addsizer(bt.sizers.SizerFix, stake=1)
    # cerebro.addobserver(MyObserver.ProfitObserver)
    cerebro.addobserver(MyObserver.OrderObserver)
    cerebro.broker.setcash(100000.0)  # Set our desired cash start
    cerebro.broker.setcommission(commission=0.0004)
    cerebro.broker.set_coc(True)  # 设置以当日收盘价成交
    cerebro.addanalyzer(btanalyzers.Transactions, _name="trans")  # 交易次数
    # 1. Feed Data
    dataframe = pd.read_csv(
        "./resource/BTCUSDT1h.csv",
        parse_dates=["datetime"],
        date_parser=lambda x: datetime.fromtimestamp(float(x) / 1000.0),
        index_col=0,
        header=0,
    )
    data = bt.feeds.PandasData(
        dataname=dataframe,
        # fromdate=dt.datetime(2023, 1, 1),
        # todate=dt.datetime(2023, 5, 27),
    )
    cerebro.adddata(data, name="BTCUSDT")
    # 2. Add Strategy
    cerebro.addstrategy(my_strategy_rsiDiv)
    # 3. View Profit
    print("Starting Portfolio cash: %.2f" % cerebro.broker.getvalue())
    result = cerebro.run()
    print("Final Portfolio : %.2f" % cerebro.broker.getvalue())
    num_of_trades = len(result[0].analyzers.trans.get_analysis())
    print("Number of Trades : %d" % num_of_trades)
    cerebro.plot(style="candle", barup="green", bardown="red", numfigs=1)
    # b = Bokeh(style="bar", plot_mode="single", scheme=Tradimo())
    # cerebro.plot(b)
