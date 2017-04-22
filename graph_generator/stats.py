import pandas as pd

class Stats(object):
    def __init__(self, serie):
        self.serie = serie

    def q90(self):
        serie=self
        q90 = serie.quantile(.10)

#    def q50(self):