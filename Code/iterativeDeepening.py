# -*- coding: utf-8 -*-

import time
from Goban import Board
from random import choice
from abstractAlgoIA import AbstractAlgoIA
from aliasesType import *

class Movement:

    def __init__(self, move = None, index = None, depth = 0, score = 0):
        self.move = move
        self.index = index
        self.depth = depth
        self.score = score

    def __repr__(self):
        return f"move=[{self.move}], index=[{self.index}], depth=[{self.depth}], score=[{self.score}]"

class IterativeDeepening(AbstractAlgoIA):

    #############################################
    #############################################
    ''' Main '''

    def __init__(self, board: Board, duration = 5):
        AbstractAlgoIA.__init__(self, board)
        self.__itDeepDuration = duration
        self.__stopDepth = 1
        self.__timeToStop = 0

        self.__bestMoves = {}


    #############################################
    #############################################
    ''' public functions for myPlayer '''

    def get_next_move(self) -> Union[FlattenMove, None]:

        self.__timeToStop = time.time() + self.__itDeepDuration

        lastMove = None
        run = True

        while run :
            m = self._start_alpha_beta()
            if m != None:
                lastMove = m
                self.__stopDepth += 1
            else:
                run = False
                self.__stopDepth -= 1 # Annulation du dernier AlphaBeta qui n'a pas terminé pour cause de manque de temps

        return lastMove
    

    #############################################
    #############################################
    ''' Internal functions '''


    def _board_value(self, isFriendLevel: bool) -> int:
        ''' 
        Heuristique d'un plateau de jeu de GO avec 9x9 cases 
        TODO : Avoir un objet pour gérer les heuristiques
        '''
        return choice([i for i in range(1, 100)]) * (1 if isFriendLevel else -1) 

            ####

    def _start_alpha_beta(self) -> Union[FlattenMove, None]:
        isFriendLevel = True
        currentDepth = 1
        possibleMoves:FlattenMoves = []
        firstMoveToCheck = 0
        maxValue = -1000000 

        moves = super().legal_moves()

        for i in range(firstMoveToCheck, len(moves)):
            
            super().push(moves[i]) 
            
            if currentDepth == self.__stopDepth:
                valueCurrentMove = self._board_value(isFriendLevel)
            else:
                valueCurrentMove = self._alpha_beta(currentDepth = currentDepth + 1, 
                                                    alpha = -1000000, beta = 1000000, 
                                                    isFriendLevel = not isFriendLevel)
            
            super().pop()

            if valueCurrentMove == None: # Si le temps est écoulé
                return None

            if valueCurrentMove > maxValue:
                maxValue = valueCurrentMove
                possibleMoves.clear()
                possibleMoves.append(moves[i])
            elif valueCurrentMove == maxValue:
                possibleMoves.append(moves[i])

        move = choice(possibleMoves)
        return move

            ####

    def _alpha_beta(self, currentDepth: int, alpha: int, beta: int, isFriendLevel: bool) -> Union[FlattenMove, None]:
        if time.time() >= self.__timeToStop:
            return None

        if currentDepth == self.__stopDepth or super().is_game_over():
            return self._board_value(isFriendLevel)

        moves = super().weak_legal_moves()
        
        firstMove = 0

        for i in range(firstMove, len(moves)):

            if super().push(moves[i]) == False: # Si le mouvement n'est pas légal
                super().pop()
                continue # On passe au mouvement suivant

            retValue = self._alpha_beta(currentDepth = currentDepth + 1, alpha = alpha, beta = beta, 
                                    isFriendLevel = not isFriendLevel)
            
            super().pop()
            
            if retValue == None:
                return None

            if isFriendLevel:
                alpha = max(alpha, retValue)
            else:
                beta = min(beta, retValue)

            if alpha >= beta :
                return (beta if isFriendLevel else alpha)

        return (alpha if isFriendLevel else beta)