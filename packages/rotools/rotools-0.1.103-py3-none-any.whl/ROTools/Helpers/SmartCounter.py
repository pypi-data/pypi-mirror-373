class SmartCounter(object):
    def __init__(self, data=None):
        self.db = {}

        data = data or {}
        for k, v in data.items():
            self.inc(k, v)

    def inc(self, mode, count=1):
        self.db[mode] = self.db.get(mode, 0) + count

    def add(self, obj_2):
        for k, v in obj_2.db.items():
            self.db[k] = self.db.get(k, 0) + v

    def __str__(self):
        return ", ".join([f"{k}: {v}" for k, v in self.db.items()])
