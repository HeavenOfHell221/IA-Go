# -*- coding: utf-8 -*-
import time
from Goban import Board 
from random import choice
from abc import ABC as AbstractClass
from abc import abstractmethod 
from aliasesType import *

class AbstractAlgoIA(AbstractClass):

    ############################################
    '''             Constructor              '''

    def __init__(self, board: Board):
        self.__board = board
   

    #############################################
    '''     Public functions for myPlayer     '''

    @abstractmethod
    def get_next_move(self) -> FlattenMove:
        pass


    ############################################
    '''     Delegation Goban functions       '''
    
    def push(self, move: int) -> bool:
        return self.__board.push(move)

        ########

    def pop(self) -> None:
        self.__board.pop()

        ########
    
    def is_game_over(self) -> bool:
        return self.__board.is_game_over()

        ########

    def weak_legal_moves(self) -> FlattenMoves:
        return self.__board.weak_legal_moves()

        ########

    def legal_moves(self) -> FlattenMoves:
        return self.__board.legal_moves()