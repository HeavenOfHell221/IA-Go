# -*- coding: utf-8 -*-

import time
from MyGoban import MyBoard
from random import choice, shuffle, uniform
from abstactAgent import AbstactAgent
from Modules.aliasesType import *
import numpy as np

class ItDeepAgent(AbstactAgent):

    ############################################
    '''             Constructor              '''

    INF = np.inf
    NINF = np.NINF

    def __init__(self, board:MyBoard, color:int, duration:int):
        super(ItDeepAgent, self).__init__()
        self.__board = board
        self.__itDeepDuration = duration
        self.__maxDepth = 1
        self.__timeToStop = 0
        self.__myColor = color
        self.__bestMoves = []

    
    def get_next_move(self):
        self.__timeToStop = time.time() + self.__itDeepDuration  
        
        while True and self.__maxDepth <= 9:
            print()
            print(f"Start AlphaBeta with depth max at {self.__maxDepth}")
            beta = time.time()
            moves, score = self._start_alpha_beta(lastMove=None, depth=self.__maxDepth, alpha=self.NINF, beta=self.INF, maximizingPlayer=True)
            if score is None:
                break
            self.__bestMoves = moves
            self.__maxDepth += 2
            print(f"Best move is {[MyBoard.flat_to_name(m) for m in self.__bestMoves]} with score : {score} in {round(time.time()-beta, 2)} secondes")
            if len(self.__bestMoves) == 1:
                break
            if score == self.INF or score == self.NINF:
                break
        
        moveSelected = choice(self.__bestMoves)
        return moveSelected
        
        return choice(self.__bestMoves)

    def _start_alpha_beta(self, lastMove, depth, alpha, beta, maximizingPlayer):
        if time.time() >= self.__timeToStop:
            return None, None

        moves = self.__board.weak_legal_useful_moves()
        bestMoves = []
        bestScore = self.NINF if maximizingPlayer else self.NINF

        for m in moves:
            if len(self.__bestMoves) > 0 and m not in self.__bestMoves:
                continue

            if self.__board.push(m) == False:
                self.__board.pop()
                continue

            value = self._alpha_beta(lastMove=m, depth=depth-1, alpha=alpha, beta=beta, maximizingPlayer=not maximizingPlayer)
            self.__board.pop()

            if value is None:
                return None, None

            if value > bestScore:
                bestScore = value
                bestMoves.clear()
                bestMoves.append(m)
            elif value == bestScore:
                bestMoves.append(m)

        b = [MyBoard.flat_to_name(m) for m in bestMoves]
        print("bestMoves = ", b)
        print("bestScore = ", bestScore)
        return bestMoves, bestScore


    def _alpha_beta(self, lastMove, depth, alpha, beta, maximizingPlayer):
        if time.time() >= self.__timeToStop:
            return None

        if depth == 0 or self.__board.is_game_over():
            return self._board_value(maximizingPlayer, lastMove)

        moves = self.__board.weak_legal_useful_moves()
        maxValue = self.NINF if maximizingPlayer else self.INF

        for m in moves:
            if self.__board.push(m) == False:
                self.__board.pop()
                continue

            currentValue = self._alpha_beta(m, depth-1, alpha, beta, not maximizingPlayer)
            self.__board.pop()
            if currentValue is None:
                return None

            if maximizingPlayer:
                maxValue = max(maxValue, currentValue)
                alpha = max(alpha, maxValue)
            else:
                maxValue = min(maxValue, currentValue)
                beta = min(beta, maxValue)

            if alpha >= beta:
                return alpha if maximizingPlayer else beta

        return alpha if maximizingPlayer else beta


    def _board_value(self, maximizingPlayer, lastMove):
        ''' Heuristique d'un plateau de jeu de GO avec 9x9 cases '''

        if maximizingPlayer:
            color = self.__board.nextPlayer
            otherColor = MyBoard.flip(color)
        else:
            otherColor = self.__board.nextPlayer
            color = MyBoard.flip(otherColor)
        
        if self.__board.is_game_over():
            return self.INF

        nbStone = self.__board.nb_stones(color)
        nbStoneOther = self.__board.nb_stones(otherColor)
        nbLiberties = self.__board.nb_liberties(color)
        nbLibertiesOther = self.__board.nb_liberties(otherColor)
        nbStrings = self.__board.len_strings(color)
        nbStringsOther = self.__board.len_strings(otherColor)

        bestCell_0 = ['C7', 'G7', 'C3', 'G3']
        bestCell_1 = ['E2', 'E8', 'B5', 'H5']
        bestCell_2 = ['E5']
        worstCell_0 = ['A1', 'J1', 'A9', 'J9']
        worstCell_1 = ['A2', 'B2', 'B1', 'H1', 'H2', 'J2', 'H8', 'H9', 'J8', 'B8', 'B9', 'A8']
    
        m = self.__board.flat_to_name(lastMove)
        score = 0

        if m == 'PASS':
            return self.NINF

        if m in bestCell_0:
            score += 3
        elif m in bestCell_1:
            score += 2
        elif m in bestCell_2:
            score += 1
        elif m in worstCell_1:
            score -= 1
        elif m in worstCell_0:
            score -= 3

        # Maximiser le ratio de liberté (entre -10 et 10)
        if nbLibertiesOther > 0:
            score += round((((nbLiberties / (nbLibertiesOther + nbLiberties)) * 2) - 1) * 10, self.__maxDepth)

        # Maximiser le ratio de pierre (entre -10 et 10)
        if nbStoneOther > 0:
            score += round((((nbStone / (nbStoneOther + nbStone)) * 2) - 1) * 10, self.__maxDepth)

        # Minimiser le ratio de string
        #if nbStrings > 0:
        #    score += (np.clip(nbStringsOther / nbStrings, 0.8, 1.2) - 1)

        # Maximiser les weakStrings
        (nb_my_weakStrings_1, nb_other_weakStrings_1) = self.__board.compute_weak_strings_k_liberties(color, 1)
        (nb_my_weakStrings_2, nb_other_weakStrings_2) = self.__board.compute_weak_strings_k_liberties(color, 2)
        (nb_my_weakStrings_3, nb_other_weakStrings_3) = self.__board.compute_weak_strings_k_liberties(color, 3)

        if nb_my_weakStrings_1 > 0:
            score -= 5
        elif nb_my_weakStrings_2 > 0:
            score -= 2
        elif nb_my_weakStrings_3 > 0:
            score -= 1
        
        if nb_other_weakStrings_1 > 0:
            score += 4
        elif nb_other_weakStrings_2 > 0:
            score += 2
        elif nb_other_weakStrings_3 > 0:
            score += 1

        if self.__maxDepth <= 1:
            return round(score, 1)
        elif self.__maxDepth <= 3:
            return round(score, 3)

        return score