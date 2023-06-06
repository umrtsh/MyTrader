import backtrader as bt


class my_strategy_rsiDiv(bt.Strategy):
    # 全局设定交易策略的参数
    params = (("maperiod", 20),)
    # [[rsi,price]old,[rsi,price]new]阶段低点和高点
    pivotLow = [[0.01, 0.01, "1"], [0.01, 0.01, "1"]]
    pivotHigh = [[0.01, 0.01, "1"], [0.01, 0.01, "1"]]
    isMax = False  # 当前位置是否为区间高点
    isMin = False  # 当前位置是否为区间低点
    # lookBack
    lbL = 6
    lastMaxBarIndex = 0
    lastMinBarIndex = 0
    currentBarNum = 0
    sumProfit = 0

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close
        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # 添加移动均线指标，内置了talib模块
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod
        )
        self.sma13 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod - 7
        )
        self.rsi = bt.indicators.RSI(self.datas[0], period=10)

    def log(self, txt, dt=None):
        """Logging function fot this strategy"""
        dtt = dt or self.datas[0].datetime.time(0)
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print("%s, %s" % (dt.isoformat(), txt))

    def updatePivot(self):
        self.currentBarNum += 1
        if self.currentBarNum < self.lbL:
            return

        rsiData = self.rsi.get(ago=0, size=self.lbL + 1)
        priceData = self.dataclose.get(ago=0, size=self.lbL + 1)

        curMax = max(rsiData)
        indexMax = rsiData.index(curMax)
        curMin = min(rsiData)
        indexMin = rsiData.index(curMin)
        # 如果区域最大最小值变化，则更新枢轴, 索引不能是最后一个(向后看一根线),距离上一个枢轴距离大于5根
        if abs(curMax - self.pivotHigh[1][0]) > 0.1 and indexMax == 5:  # 当前最大
            # lastHigh
            self.pivotHigh[0][0] = self.pivotHigh[1][0]
            self.pivotHigh[0][1] = self.pivotHigh[1][1]
            self.pivotHigh[0][2] = self.pivotHigh[1][2]
            # currentHigh
            self.pivotHigh[1][0] = curMax
            self.pivotHigh[1][1] = priceData[indexMax]
            dtt = self.datas[0].datetime.time(0).isoformat()
            dt = self.datas[0].datetime.date(0).isoformat()
            self.pivotHigh[1][2] = dt + " " + dtt
            self.isMax = True
            self.lastMaxBarIndex = self.currentBarNum
        else:
            self.isMax = False

        if abs(curMin - self.pivotLow[1][0]) > 0.1 and indexMin == 5:
            # lastLow
            self.pivotLow[0][0] = self.pivotLow[1][0]
            self.pivotLow[0][1] = self.pivotLow[1][1]
            self.pivotLow[0][2] = self.pivotLow[1][2]
            # currentLow
            self.pivotLow[1][0] = curMin
            self.pivotLow[1][1] = priceData[indexMin]
            dtt = self.datas[0].datetime.time(0).isoformat()
            dt = self.datas[0].datetime.date(0).isoformat()
            self.pivotLow[1][2] = dt + " " + dtt
            self.isMin = True
            self.lastMinBarIndex = self.currentBarNum

            # self.log('pivotMin: %.1f minPrice: %.1f' % (curMin, priceData[indexMin]))
        else:
            self.isMin = False

    def bullCondition(self):
        # rsi: Higher Low  _inRange：之前的低点要在rangeLower-rangeUpper之间
        # plFound = na(pivotlow(osc, lbL, lbR)) ? false : true
        # rsi[lbR] > valuewhen(plFound, osc[lbR], 1) and _inRange(plFound[1])
        # rsi: Higher Low
        rsiHL = self.pivotLow[1][0] > self.pivotLow[0][0]
        # Price: Lower Low
        priceLL = self.pivotLow[1][1] < self.pivotLow[0][1]

        return rsiHL and priceLL and self.isMin

    def bearCondition(self):
        # rsi: Lower High
        rsiLH = self.pivotHigh[1][0] < self.pivotHigh[0][0]
        # Price: Higher High
        priceHH = self.pivotHigh[1][1] > self.pivotHigh[0][1]

        return rsiLH and priceHH and self.isMax

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            curPrice = order.executed.price
            curSize = order.executed.size
            if order.isbuy() and self.position:
                self.log(
                    "BUY %.0f EXECUTED:%.2f, left cash:%.2f, curtime:%s, rsi:%.2f, last low:%s %d %.2f"
                    % (
                        curSize,
                        curPrice,
                        self.broker.cash,
                        self.pivotLow[1][2],
                        self.pivotLow[1][0],
                        self.pivotLow[0][2],
                        self.pivotLow[0][1],
                        self.pivotLow[0][0],
                    )
                )
            elif order.issell():
                self.log(
                    "SELL %.0f EXECUTED:%.2f, profit:%.2f, curtime:%s, rsi:%.2f last high:%s %d %.2f"
                    % (
                        curSize,
                        curPrice,
                        self.broker.getvalue() - 100000,
                        self.pivotHigh[1][2],
                        self.pivotHigh[1][0],
                        self.pivotHigh[0][2],
                        self.pivotHigh[0][1],
                        self.pivotHigh[0][0],
                    )
                )
                print("\n")
        # Write down: no pending order
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        self.trade = trade  # 记录交易
        if trade.isclosed:
            self.sumProfit += trade.pnlcomm
            print(
                "毛收益 %0.2f, 扣佣后收益 % 0.2f, 总收益 %0.2f, 佣金 %.2f"
                % (trade.pnl, trade.pnlcomm, self.sumProfit, trade.commission)
            )

    def next(self):
        trail_amount = 410
        self.updatePivot()
        if self.order:  # 检查是否有指令等待执行,
            return
        # 需要未来一bar走完才能判断高低点(趋势逆转)，所以会延迟1h
        if self.bullCondition():
            if self.position.size > 0:  # 已有仓位
                return
            if self.position.size < 0:
                pass
                # self.close()

            mainside = self.buy(size=1, transmit=False)
            lowside = self.sell(
                exectype=bt.Order.StopTrail,
                trailamount=trail_amount,
                size=mainside.size,
                transmit=True,
                parent=mainside,
            )
            # self.order_target_size(target=1)
        elif self.bearCondition():
            if self.position.size < 0:
                return
            if self.position.size > 0:
                pass
                # self.close()

            mainside = self.sell(size=1, transmit=False)
            highside = self.buy(
                exectype=bt.Order.StopTrail,
                trailamount=trail_amount,
                size=mainside.size,
                transmit=True,
                parent=mainside,
            )
            # self.order_target_size(target=-1)
