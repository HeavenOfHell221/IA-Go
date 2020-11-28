# -*- coding: utf-8 -*-
import time
from MyGoban import MyBoard
from abstractAlgoIA import AbstractAlgoIA
from random import choice, shuffle
from Modules.aliasesType import *
#from threading import Thread
from multiprocessing import Process, Array

import sys

class recursionlimit:
    def __init__(self, limit):
        self.limit = limit
        self.old_limit = sys.getrecursionlimit()

    def __enter__(self):
        sys.setrecursionlimit(self.limit)

    def __exit__(self, type, value, tb):
        sys.setrecursionlimit(self.old_limit)


class MonteCarlo(AbstractAlgoIA):


    ############################################
    '''             Constructor              '''

    def __init__(self, board: MyBoard):
        AbstractAlgoIA.__init__(self, board)

    ############################################
    '''          public functions            '''

    def get_next_move(self) -> FlattenMove:
        isFriendLevel = True
        winRateMax:float = -1.0
        possibleMoves:FlattenMoves = []
        begin = time.time()

        legalMoves = super().legal_moves()
        shuffle(legalMoves)

        #n = round(len(legalMoves)/10)
        threads = []
        begin = time.time()

        n = round(len(legalMoves)/4)

        ratios = Array('d', range(n))

        for i in range(n):
            super().push(legalMoves[i])
            threads.append(WorkerMonteCarloProc(super().deepcopy_board(), ratios,legalMoves[i], i))
            super().pop()

        for i in range(n):
            threads[i].join()

        print(f"Temps écouté pour {n} processus : {round(time.time()-begin, 3)} ")
        #print([r for r in ratios])

        for i in range(0, n):
            winRate = ratios[i]
            if winRate > winRateMax:
                winRateMax = winRate
                possibleMoves.clear()
                possibleMoves.append(legalMoves[i])
            elif winRate == winRateMax:
                possibleMoves.append(legalMoves[i])

        '''
        for i in range(0, round(len(legalMoves)/4)):
            print(f"For move [{super().flat_to_name(legalMoves[i])}]")
            if super().push(legalMoves[i]) == False: 
                super().pop()
                continue 

            win = 0
            lose = 0

            win, lose = self._start_monte_carlo(isFriendLevel)

            super().pop()

            if win+lose > 0:
                winRate:float = win / (win+lose)
            else:
                winRate:float = 0.0
            
            print(f"Win = {win} and lose = {lose} | Total game = {win+lose} ")
            print(f"WinRate = {round(winRate*100, 2)}%")
            print(f"WinRateMax = {round(winRateMax*100, 2)}%")
            print()

            if winRate > winRateMax:
                winRateMax = winRate
                possibleMoves.clear()
                possibleMoves.append(legalMoves[i])
            elif winRate == winRateMax:
                possibleMoves.append(legalMoves[i])
        '''
        print(possibleMoves)
        move = choice(possibleMoves)
        return move

        ########

    def start_monte_carlo(self, isFriendLevel:bool) -> float:
        ''' 
        Pour un coup joué dans get_next_move, joue des parties partie aléatoire jusqu'à gagné ou perdre.
        Return le ratio de victoire.
        Joue {n} parties.
        '''
        legalMoves = super().legal_moves()
        shuffle(legalMoves)

        win = 0
        lose = 0
        n = round(len(legalMoves)/2)

        for i in range(n):
            if super().push(legalMoves[i]) == False: 
                super().pop()
                continue 
            with recursionlimit(1500):
                w , l = self._random_monte_carlo(isFriendLevel = not isFriendLevel)
            win += (w if isFriendLevel else l)
            lose += (l if isFriendLevel else w)
            super().pop()
        
        return round((win/(win+lose)), 2)


    #############################################
    '''         Internal functions            '''
    
    def _random_monte_carlo(self, isFriendLevel:bool):
        ''' Joue à partir d'un plateau donné des coups aux hasard jusqu'à la fin de la partie. '''
        ''' Retourne (1,0) si c'est notre IA qui gagne, (0,1) sinon. '''

        if super().is_game_over():
            return (1, 0) if isFriendLevel else (0, 1)
        win = 0
        lose = 0
        moves = []
        legalMoves = super().legal_moves()

        # Tant qu'il reste au moins 20 coups possibles, on retire le 'PASS' pour ne pas faire durée la partie
        # et ne pas perdre un potentiel avantage
        if len(legalMoves) > 20:
            legalMoves.remove(-1)

        super().push(choice(legalMoves))        
        w , l = self._random_monte_carlo(not isFriendLevel)
        super().pop()
        
        win += (w if isFriendLevel else l)
        lose += (l if isFriendLevel else w)

        return (win, lose)
'''
class WorkerMonteCarloThread(Thread):

    def __init__(self, board:MyBoard, winRate:dict, pid:int):
        Thread.__init__(self)
        self.__mc = MonteCarlo(board)
        self.__winRate = winRate
        self.__pid = pid

    def run(self):
        print(f"Thread {self.__pid} start MonteCarlo ")
        ratio = self.__mc.start_monte_carlo(True, self.__pid)
        self.__winRate[self.__pid] = ratio
        print(f"Thread {self.__pid} finish | ratio = {ratio} ")
'''

class WorkerMonteCarloProc:

    def __init__(self, board:MyBoard, array:Array, move:FlattenMove, i:int):
        self.__p = Process(target=self._run, args=(array, move, i))
        self.__mc = MonteCarlo(board)
        self.__p.start()

    def _run(self, array:Array, move:FlattenMove, i:int):
        print(f"Processus {i} start MonteCarlo with move {self.__mc.flat_to_name(move)} ")
        ratio = self.__mc.start_monte_carlo(True)
        print(f"Processus {i} finish | ratio = {ratio} with move {self.__mc.flat_to_name(move)}")
        array[i] = ratio

    def join(self):
        self.__p.join()
        

    