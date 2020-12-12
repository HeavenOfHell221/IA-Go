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
        #moves2 = self.__board.weak_legal_moves()
        #print(f"Weak_Legal_Moves        : {[MyBoard.flat_to_name(m) for m in moves2]}")
        #print(f"Weak_Legal_Useful_Moves : {[MyBoard.flat_to_name(m) for m in moves]}")
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

        if self.__board.is_game_over():
            return self.INF if self.__board.winner == self.__myColor else self.NINF

        if depth == 0:
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
                return maxValue

        return maxValue


    def _board_value(self, maximizingPlayer, lastMove):
        ''' Heuristique d'un plateau de jeu de GO avec 9x9 cases '''

        if maximizingPlayer:
            color = self.__board.nextPlayer
            othercolor = MyBoard.flip(color)
        else:
            otherColor = self.__board.nextPlayer
            color = MyBoard.flip(otherColor)
        
        nbStone = self.__board.nb_stones(color)
        nbStoneOther = self.__board.nb_stones(otherColor)
        nbLiberties = self.__board.nb_liberties(color)
        nbLibertiesOther = self.__board.nb_liberties(otherColor)
        nbStrings = self.__board.len_strings(color)
        nbStringsOther = self.__board.len_strings(otherColor)


        l0 = ['C7', 'G7', 'C3', 'G3']
        l1 = ['A1', 'J1', 'A9', 'J9']
        l2 = ['A2', 'B2', 'B1', 'H1', 'H2', 'J2', 'H8', 'H9', 'J8', 'B8', 'B9', 'A8']
        l3 = ['C1', 'D1', 'E1', 'F1', 'G1', 'H3', 'H4', 'H5', 'H6', 'H7', 'C9', 'D9', 'E9', 'F9', 'G9', 'A3', 'A4', 'A5', 'A6', 'A7']
    
        m = self.__board.flat_to_name(lastMove)

        score = 1000
        mult = 1

        if lastMove == -1:
            return 0

        if m in l0:
            mult += 0.4
        elif m in l1:
            score -= 0.1
        elif m in l2:
            score -= 0.2
        elif m in l3:
            score -= 0.4

        # Maximiser le ratio de liberté (entre -1 et 1)
        if nbLibertiesOther > 0:
            mult += (((nbLiberties / (nbLibertiesOther + nbLiberties)) * 2) - 1) 

        # Maximiser le ratio de pierre (entre -2 et 2)
        if nbStoneOther > 0:
            mult += (((nbStone / (nbStoneOther + nbStone)) * 2) - 1) * 2

        # Minimiser le ratio de string
        if nbStrings > 0:
            mult += (np.clip(nbStringsOther / nbStrings, 0.8, 1.2) - 1)

        # Maximiser les weakStrings
        nb_my_weakStrings_1, nb_other_weakStrings_1 = self.__board.compute_weak_strings_k_liberties(color, 1)
        nb_my_weakStrings_2, nb_other_weakStrings_2 = self.__board.compute_weak_strings_k_liberties(color, 2)
        nb_my_weakStrings_3, nb_other_weakStrings_3 = self.__board.compute_weak_strings_k_liberties(color, 3)

        if nb_my_weakStrings_1 > 0:
            mult -= 1
        if nb_my_weakStrings_2 > 0:
            mult -= 0.5
        if nb_my_weakStrings_3 > 0:
            mult -= 0.25

        if nb_other_weakStrings_1 > 0:
            mult += 2
        if nb_other_weakStrings_2 > 0:
            mult += 1
        if nb_other_weakStrings_3 > 0:
            mult += 0.5
        

        #nbDiff = len(self.__board.weak_legal_moves()) - len(self.__board.weak_legal_useful_moves())
        #mult += (nbDiff*0.5)

        score *= mult

        if self.__maxDepth <= 1:
            return round(score/10)

        if self.__maxDepth <= 3:
            return round(score, 3) 

        return score