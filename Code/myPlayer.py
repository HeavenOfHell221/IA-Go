# -*- coding: utf-8 -*-

import time
from MyGoban import MyBoard 
from random import choice
from playerInterface import PlayerInterface
from itDeepAgent import ItDeepAgent
from myGobanEval import MyGobanEval
from Modules.colorText import *

class myPlayer(PlayerInterface):

    '''
    Notre Player actuel.
    Utilise l'agent ItDeepAgent, contenu dans itDeepAgent.py.
    Utilise l'heuristique MyGobanEval, contenu dans myGobanEval.py.
    '''

    ############################################
    '''             Constructor              '''

    def __init__(self):
        self._board = MyBoard()
        self._myColor = None
        self._opponentColor = None
        self._nbMove = 0
        self._lastMove = None
        self._lastOpponentMove = None
        self._timeRemaining = 298

    ############################################
    '''          public functions            '''

    def getPlayerName(self):
        return "if(Gab && Yo) print(\"Let's GO\")"

    def newGame(self, color):
        self.__init__()
        self._myColor = color
        self._opponentColor = MyBoard.flip(color)
    
    def getPlayerMove(self):
        print(f"{Normal_Green}")
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"

        print(self._board.compute_territory(self._myColor))

        move = self._get_move()
        self._board.push(move)
        self._lastMove = move

        self._board.pretty_print()
        print(f"{Normal_White}")

        self._nbMove += 1
        return MyBoard.flat_to_name(move) # move is an internal representation. To communicate with the interface I need to change if to a string

    def playOpponentMove(self, move):
        m = MyBoard.name_to_flat(move)
        self._board.push(m) 
        self._nbMove += 1
        self._lastOpponentMove = move

    def endGame(self, winner):
        if self._myColor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

    #############################################
    '''         Internal functions            '''

    def _get_move(self):

        ''' Durée d'Iterative Deepening '''

        if self._timeRemaining > 150: # 300 et 151
            if self._nbMove < 30:
                duration = 15
            elif self._nbMove < 60:
                duration = 20
            else:
                duration = 25
        elif self._timeRemaining > 60: # 150 et 61
            if self._nbMove < 30:
                duration = 10
            elif self._nbMove < 60:
                duration = 15
            else:
                duration = 20
        elif self._timeRemaining > 30: # 60 et 31
            duration = 10
        else: #10 et 0
            duration = 1

        timeBegin = time.time()
        agent = ItDeepAgent(board=self._board, color=self._myColor, duration=min(duration, self._timeRemaining))
        move = agent.get_next_move(lastOpponentMove=self._lastOpponentMove, evalHandler=MyGobanEval(), incrementStep=2)
        timeEnd = time.time()

        self._timeRemaining -= (timeEnd - timeBegin) 
        print(f"{round(self._timeRemaining, 2)} secondes remaining.")

        if self._timeRemaining <= 0:
            return -1

        return move

