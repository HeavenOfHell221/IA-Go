# -*- coding: utf-8 -*-
import time
from MyGoban import MyBoard
from random import choice
from abc import ABC as AbstractClass
from abc import abstractmethod 
from Modules.aliasesType import *

class AbstactAgent(AbstractClass):

    ############################################
    '''             Constructor              '''

    def __init__(self):
        pass

    #############################################
    '''     Public functions for myPlayer     '''

    @abstractmethod
    def get_next_move(self):
        pass
