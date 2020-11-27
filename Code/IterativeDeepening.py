# -*- coding: utf-8 -*-
import Goban
import time
from random import choice
from AbstractAlgoIA import *

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

    def __init__(self, board, duration = 5):
        AbstractAlgoIA.__init__(self, board)
        self._itDeepDuration = duration
        self._stopDepth = 1
        self._timeToStop = 0

        self._bestMoves = {}


    #############################################
    #############################################
    ''' public functions for myPlayer '''

    def getMove(self):

        self._timeToStop = time.time() + self._itDeepDuration

        lastMove = None
        run = True

        while run :
            m = self._startAlphaBeta()
            if m != None:
                lastMove = m
                self._stopDepth += 1
            else:
                run = False
                self._stopDepth -= 1 # Annulation du dernier AlphaBeta qui n'a pas terminé pour cause de manque de temps


        return lastMove
    

    #############################################
    #############################################
    ''' Internal functions '''


    def _boardValue(self, isFriendLevel):
        ''' 
        Heuristique d'un plateau de jeu de GO avec 9x9 cases 
        TODO : Avoir un objet pour gérer les heuristiques
        '''
        l = choice([i for i in range(1, 100)])
        if not isFriendLevel:
            l *= -1
        return l

            ####

    def _startAlphaBeta(self):
        isFriendLevel = True
        currentDepth = 1
        possibleMoves = []
        firstMoveToCheck = 0
        maxValue = -1000000 

        moves = super().getLegalMovements()

        for i in range(firstMoveToCheck, len(moves)):
            
            super().push(moves[i]) 
            
            if currentDepth == self._stopDepth:
                valueCurrentMove = self._boardValue(isFriendLevel)
            else:
                valueCurrentMove = self._alphaBeta(currentDepth = currentDepth + 1, 
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

    def _alphaBeta(self, currentDepth, alpha, beta, isFriendLevel):
        if time.time() >= self._timeToStop:
            return None

        if currentDepth == self._stopDepth or super().isGameOver():
            return self._boardValue(isFriendLevel)

        moves = super().getWeakMovements()
        
        firstMove = 0

        for i in range(firstMove, len(moves)):

            if super().push(moves[i]) == False: # Si le mouvement n'est pas légal
                super().pop()
                continue # On passe au mouvement suivant

            retValue = self._alphaBeta(currentDepth = currentDepth + 1, alpha = alpha, beta = beta, 
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