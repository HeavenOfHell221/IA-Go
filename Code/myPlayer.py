# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this! '''

import time
from MyGoban import MyBoard 
from random import choice
from playerInterface import PlayerInterface
from iterativeDeepening import IterativeDeepening as ItDeep
from monteCarlo import MonteCarlo 
from gameOpening import GameOpening

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy! '''
    
    ############################################
    '''             Constructor              '''

    def __init__(self):
        self._board = MyBoard()
        self._myColor = None
        self._opponent = None
        self._currentAlgo = None

    ############################################
    '''          public functions            '''

    def getPlayerName(self):
        return "Gab & Yo"

        ########

    def newGame(self, color):
        self.__init__()
        self._myColor = color
        self._opponent = MyBoard.flip(color)

        ########
    
    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        move = self._get_move()
        self._board.push(move)
        self._display_move(move)
        return MyBoard.flat_to_name(move) # move is an internal representation. To communicate with the interface I need to change if to a string

        ########

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        m = MyBoard.name_to_flat(move)
        self._board.push(m) 

        ########

    def endGame(self, winner):
        if self._myColor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")


    #############################################
    '''         Internal functions            '''


    def _display_move(self, move):
        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.pretty_print()

        ########

    def _get_move(self):
        self._currentAlgo = ItDeep(board=self._board, color=self._myColor, duration=7)
        move = self._currentAlgo.get_next_move()
        return move

    