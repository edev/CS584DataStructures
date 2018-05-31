from sortedcontainers import SortedList as OriginalSortedList


class SortedList(OriginalSortedList):
    legend_text = "SortedList"

    def search(self, x):
        return self.__getitem__(self.index(x))