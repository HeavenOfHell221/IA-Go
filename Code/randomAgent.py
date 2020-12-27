# -*- coding: utf-8 -*-

import time
from MyGoban import MyBoard
from random import choice, shuffle
from abstactAgent import AbstactAgent
from Modules.aliasesType import *
import numpy as np

class RandomAgent(AbstactAgent):
    '''
    Agent jouant aléatoirement.
    Il utilise cependant {self.__board.weak_legal_useful_moves()} pour récupérer les coups à jouer.
    '''
    def __init__(self, board:MyBoard):
        self.__board = board

    def get_next_move(self, lastOpponentMove, evalHandler, incrementStep):
        moves = self.__board.weak_legal_useful_moves()

        # Pour éviter qu'il fasse trop vite un 'PASS' par hasard
        if len(moves) > 5:
            moves.remove(-1)

        move = choice(moves)
        
        while(self.__board.push(move) == False):
            self.__board.pop()
            moves.remove(move)
            move = choice(moves)
        
        self.__board.pop()

        return move