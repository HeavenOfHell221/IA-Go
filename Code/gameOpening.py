import time
from MyGoban import MyBoard
from abstractAlgoIA import AbstractAlgoIA
from random import choice, shuffle
from Modules.aliasesType import *

class GameOpening(AbstractAlgoIA):

    ############################################
    '''             Constructor              '''

    def __init__(self, board:MyBoard, opLastMove:str):
        AbstractAlgoIA.__init__(self, board)
        self._opponentLastMove:str = opLastMove
        self._moveWantToPlay = {}
        self._moveWantToPlay['C3'] = 'C7'
        self._moveWantToPlay['C7'] = 'C3'
        self._moveWantToPlay['G3'] = 'G7'
        self._moveWantToPlay['G7'] = 'G3'

    ############################################
    '''          public functions            '''

    def get_next_move(self) -> FlattenMove:
        if self._opponentLastMove == None:
            return super().name_to_flat('G7') 

        if self._opponentLastMove in self._moveWantToPlay:
            m = self._moveWantToPlay[self._opponentLastMove]
            self._moveWantToPlay[self._opponentLastMove] = None
            if m == None:
                return -1
        else:
            return -1

        return super().name_to_flat(m)
  