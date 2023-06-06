import backtrader as bt


class my_BuySell(bt.observers.BuySell):
    params = (("barplot", True), ("bardist", 0.02))

    plotlines = dict(
        buy=dict(marker=r"$\Uparrow$", markersize=10.0, color="#2ca02c"),
        sell=dict(marker=r"$\Downarrow$", markersize=10.0, color="#d62728"),
    )


class ProfitObserver(bt.observer.Observer):
    maxValue = 0.0
    drawback = 0.0
    lastCash = 0.0
    alias = ("CashProfit",)
    lines = (
        "profit",
        "drawback",
    )

    plotinfo = dict(plot=True, subplot=True)

    plotlines = dict(profit=dict(color="green"), drawback=dict(color="red"))

    def next(self):
        # 出现买卖
        if self._owner.broker.getcash() != self.lastCash:
            self.lastCash = self._owner.broker.getcash()
            self.lines.profit[0] = self._owner.broker.getvalue() - 100000
            self.maxValue = max(self.maxValue, self._owner.broker.getvalue())
            self.lines.drawback[0] = self.maxValue - self._owner.broker.getvalue()
        else:
            self.lines.drawback[0] = self.lines.drawback[-1]
            self.lines.profit[0] = self.lines.profit[-1]


class OrderObserver(bt.observer.Observer):
    maxValue = 0.0
    drawback = 0.0
    lastCash = 0.0
    alias = ("CashProfit",)
    lines = ("possize", "stopsize")

    plotinfo = dict(plot=True, subplot=True)

    plotlines = dict(possize=dict(color="green"), stopsize=dict(color="red"))

    def next(self):
        # 出现买卖
        # self._owner.broker.getposition(self.data).size
        self.lines.possize[0] = self._owner.broker.getposition(self.data).size
        sz = 0
        for order in self._owner._orderspending:
            # if order.data is not self.data:
            #     continue
            # if order.exectype == bt.Order.Stop:
            sz += 1
        self.lines.stopsize[0] = sz
