# -*- coding: utf-8 -*-
import time
from MyGoban import MyBoard
from random import choice
from abc import ABC as AbstractClass
from abc import abstractmethod 
from Modules.aliasesType import *
import copy

class AbstractAlgoIA(AbstractClass):

    ############################################
    '''             Constructor              '''

    def __init__(self, board: MyBoard):
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

        ########

    def currentHash(self) -> int:
        return self.__board.currentHash

        ########

    def nbStoneWhite(self) -> int:
        return self.__board.nbStoneWhite

        ########

    def nbStoneBlack(self) -> int:
        return self.__board.nbStoneBlack

        ########

    def nb_stones(self, color:int) -> int:
        return self.__board.nb_stones(color)

        ########

    def nb_liberties_at(self, fcoord:FlattenMove) -> int:
        return self.__board.nb_liberties_at(fcoord) 

        ########

    def nb_liberties(self, color:int) -> int:
        return self.__board.nb_liberties(color)

        ########

    def nb_strings(self, color:int) -> int:
        return self.__board.nb_strings(color)

        ########

    def switch_color(self, color:int) -> int:
        return MyBoard.flip(color)

        ########

    def next_player(self) -> int:
        return self.__board.next_player()

        ########

    def flat_to_name(self, fcoord) -> str:
        return MyBoard.flat_to_name(fcoord)

        ########

    def deepcopy_board(self) -> MyBoard:
        return copy.deepcopy(self.__board)

        ########

    def pretty_print(self) -> None:
        self.__board.pretty_print()

    def stones_list(self, color:int) -> set:
        return self.__board.stones_list(color)
