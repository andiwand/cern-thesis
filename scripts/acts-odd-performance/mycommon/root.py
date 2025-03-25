import numpy as np


class TEfficiency:
    def __init__(self, tefficency):
        try:
            th1 = tefficency.GetTotalHistogram()
        except:
            th1 = tefficency

        bins = [i for i in range(th1.GetNbinsX()) if th1.GetBinContent(i) > 0.0]
        bins = bins[1:]

        self.x = [th1.GetBinCenter(i) for i in bins]

        self.x_lo = [th1.GetBinLowEdge(i) for i in bins]
        self.x_width = [th1.GetBinWidth(i) for i in bins]
        self.x_hi = np.add(self.x_lo, self.x_width)
        self.x_err_lo = np.subtract(self.x, self.x_lo)
        self.x_err_hi = np.subtract(self.x_hi, self.x)

        try:
            self.y = [tefficency.GetEfficiency(i) for i in bins]
            self.y_err_lo = [tefficency.GetEfficiencyErrorLow(i) for i in bins]
            self.y_err_hi = [tefficency.GetEfficiencyErrorUp(i) for i in bins]
        except:
            self.y = [tefficency.GetBinContent(i) for i in bins]
            self.y_err_lo = [tefficency.GetBinError(i) for i in bins]
            self.y_err_hi = [tefficency.GetBinError(i) for i in bins]

    def errorbar(self, ax, **errorbar_kwargs):
        ax.errorbar(
            self.x,
            self.y,
            yerr=(self.y_err_lo, self.y_err_hi),
            xerr=(self.x_err_lo, self.x_err_hi),
            **errorbar_kwargs,
        )
        return ax

    def step(self, ax, **step_kwargs):
        ax.step(self.x_hi, self.y, **step_kwargs)
        return ax

    def bar(self, ax, **bar_kwargs):
        ax.bar(self.x, height=self.y, yerr=(self.y_err_lo, self.y_err_hi), **bar_kwargs)
        return ax
