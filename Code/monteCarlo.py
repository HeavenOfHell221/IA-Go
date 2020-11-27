# -*- coding: utf-8 -*-
import time
from Goban import Board
from abstractAlgoIA import AbstractAlgoIA
from random import choice
from aliasesType import *

class MonteCarlo(AbstractAlgoIA):

    def __init__(self, board: Board):
        AbstractAlgoIA.__init__(self, board)

    def get_next_move(self) -> FlattenMove:
        pass

    

