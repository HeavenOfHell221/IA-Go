# -*- coding: utf-8 -*-
from MyGoban import MyBoard
from abc import ABC as AbstractClass
from abc import abstractmethod 
from Modules.aliasesType import *

class AbstactAgent(AbstractClass):
    '''
    Classe abstaite pour les agents.
    '''

    ############################################
    '''             Constructor              '''

    def __init__(self):
        pass

    #############################################
    '''     Public functions for myPlayer     '''

    @abstractmethod
    def get_next_move(self, lastOpponentMove:FlattenMove, evalHandler, incrementStep:int) -> FlattenMove:
        '''
        Calcul, via le déroulement de l'arbre de jeu, le meilleur mouvement à jouer, puis le retourne.
        Utilise {evalHandler} pour évaluer un plateau de jeu. Il est de type AbstractGobanEval.
        '''
        pass
