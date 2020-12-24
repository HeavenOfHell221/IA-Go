from abc import ABC as AbstractClass
from abc import abstractmethod 
from MyGoban import MyBoard

class AbstractGobanEval:
    def __init__(self):
        pass

    @abstractmethod
    def board_value(self, board, maxDepth, maximizingPlayer, lastMove):
        pass

