class List:
    legend_text = "Built-in list"

    def __init__(self):
        self.list = []
        self.remove = self.list.remove
        self.add = self.list.append

    def search(self, x):
        return self.list[self.list.index(x)]
