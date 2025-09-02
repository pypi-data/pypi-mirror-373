import math

class TxnHist(object):
    def __init__(self, type, kind, duration):
        self.type = type
        self.kind = kind
        self.hist = {}
        self.hist[self._find_bin(duration)] = 1

    def aggregate(self, duration):
        hbin = self._find_bin(duration)
        if hbin not in self.hist:
            self.hist[hbin] = 1
        else:
            self.hist[hbin] += 1

    def _round_bin(self, duration, unit):
        return math.floor(duration/float(unit)) * unit

    def _find_bin(self, duration):
        seconds = 1000
        hbin = 0

        if duration < 0:
            hbin = 0
        elif duration < 2*seconds:
            hbin = self._round_bin(duration, 10)
        elif duration < 10*seconds:
            hbin = self._round_bin(duration, 25)
        elif duration < 20*seconds:
            hbin = self._round_bin(duration, 50)
        elif duration < 50*seconds:
            hbin = self._round_bin(duration, 100)
        elif duration < 80*seconds:
            hbin = self._round_bin(duration, 200)
        elif duration < 100*seconds:
            hbin = self._round_bin(duration, 250)
        else:
            hbin = self._round_bin(duration, 1000)

        return hbin