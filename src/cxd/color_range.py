__author__ = "malware4n6"
__copyright__ = "malware4n6"
__license__ = "The Unlicense"

class ColorRange():
    def __init__(self, start, length, color = None, comment = None) -> None:
        self.start = start
        self.length = length
        self.color = color
        # -1 because (start + length) define the first next excluded byte
        self.end = start + length - 1
        self.comment = comment

    def __str__(self):
        return f'{self.start},{self.length},{self.color if self.color else ""},{self.comment if self.comment else ""}'
