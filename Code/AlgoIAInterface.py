import Goban
import time
from random import choice

class AlgoIAInterface:

    ############################################
    '''             Constructor              '''

    def __init__(self, board):
        self._board = board
    

    #############################################
    '''     Public functions for myPlayer     '''

    def getMove(self):
        pass


    ############################################
    '''     Delegation Goban functions       '''
    
    def _push(self, move):
        return self._board.push(move)

    ########

    def _pop(self):
        self._board.pop()