# -*- coding: utf-8 -*-

import time
from MyGoban import MyBoard
from random import choice, shuffle, uniform
from abstactAgent import AbstactAgent
from Modules.aliasesType import *
import numpy as np
from Modules.colorText import *

class ItDeepAgent(AbstactAgent):
    '''
    IA utilisant Iterative Deepening (et AlphaBeta).
    '''

    ############################################
    '''             Constructor              '''

    INF = np.inf
    NINF = np.NINF

    def __init__(self, board, color, duration):
        super(ItDeepAgent, self).__init__()
        self.__board = board
        self.__itDeepDuration = duration
        self.__maxDepth = 1
        self.__timeToStop = 0
        self.__myColor = color
        self.__bestMoves = []
        self.__evalHandler = None

    @property
    def maxDepth(self):
        return self.__maxDepth

    def get_next_move(self, lastOpponentMove, evalHandler, incrementStep=2):
        self.__timeToStop = time.time() + self.__itDeepDuration  
        self.__evalHandler = evalHandler

        while True and self.__maxDepth <= 5:
            print()
            print(f"Start AlphaBeta with depth max at {self.__maxDepth}")
            start = time.time()
            moves, score = self._start_alpha_beta(  lastMove=None, 
                                                    depth=self.__maxDepth, 
                                                    alpha=self.NINF, 
                                                    beta=self.INF, 
                                                    maximizingPlayer=True)
            if score is None:
                break

            if self.__maxDepth == 1:
                if len(moves) <= 5:
                    self.__bestMoves = moves
                else:
                    shuffle(moves)
                    self.__bestMoves = [moves[i] for i in range(5)]
            elif self.__maxDepth == 3:
                if len(moves) <= 3:
                    self.__bestMoves = moves
                else:
                    shuffle(moves)
                    self.__bestMoves = [moves[i] for i in range(3)]    
            else:
                self.__bestMoves = moves

            print("bestMoves = ", [MyBoard.flat_to_name(m) for m in self.__bestMoves])
            print("bestScore = ", score)
            print(f"In {round(time.time()-start, 2)} secondes")
            
            self.__maxDepth += incrementStep
            if len(self.__bestMoves) == 1:
                break
            if score == self.INF or score == self.NINF:
                break
        
        if len(self.__bestMoves) == 0:
            return -1

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

            value = self._alpha_beta(   lastMove=m, 
                                        depth=depth-1, 
                                        alpha=alpha, 
                                        beta=beta, 
                                        maximizingPlayer=not maximizingPlayer)
            self.__board.pop()

            if value is None:
                return None, None

            if value > bestScore:
                bestScore = value
                bestMoves.clear()
                bestMoves.append(m)
            elif value == bestScore:
                bestMoves.append(m)
        return bestMoves, bestScore


    def _alpha_beta(self, lastMove, depth, alpha, beta, maximizingPlayer):
        if time.time() >= self.__timeToStop:
            return None

        if depth == 0 or self.__board.is_game_over():
            return self.__evalHandler.board_value(  board=self.__board, 
                                                    maxDepth=self.__maxDepth, 
                                                    maximizingPlayer=maximizingPlayer, 
                                                    lastMove=lastMove)

        moves = self.__board.weak_legal_useful_moves()
        maxValue = self.NINF if maximizingPlayer else self.INF

        for m in moves:
            if self.__board.push(m) == False:
                self.__board.pop()
                continue

            currentValue = self._alpha_beta(    lastMove=m, 
                                                depth=depth-1, 
                                                alpha=alpha, 
                                                beta=beta, 
                                                maximizingPlayer=not maximizingPlayer)
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



