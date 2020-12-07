# -*- coding: utf-8 -*-

import time
from MyGoban import MyBoard
from random import choice, shuffle
from abstractAlgoIA import AbstractAlgoIA
from Modules.aliasesType import *
import numpy as np

class IterativeDeepening(AbstractAlgoIA):

    ############################################
    '''             Constructor              '''

    INF = np.inf
    NINF = np.NINF

    def __init__(self, board:MyBoard, color, duration:int):
        super(IterativeDeepening, self).__init__(board)
        self.__itDeepDuration = duration
        self.__maxDepth = 1
        self.__timeToStop = 0
        self.__myColor = color


    def get_next_move(self):
        self.__timeToStop = time.time() + self.__itDeepDuration  
        maxMoves = []
        maxScores = []

        while True and self.__maxDepth < 20:
            print()
            print(f"Start AlphaBeta with depth max at {self.__maxDepth}")
            beta = time.time()
            move, score = self._start_alpha_beta(lastMove=None, depth=self.__maxDepth, alpha=self.NINF, beta=self.INF, maximizingPlayer=True)
            if score is None:
                break
            print(f"Best move is {super(IterativeDeepening, self).flat_to_name(move)} with score : {score} in {round(time.time()-beta, 2)} secondes")
            self.__maxDepth += 2
            maxMoves.append(move)
            maxScores.append(score)

        idxList = np.argwhere(maxScores == np.amax(maxScores)).flatten().tolist()
        moveSelected = maxMoves[choice(idxList)]   
        print("moveSelected = ", super(IterativeDeepening, self).flat_to_name(moveSelected))
        return moveSelected
        

    def _start_alpha_beta(self, lastMove, depth, alpha, beta, maximizingPlayer):
        if time.time() >= self.__timeToStop:
            return None, None

        moves = super().weak_eye_legal_moves()
        bestMoves = []
        bestScore = self.NINF

        for m in moves:
            if super().push(m) == False:
                super().pop()
                continue

            value = self._alpha_beta(lastMove=m, depth=depth-1, alpha=alpha, beta=beta, maximizingPlayer=not maximizingPlayer)
            super().pop()

            if value is None:
                return None, None

            if value > bestScore:
                bestScore = value
                bestMoves.clear()
                bestMoves.append(m)
            elif value == bestScore:
                bestMoves.append(m)

        b = [super(IterativeDeepening, self).flat_to_name(m) for m in bestMoves]
        print("bestMoves = ", b)
        print("bestScore = ", bestScore)
        return choice(bestMoves), bestScore


    def _alpha_beta(self, lastMove, depth, alpha, beta, maximizingPlayer):
        if time.time() >= self.__timeToStop:
            return None

        if super().is_game_over():
            return self.INF if super().winner != super().next_player else self.NINF

        if depth == 0:
            return self._board_value(maximizingPlayer, lastMove)

        moves = super().weak_eye_legal_moves()

        maxValue = self.NINF if maximizingPlayer else self.INF

        for m in moves:
            if super().push(m) == False:
                super().pop()
                continue

            currentValue = self._alpha_beta(m, depth-1, alpha, beta, not maximizingPlayer)
            super().pop()
            if currentValue is None:
                return None

            if maximizingPlayer:
                maxValue = max(maxValue, currentValue)
                alpha = max(alpha, maxValue)
            else:
                maxValue = min(maxValue, currentValue)
                beta = min(beta, maxValue)

            if alpha >= beta:
                return maxValue

        return maxValue


    def _board_value(self, maximizingPlayer, lastMove):
        ''' Heuristique d'un plateau de jeu de GO avec 9x9 cases '''

        color = self.__myColor
        otherColor = super().opponent_color(color)

        nbStone = super().nb_stones(color)
        nbStoneOther = super().nb_stones(otherColor)

        l0 = ['C7', 'G7', 'C3', 'G3']
        l1 = ['A1', 'J1', 'A9', 'J9']
        l2 = ['A2', 'B2', 'B1', 'H1', 'H2', 'J2', 'H8', 'H9', 'J8', 'B8', 'B9', 'A8']
        l3 = ['C1', 'D1', 'E1', 'F1', 'G1', 'H3', 'H4', 'H5', 'H6', 'H7', 'C9', 'D9', 'E9', 'F9', 'G9', 'A3', 'A4', 'A5', 'A6', 'A7']
    

        m = super().flat_to_name(lastMove)

        score = 1000
        
        if lastMove == -1:
            return -score

        if m in l0:
            score *= 1.2
        elif m in l1:
            score *= 0.2
        elif m in l2:
            score *= 0.3
        elif m in l3:
            score *= 0.5

        nb_my_weakStrings, nb_other_weakStrings = self.get_nb_weak_strings(color)
       
        if nb_my_weakStrings > 0:
            score *= (nb_other_weakStrings / nb_my_weakStrings)*5

        if nbStoneOther > 0:
            score *= min((nbStone / nbStoneOther), 1.25)
        
        return round(score) if not maximizingPlayer else -round(score)




    def get_nb_weak_strings(self, color):
        weakStrings = super().weak_strings()

        nb_my_weakStrings = 0
        nb_other_weakStrings = 0

        for s in weakStrings:
            if s.color == color:
                nb_my_weakStrings += 1
            else:
                nb_other_weakStrings += 1

        return nb_my_weakStrings, nb_other_weakStrings
