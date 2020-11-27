# -*- coding: utf-8 -*-
import Goban
import time
from random import choice
from abc import ABC, abstractmethod 

class AbstractAlgoIA(ABC):

    ############################################
    '''             Constructor              '''

    def __init__(self, board:Goban):
        self.__board = board
   

    #############################################
    '''     Public functions for myPlayer     '''

    @abstractmethod
    def getMove(self):
        pass


    ############################################
    '''     Delegation Goban functions       '''
    
    def push(self, move):
        return self.__board.push(move)

        ########

    def pop(self):
        self.__board.pop()

        ########
    
    def isGameOver(self) -> bool:
        return self.__board.is_game_over()

        ########

    def getWeakMovements(self) -> []:
        return self.__board.weak_legal_moves()

        ########

    def getLegalMovements(self) -> []:
        return self.__board.legal_moves()