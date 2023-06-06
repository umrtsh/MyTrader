import backtrader as bt


class OpStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.rsi = bt.indicators.RSI(self.datas[0], period=10)

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print("%s, %s" % (dt.isoformat(), txt))

    def get_divergence_strength(self, rsi, price, is_min, count=0):
        volatility = 10  # 跟波动率相关,后续算,将价格与量级变为两位数
        price_diff = (self.dataclose[-count] - price) / volatility
        rsi_diff = self.rsi[-count] - rsi
        if is_min:
            return -price_diff + rsi_diff
        else:
            return price_diff - rsi_diff

    # 背离天数
    def get_divergence_count(self, rsi, price, is_min, diff=0):
        count = 0
        if is_min:
            while self.dataclose[count] - price < diff and self.rsi[count] - rsi > diff:
                count += 1
        else:
            while self.dataclose[count] - price > diff:
                count += 1
        return count

    # 对进行中的订单进行移动止损，止盈一部分后，保本损
    def trailing_stop(self):
        pass

    def update_pivot(self):
        a = 0

    def condition_bull(self):
        a = 0

    def condition_bear(self):
        a = 0

    def notify_order(self, order):
        a = 0

    def notify_trade(self, trade):
        a = 0

    def next(self):
        self.update_pivot()
        # 需要未来一bar走完才能判断高低点(趋势逆转)，所以会延迟1h
        # self.order_target_size(target=±1)
        if self.condition_bull():
            if self.position.size > 0:  # 已有仓位
                return
            if self.position.size < 0:
                self.close
            mainside = self.buy(size=1, transmit=False)
            self.sell(
                exectype=bt.Order.StopTrail,
                trailamount=500,
                size=mainside.size,
                transmit=True,
                parent=mainside,
            )
        elif self.condition_bear():
            if self.position.size < 0:
                return
            if self.position.size > 0:
                self.close
            mainside = self.sell(size=1, transmit=False)
            self.buy(
                exectype=bt.Order.StopTrail,
                trailamount=500,
                size=mainside.size,
                transmit=True,
                parent=mainside,
            )
