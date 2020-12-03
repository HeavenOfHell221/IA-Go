# -*- coding: utf-8 -*-

import time
from MyGoban import MyBoard
from random import choice
from abstractAlgoIA import AbstractAlgoIA
from Modules.aliasesType import *
from multiprocessing import Process, Array
import numpy as np

class IterativeDeepening(AbstractAlgoIA):

    ############################################
    '''             Constructor              '''

    def __init__(self, board:MyBoard, myColor:int, duration:int):
        super(IterativeDeepening, self).__init__(board)
        self.__itDeepDuration = duration
        self.__stopDepth = 1
        self.__timeToStop = 0
        self.__myColor = myColor

        self.__oracle = {}


    ############################################
    '''   public functions for myPlayer      '''


    def get_next_move(self) -> FlattenMove_None:
        run = True
        moves = []
        scores = []

        self.__timeToStop = time.time() + self.__itDeepDuration

        while run :
            begin = time.time()
            move, score = self._start_alpha_beta(isFriendLevel=True)
            print("Move calculated in : ", round(time.time()-begin, 3), "secondes.")
            if move is not None:
                print("move:", move, ", score:", score, "depth:", self.__stopDepth)
                moves.append(move)
                scores.append(score)
                self.__stopDepth += 1
            else:
                run = False
                self.__stopDepth -= 1 # Annulation du dernier AlphaBeta qui n'a pas terminé pour cause de manque de temps
            
        idxList = np.argwhere(scores == np.amax(scores)).flatten().tolist()
        #print("Moves: ", moves)
        #print("Scores : ", scores)
        #print("idxList : ", idxList)
        maxMove = moves[choice(idxList)]    

        return maxMove
    

    #############################################
    '''         Internal functions            '''


    def _board_value(self, isFriendLevel: bool) -> int:
        ''' Heuristique d'un plateau de jeu de GO avec 9x9 cases '''
        color = super().next_player
        otherColor = super().opponent_color(color)

        nbStone = super().nb_stones(color)
        nbStoneOther = super().nb_stones(otherColor)

        ret = nbStone - nbStoneOther

        return ret if isFriendLevel else ret*-1

        ########

    
    def _start_alpha_beta(self, isFriendLevel:bool) -> FlattenMove_None:
        possibleMoves = []
        possibleScores = []
        currentDepth = 0
        maxValue = -np.inf

        moves = super().weak_eye_legal_moves()

        minRange = 0
        for i in range(minRange, len(moves)):
            m = moves[i]
            if super().push(m) == False: # Si le mouvement n'est pas légal
                super().pop()
                continue # On passe au mouvement suivant
            
            if currentDepth+1 == self.__stopDepth:
                valueCurrentMove = self._board_value(not isFriendLevel)
            
            else:
                valueCurrentMove = self._alpha_beta(lastMove=m, currentDepth=currentDepth+1, 
                                                    alpha=-np.inf, beta=np.inf, isFriendLevel=not isFriendLevel)
            
            super().pop()

            if valueCurrentMove is None: # Si le temps est écoulé
                return None, None

            if valueCurrentMove > maxValue:
                maxValue = valueCurrentMove
                possibleMoves.clear()
                possibleScores.clear()
                possibleMoves.append(m)
                possibleScores.append(valueCurrentMove)
            elif valueCurrentMove == maxValue:
                possibleMoves.append(m)
                possibleScores.append(valueCurrentMove)

        move = choice(possibleMoves)
        idx = possibleMoves.index(move)
        score = possibleScores[idx]

        return move, score

        ########
    

    
    def _alpha_beta(self, lastMove:FlattenMove, currentDepth:int, alpha:int, beta:int, isFriendLevel:bool):

        if time.time() >= self.__timeToStop:
            return None

        if currentDepth == self.__stopDepth or super().is_game_over():
            return self._board_value(isFriendLevel)

        moves = super().weak_eye_legal_moves()
        
        maxValue = (-np.inf) if isFriendLevel else (np.inf)

        minRange = 0
        for i in range(minRange, len(moves)):
            m = moves[i]
            if super().push(m) == False: # Si le mouvement n'est pas légal
                super().pop()
                continue # On passe au mouvement suivant

            currentValue = self._alpha_beta(lastMove=m, currentDepth=currentDepth+1, 
                                            alpha=alpha, beta=beta, isFriendLevel=not isFriendLevel)
            super().pop()

            if currentValue is None:
                return None

            if isFriendLevel:
                maxValue = max(maxValue, currentValue)
                alpha = max(maxValue, alpha)
            else:
                maxValue = min(maxValue, currentValue)
                beta = min(maxValue, beta)

            if alpha >= beta: # On coupe l'arbre
                break

        return maxValue
