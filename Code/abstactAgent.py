# -*- coding: utf-8 -*-
from MyGoban import MyBoard
from abc import ABC as AbstractClass
from abc import abstractmethod 

class AbstactAgent(AbstractClass):

    ############################################
    '''             Constructor              '''

    def __init__(self):
        pass

    #############################################
    '''     Public functions for myPlayer     '''

    @abstractmethod
    def get_next_move(self, lastOpponentMove, evalHandler):
        pass
