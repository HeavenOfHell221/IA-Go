# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this! '''

import time
from MyGoban import MyBoard 
from random import choice
from playerInterface import PlayerInterface
from iterativeDeepening import IterativeDeepening as ItDeep

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy! '''
    
    def __init__(self):
        self._board = MyBoard()
        self._mycolor = None

    def getPlayerName(self):
        return "Gab & Yo"

    def newGame(self, color):
        self._mycolor = color
        self._opponent = MyBoard.flip(color)
    
    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"

        itDeep = ItDeep(self._board)
        move = itDeep.get_next_move() 

        self._board.push(move)
        self._display_move(move)
        return MyBoard.flat_to_name(move) # move is an internal representation. To communicate with the interface I need to change if to a string

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(MyBoard.name_to_flat(move)) 

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

    def _display_move(self, move):
        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.pretty_print()