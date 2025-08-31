class Counter:
    def __init__(self, array_or_int):
        self.length = array_or_int if isinstance(array_or_int,int) else len(array_or_int)
        self.index = 0

    def tick(self):
        self.index += 1
        percentage = round(self.index * 100 / self.length) if self.length else 0
        return {"index": self.index, "length": self.length, "percentage": percentage}