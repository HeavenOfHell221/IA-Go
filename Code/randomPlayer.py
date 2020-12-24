# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this! '''

import time
from MyGoban import MyBoard 
from random import choice
from playerInterface import PlayerInterface
from itDeepAgent import ItDeepAgent
from randomAgent import RandomAgent

class myPlayer(PlayerInterface):
    
    ############################################
    '''             Constructor              '''

    def __init__(self):
        self._board = MyBoard()
        self._myColor = None
        self._opponent = None
        self._nbMove = 0
        self._lastOpponentMove = None

    ############################################
    '''          public functions            '''

    def getPlayerName(self):
        return "Random player"

    def newGame(self, color):
        self.__init__()
        self._myColor = color
        self._opponent = MyBoard.flip(color)
    
    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        move = self._get_move()
        self._board.push(move)
        self._nbMove += 1
        return MyBoard.flat_to_name(move) # move is an internal representation. To communicate with the interface I need to change if to a string

        ########

    def playOpponentMove(self, move):
        m = MyBoard.name_to_flat(move)
        self._board.push(m) 
        self._lastOpponentMove = move
        self._nbMove +=1

        ########

    def endGame(self, winner):
        if self._myColor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")


    #############################################
    '''         Internal functions            '''

    def _get_move(self):
        agent = RandomAgent(board=self._board)
        move = agent.get_next_move(lastOpponentMove=self._lastOpponentMove, evalHandler=None)
        return move

