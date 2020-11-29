# -*- coding: utf-8 -*-
import time
from MyGoban import MyBoard
from abstractAlgoIA import AbstractAlgoIA
from random import choice, shuffle
from Modules.aliasesType import *
from Modules.recursionLimit import RecursionLimit
from multiprocessing import Process, Array
import os

NB_CPU = len(os.sched_getaffinity(0)) - 1


class MonteCarlo(AbstractAlgoIA):


    ############################################
    '''             Constructor              '''

    def __init__(self, board: MyBoard):
        AbstractAlgoIA.__init__(self, board)

    ############################################
    '''          public functions            '''

    def get_next_move(self) -> FlattenMove:
        winRateMax:float = -1.0
        possibleMoves:FlattenMoves = []

        legalMoves = super().legal_moves()
        shuffle(legalMoves)

        ratios = Array('d', range(len(legalMoves)))
        n = min(len(legalMoves), NB_CPU)
        min_n = 0
        max_n = n

        while max_n < len(legalMoves):
            self._run_multiprocessing(ratios, legalMoves, winRateMax, min_n, max_n)
            min_n = max_n
            max_n += n 

        for i in range(0, min_n):
            winRate = ratios[i]
            if winRate > winRateMax:
                winRateMax = winRate
                possibleMoves.clear()
                possibleMoves.append(legalMoves[i])
            elif winRate == winRateMax:
                possibleMoves.append(legalMoves[i])
        
        return choice(possibleMoves)

        ########

    def start_monte_carlo(self, isFriendLevel:bool) -> float:
        ''' 
        Pour un coup joué dans get_next_move, joue des parties partie aléatoire jusqu'à gagné ou perdre.
        Return le ratio de victoire.
        Joue {n} parties.
        '''
        weakLegalMoves = super().weak_legal_moves()
        shuffle(weakLegalMoves)

        win = 0
        lose = 0
        n = min(40, len(weakLegalMoves))

        for i in range(n):
            if super().push(weakLegalMoves[i]) == False: 
                super().pop()
                continue 
            with RecursionLimit(1500):
                w , l = self._random_monte_carlo(isFriendLevel = not isFriendLevel)
            win += (w if isFriendLevel else l)
            lose += (l if isFriendLevel else w)
            super().pop()
        
        return round((win/(win+lose)), 2)


    #############################################
    '''         Internal functions            '''
    
    def _run_multiprocessing(self, ratios:Array, legalMoves:FlattenMoves, winRateMax:float, begin:int, end:int) -> None:
        isFriendLevel = True
        possibleMoves:FlattenMoves = []
        process = []
        t1 = time.time()

        for i in range(begin, end):
            super().push(legalMoves[i])
            worker = WorkerMonteCarlo(super().deepcopy_board(), ratios, legalMoves[i], i)
            process.append(worker)
            worker.start()
            super().pop()

        for i in range(begin, end):
            process[i-begin].join()

        print(f"Temps écouté pour {end-begin} processus : {round(time.time()-t1, 3)} ")


        ########


    def _random_monte_carlo(self, isFriendLevel:bool) -> Tuple[int, int]:
        ''' Joue à partir d'un plateau donné des coups aux hasard jusqu'à la fin de la partie. '''
        ''' Retourne (1,0) si c'est notre IA qui gagne, (0,1) sinon. '''

        otherColor = super().switch_color(super().next_player())
        nbLiberties = super().nb_liberties(super().next_player())
        nbLiberties_Other = super().nb_liberties(otherColor)

        if nbLiberties < 0 or nbLiberties_Other < 0:
            print(nbLiberties, nbLiberties_Other)
            super().pretty_print()
        assert nbLiberties >= 0 and nbLiberties_Other >= 0

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


    ###############################################
    ###############################################
    ###############################################


class WorkerMonteCarlo:

    def __init__(self, board:MyBoard, array:Array, move:FlattenMove, i:int):
        self.__p = Process(target=self._exec, args=(array, move, i))
        self.__mc = MonteCarlo(board)

        ########

    def _exec(self, array:Array, move:FlattenMove, i:int) -> None:
        print(f"Processus {i} start MonteCarlo with move {self.__mc.flat_to_name(move)} ")
        
        ratio = self.__mc.start_monte_carlo(True)
        array[i] = ratio
        
        print(f"Processus {i} finish | ratio = {ratio} with move {self.__mc.flat_to_name(move)}")
        
        ########

    def join(self) -> None:
        self.__p.join()

        ########

    def start(self) -> None:
        self.__p.start()
        

    