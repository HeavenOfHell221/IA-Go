# -*- coding: utf-8 -*-

''' This is a class to play small games of GO, natively coded in Python.
    I tried to use nice data structures to speed it up (union & find, Zobrist hashs, 
    numpy memory efficient ...)

    Licence is MIT: you can do whatever you want with the code. But keep my name somewhere.
    
    (c) Laurent SIMON 2019 -- 2020

    Known Limitations:
     - No early detection of endgames (only stops when no stone can be put on the board, or superKo)
     - Final scoring does not remove dead stones, and thus may differ from a more smart counting.
       You may want to end the game only when all the areas are almost filled.


    References and Code inspirations
    --------------------------------

    I looked around in the web for inspiration. One important source of inspiration (some of my python lines
    may be directly inspired by him is the fantastic github repo and book (which I bought :)) of Max Pumperla 
    about Deep Learning and the game of Go
    
    https://github.com/maxpumperla/deep_learning_and_the_game_of_go 
    
    I tried to be faster by using more non python data structures (limiting lists and sets), however :)

    '''

from __future__ import print_function # Used to help cython work well
import numpy as np
import random

def getProperRandom():
    ''' Gets a proper 64 bits random number (ints in Python are not the ideal toy to play with int64)'''
    return np.random.randint(np.iinfo(np.int64).max, dtype='int64') 

class MyBoard:
    ''' GO MyBoard class to implement your (simple) GO player.'''

    __VERSION__ = 2.2
    __BLACK = 1
    __WHITE = 2
    __EMPTY = 0
    __BOARDSIZE = 9 # Used in static methods, do not write it
    __DEBUG = True 

    ##########################################################
    ##########################################################
    ''' A set of functions to manipulate the moves from the
    - internal representation, called "flat", in 1D (just integers)
    - coord representation on the board (0,0)..(__BOARDSIZE, __BOARDSIZE)
    - name representation (A1, A2, ... D5, D6, ..., PASS)'''

    @staticmethod
    def flatten(coord):
        ''' Static method that teturns the flatten (1D) coordinates given the 2D coordinates (x,y) on the board. It is a
        simple helper function to get x*__BOARDSIZE + y. 
        
        Internally, all the moves are flatten. If you use legal_moves or weak_legal_moves, it will produce flatten
        coordinates.''' 
        if coord == (-1,-1): return -1
        return MyBoard.__BOARDSIZE * coord[1] + coord[0]

    @staticmethod
    def unflatten(fcoord):
        if fcoord == -1: return (-1, -1)
        d = divmod(fcoord, MyBoard.__BOARDSIZE)
        return d[1], d[0]

    @staticmethod
    def name_to_coord(s):
        if s == 'PASS': return (-1,-1)
        indexLetters = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'J':8}

        col = indexLetters[s[0]]
        lin = int(s[1:]) - 1
        return (col, lin )

    @staticmethod
    def name_to_flat(s):
        return MyBoard.flatten(MyBoard.name_to_coord(s))

    @staticmethod
    def coord_to_name(coord):
        if coord == (-1,-1): return 'PASS'
        letterIndex = "ABCDEFGHJ"
        return letterIndex[coord[0]]+str(coord[1]+1)

    @staticmethod
    def flat_to_name(fcoord):
        if fcoord == -1: return 'PASS'
        return MyBoard.coord_to_name(MyBoard.unflatten(fcoord))

    ##########################################################
    ##########################################################
    '''Just a couple of helper functions about who has to play next'''

    @staticmethod
    def flip(player):
        if player == MyBoard.__BLACK:
            return MyBoard.__WHITE
        return MyBoard.__BLACK

    @staticmethod
    def player_name(player):
        if player == MyBoard.__BLACK:
            return "black"
        elif player == MyBoard.__WHITE:
            return "white"
        return "???"

    ##########################################################
    ##########################################################

    def __init__(self):
        ''' Main constructor. Instantiate all non static variables.'''
        self._winner = MyBoard.__EMPTY
        self._nbWHITE = 0
        self._nbBLACK = 0
        self._capturedWHITE = 0
        self._capturedBLACK = 0

        self._nbLiberties = {MyBoard.__WHITE:0 , MyBoard.__BLACK:0}
        self._nbStrings = {MyBoard.__WHITE:0 , MyBoard.__BLACK:0}

        self._nextPlayer = self.__BLACK
        self._board = np.zeros((MyBoard.__BOARDSIZE**2), dtype='int8')

        self._lastPlayerHasPassed = False
        self._gameOver = False

        self._stringUnionFind = np.full((MyBoard.__BOARDSIZE**2), -1, dtype='int8')
        self._stringLiberties = np.full((MyBoard.__BOARDSIZE**2), -1, dtype='int8')
        self._stringSizes = np.full((MyBoard.__BOARDSIZE**2), -1, dtype='int8')

        self._stonesBLACK = set()
        self._stonesWHITE = set()
        self._empties = set(range(MyBoard.__BOARDSIZE **2))

        # Zobrist values for the hashes. I use np.int64 to be machine independant
        self._positionHashes = np.empty((MyBoard.__BOARDSIZE**2, 2), dtype='int64')
        for x in range(MyBoard.__BOARDSIZE**2):
            for c in range(2):
                self._positionHashes[x][c] = getProperRandom()
        self._currentHash = getProperRandom() 
        self._passHash = getProperRandom() 

        self._seenHashes = set()

        self._historyMoveNames = []
        self._trailMoves = [] # data structure used to push/pop the moves

        #Building fast structures for accessing neighborhood
        self._neighbors = []
        self._neighborsEntries = []
        for nl in [self._get_neighbors(fcoord) for fcoord in range(MyBoard.__BOARDSIZE**2)] :
            self._neighborsEntries.append(len(self._neighbors))
            for n in nl:
                self._neighbors.append(n)
            self._neighbors.append(-1) # Sentinelle
        self._neighborsEntries = np.array(self._neighborsEntries, dtype='int16')
        self._neighbors = np.array(self._neighbors, dtype='int8')



    ##########################################################
    ##########################################################
    ''' Simple helper function to directly access the board.
    if b is a MyBoard(), you can ask for b[m] to get the value of the corresponding cell,
    (0 for Empty, 1 for Black and 2 for White, see MyBoard.__BLACK,__WHITE,__EMPTY values)
    If you want to have an access via coordinates on the board you can use it like
    b[MyBoard.flatten((x,y))]

    '''
    def __getitem__(self, key):
        ''' Helper access to the board, from flatten coordinates (in [0 .. MyBoard.BOARDSIZE**2]). 
        Read Only array. If you want to add a stone on the board, you have to use
        _put_stone().'''
        return self._board[key]

    def __len__(self):
        return MyBoard.__BOARDSIZE**2

    def __str__(self):
        ''' WARNING: this print function does not reflect the classical coordinates. It represents the internal
        values in the board.'''
        toreturn=""
        for i,c in enumerate(self._board):
            toreturn += self._piece2str(c) + " " # +'('+str(i)+":"+str(self._stringUnionFind[i])+","+str(self._stringLiberties[i])+') '
            if (i+1) % MyBoard.__BOARDSIZE == 0:
                toreturn += "\n"
        toreturn += "Next player: " + ("BLACK" if self._nextPlayer == self.__BLACK else "WHITE") + "\n"
        toreturn += str(self._nbBLACK) + " blacks and " + str(self._nbWHITE) + " whites on board\n"
        return toreturn


    ##########################################################
    ##########################################################
    ''' Main functions for generating legal moves '''

    def is_game_over(self):
        ''' Checks if the game is over, ie, if you can still put a stone somewhere'''
        return self._gameOver

    def legal_moves(self):
        '''
        Produce a list of moves, ie flatten moves. They are integers representing the coordinates on the board. To get
        named Move (like A1, D5, ..., PASS) from these moves, you can use the function MyBoard.flat_to_name(m).

        This function only produce legal moves. That means that SuperKO are checked BEFORE trying to move (when
        populating the returned list). This can
        only be done by actually placing the stone, capturing strigns, ... to compute the hash of the board. This is
        extremelly costly to check. Thus, you should use weak_legal_moves that does not check the superko and actually
        check the return value of the push() function that can return False if the move was illegal due to superKo.
        '''
        moves = [m for m in self._empties if not self._is_suicide(m, self._nextPlayer) 
                and not self._is_super_ko(m, self._nextPlayer)[0]]
        moves.append(-1) # We can always ask to pass
        return moves

    def weak_legal_moves(self):
        '''
        Produce a list of moves, ie flatten moves. They are integers representing the coordinates on the board. To get
        named Move (like A1, D5, ..., PASS) from these moves, you can use the function MyBoard.flat_to_name(m).
        Can generate illegal moves, but only due to Super KO position. In this generator, KO are not checked.
        If you use a move from this list, you have to check if push(m) was True or False and then immediatly pop 
        it if it is False (meaning the move was superKO.'''
        moves = [m for m in self._empties if not self._is_suicide(m, self._nextPlayer)]
        moves.append(-1) # We can always ask to pass
        return moves

    def generate_legal_moves(self):
        ''' See legal_moves description. This is just a wrapper to this function, kept for compatibility.'''
        return self.legal_moves()

    def move_to_str(self, m):
        ''' Transform the internal representation of a move into a string. Simple wrapper, but useful for 
        producing general code.'''
        return MyBoard.flat_to_name(m)

    def str_to_move(self, s):
        ''' Transform a move given as a string into an internal representation. Simple wrapper here, but may be
        more complex in other games.'''
        return MyBoard.name_to_flat(s)

    def play_move(self, fcoord):
        ''' Main internal function to play a move. 
        Checks the superKo, put the stone then capture the other color's stones.
        Returns True if the move was ok, and False otherwise. If False is returned, there was no side effect.
        In particular, it checks the superKo that may not have been checked before.
        
        You can call it directly but the push/pop mechanism will not be able to undo it. Thus in general, 
        only push/pop are called and this method is never directly used.'''
    
        if self._gameOver: return
        if fcoord != -1:  # pass otherwise
            alreadySeen, tmpHash = self._is_super_ko(fcoord, self._nextPlayer)
            if alreadySeen: 
                self._historyMoveNames.append(self.flat_to_name(fcoord))
                return False
            captured = self._put_stone(fcoord, self._nextPlayer)

            # captured is the list of Strings that have 0 liberties
            for fc in captured:
                self._capture_string(fc)

            assert tmpHash == self._currentHash
            self._lastPlayerHasPassed = False
            if self._nextPlayer == self.__WHITE:
                self._nbWHITE += 1
            else:
                self._nbBLACK += 1
        else:
            if self._lastPlayerHasPassed:
                self._gameOver = True
                self._winner = self._nextPlayer
            else:
                self._lastPlayerHasPassed = True
            self._currentHash ^= self._passHash

        self._seenHashes.add(self._currentHash)
        self._historyMoveNames.append(self.flat_to_name(fcoord))
        self._nextPlayer = MyBoard.flip(self._nextPlayer)

        if MyBoard.__DEBUG:
            assert len(self._stonesBLACK) == self._nbBLACK
            assert len(self._stonesWHITE) == self._nbWHITE

        return True
    
    def reset(self):
        self.__init__()

    ##########################################################
    ##########################################################
    ''' Helper functions for pushing/poping moves. You may want to use them in your game tree traversal'''

    def push(self, m):
        ''' 
        push: used to push a move on the board. More costly than play_move() 
        but you can pop it after. Helper for your search tree algorithm'''
        assert not self._gameOver
        self._pushBoard()
        return self.play_move(m)

    def pop(self):
        '''
        pop: another helper function for you rsearch tree algorithm. If a move has been pushed, 
        you can undo it by calling pop
        '''
        hashtopop = self._currentHash
        self._popBoard()
        if hashtopop in self._seenHashes:
            self._seenHashes.remove(hashtopop)

    ##########################################################
    ##########################################################

    def result(self):
        '''
        The scoring mechanism is fixed but really costly. It may be not a good idea to use it as a heuristics. 
        It is the chinese area scoring that computes the final result. It uses the same notation as in chess:
        Returns:
        - "1-0" if WHITE wins
        - "0-1" if BLACK wins
        - "1/2-1/2" if DEUCE


        Known problems: dead stones are not removed, so the score only stricly apply the area rules. You may want 
        to keep playing to consolidate your area before computing the scores.
        '''
        score = self._count_areas()
        score_black = self._nbBLACK + score[0]
        score_white = self._nbWHITE + score[1]
        if score_white > score_black:
            return "1-0"
        elif score_white < score_black:
            return "0-1"
        else:
            return "1/2-1/2"

    def compute_score(self):
        ''' Computes the score (chinese rules) and return the scores for (blacks, whites) in this order'''
        score = self._count_areas()
        return (self._nbBLACK + score[0], self._nbWHITE + score[1])

    def final_go_score(self):
        ''' Returns the final score in a more GO-like way.'''
        score_black, score_white = self.compute_score()
        if score_white > score_black:
            return "W+"+str(score_white-score_black)
        elif score_white < score_black:
            return "B+"+str(score_black-score_white)
        else:
            return "0"
       
    def pretty_print(self):
        if MyBoard.__BOARDSIZE not in [5,7,9]:
            print(self)
            return
        print()
        print("To Move: ", "black" if self._nextPlayer == MyBoard.__BLACK else "white")
        print("Last player has passed: ", "yes" if self._lastPlayerHasPassed else "no")
        print()
        print("     WHITE (O) has captured %d stones" % self._capturedBLACK)
        print("     BLACK (X) has captured %d stones" % self._capturedWHITE)
        print()
        print("     WHITE (O) has %d stones" % self._nbWHITE)
        print("     BLACK (X) has %d stones" % self._nbBLACK)
        print()
        if MyBoard.__BOARDSIZE == 9:
            specialPoints = [(2,2), (6,2), (4,4), (2,6), (6,6)]
            headerline = "    A B C D E F G H J"
        elif MyBoard.__BOARDSIZE == 7:
            specialPoints = [(2,2), (4,2), (3,3), (2,4), (4,4)]
            headerline = "    A B C D E F G"
        else:
            specialPoints = [(1,1), (3,1), (2,2), (1,3), (3,3)]
            headerline = "    A B C D E"
        print(headerline)
        for l in range(MyBoard.__BOARDSIZE):
            line = MyBoard.__BOARDSIZE - l
            print("  %d" % line, end="")
            for c in range(MyBoard.__BOARDSIZE):
                p = self._board[MyBoard.flatten((c, MyBoard.__BOARDSIZE - l - 1))]
                ch = '.'
                if p==MyBoard.__WHITE:
                    ch = 'O'
                elif p==MyBoard.__BLACK:
                    ch = 'X'
                elif (l,c) in specialPoints:
                    ch = '+'
                print(" " + ch, end="")
            print(" %d" % line)
        print(headerline)
        print("hash = ", self._currentHash)


    ##########################################################
    ##########################################################
    ##########################################################
    ##########################################################

    ''' Internal functions only'''

    def _pushBoard(self):
        currentStatus = []
        currentStatus.append(self._winner)
        currentStatus.append(self._stonesWHITE.copy())
        currentStatus.append(self._stonesBLACK.copy())
        currentStatus.append(self._nbLiberties.copy())
        currentStatus.append(self._nbStrings.copy())
        currentStatus.append(self._nbWHITE)
        currentStatus.append(self._nbBLACK)
        currentStatus.append(self._capturedWHITE)
        currentStatus.append(self._capturedBLACK)
        currentStatus.append(self._nextPlayer)
        currentStatus.append(self._board.copy())
        currentStatus.append(self._gameOver)
        currentStatus.append(self._lastPlayerHasPassed)
        currentStatus.append(self._stringUnionFind.copy())
        currentStatus.append(self._stringLiberties.copy())
        currentStatus.append(self._stringSizes.copy())
        currentStatus.append(self._empties.copy())
        currentStatus.append(self._currentHash)
        self._trailMoves.append(currentStatus)

    def _popBoard(self):
        oldStatus = self._trailMoves.pop()
        self._currentHash = oldStatus.pop()
        self._empties = oldStatus.pop()
        self._stringSizes = oldStatus.pop()
        self._stringLiberties = oldStatus.pop()
        self._stringUnionFind = oldStatus.pop()
        self._lastPlayerHasPassed = oldStatus.pop()
        self._gameOver = oldStatus.pop()
        self._board = oldStatus.pop()
        self._nextPlayer = oldStatus.pop()
        self._capturedBLACK = oldStatus.pop()
        self._capturedWHITE = oldStatus.pop()
        self._nbBLACK = oldStatus.pop()
        self._nbWHITE = oldStatus.pop()
        self._nbStrings = oldStatus.pop()
        self._nbLiberties = oldStatus.pop()
        self._stonesBLACK = oldStatus.pop()
        self._stonesWHITE = oldStatus.pop()
        self._winner = oldStatus.pop()
        self._historyMoveNames.pop()

    def _getPositionHash(self, fcoord, color):
        return self._positionHashes[fcoord][color-1]

    # Used only in init to build the neighborsEntries datastructure
    def _get_neighbors(self, fcoord):
        x, y = MyBoard.unflatten(fcoord)
        neighbors = ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
        return [MyBoard.flatten(c) for c in neighbors if self._is_on_board(c[0], c[1])]

    # for union find structure, recover the number of the current string of stones
    def _getStringOfStone(self, fcoord):
        # In the union find structure, it is important to route all the nodes to the root
        # when querying the node. But in Python, using the successive array is really costly
        # so this is not so clear that we need to use the successive collection of nodes
        # Moreover, not rerouting the nodes may help for backtracking on the structure 
        successives = []
        while self._stringUnionFind[fcoord] != -1:
            fcoord = self._stringUnionFind[fcoord]
            successives.append(fcoord)
        if len(successives) > 1:
            for fc in successives[:-1]:
                self._stringUnionFind[fc] = fcoord
        return fcoord

    def _merge_strings(self, str1, str2):
        self._stringLiberties[str1] += self._stringLiberties[str2]
        self._stringLiberties[str2] = -1
        self._stringSizes[str1] += self._stringSizes[str2]
        self._stringSizes[str2] = -1
        assert self._stringUnionFind[str2] == -1
        self._stringUnionFind[str2] = str1

    def _put_stone(self, fcoord, color):
        self._board[fcoord] = color
        self._currentHash ^= self._getPositionHash(fcoord, color)
        if self.__DEBUG:
            assert fcoord in self._empties
        self._empties.remove(fcoord)

        if self._nextPlayer == MyBoard.__WHITE:
            self._stonesWHITE.add(fcoord)
        else:
            self._stonesBLACK.add(fcoord)

        otherColor = MyBoard.flip(color)
        nbEmpty = 0
        nbSameColor = 0
        nbOtherColor = 0
        i = self._neighborsEntries[fcoord]
        while self._neighbors[i] != -1:
            n = self._board[self._neighbors[i]]
            if  n == MyBoard.__EMPTY:
                nbEmpty += 1
            elif n == color:
                nbSameColor += 1
            elif n == otherColor:
                nbOtherColor += 1
            i += 1

        currentString = fcoord
        self._stringLiberties[currentString] = nbEmpty              
        self._stringSizes[currentString] = 1
        self._nbLiberties[color] += (nbEmpty - nbSameColor)
        self._nbLiberties[otherColor] -= (nbOtherColor)
        self._nbStrings[color] += 1

        stringWithNoLiberties = [] # String to capture (if applies)
        i = self._neighborsEntries[fcoord]
        while self._neighbors[i] != -1:
            fn = self._neighbors[i]
            if self._board[fn] == color: # We may have to merge the strings
                stringNumber = self._getStringOfStone(fn)
                self._stringLiberties[stringNumber] -= 1
                if currentString != stringNumber:
                    self._merge_strings(stringNumber, currentString)
                    self._nbStrings[color] -= 1
                currentString = stringNumber
            elif self._board[fn] != MyBoard.__EMPTY: # Other color
                stringNumber = self._getStringOfStone(fn)
                self._stringLiberties[stringNumber] -= 1
                if self._stringLiberties[stringNumber] == 0:
                    if stringNumber not in stringWithNoLiberties: # We may capture more than one string
                        stringWithNoLiberties.append(stringNumber)
                        self._nbStrings[otherColor] -= 1
            i += 1

        return stringWithNoLiberties

    def _is_on_board(self,x,y):
        return x >= 0 and x < MyBoard.__BOARDSIZE and y >= 0 and y < MyBoard.__BOARDSIZE

    def _is_suicide(self, fcoord, color):
        opponent = MyBoard.flip(color)
        i = self._neighborsEntries[fcoord]
        libertiesFriends = {}
        libertiesOpponents = {}
        while self._neighbors[i] != -1:
            fn = self._neighbors[i]
            if self._board[fn] == MyBoard.__EMPTY:
                return False
            string = self._getStringOfStone(fn)
            if self._board[fn] == color: # check that we don't kill the whole zone
                if string not in libertiesFriends:
                    libertiesFriends[string] = self._stringLiberties[string] - 1
                else:
                    libertiesFriends[string] -= 1
            else:
                if MyBoard.__DEBUG:
                    assert self._board[fn] == opponent
                if string not in libertiesOpponents:
                    libertiesOpponents[string] = self._stringLiberties[string] - 1
                else:
                    libertiesOpponents[string] -= 1
            i += 1

        for s in libertiesOpponents:
            if libertiesOpponents[s] == 0:
                return False # At least one capture right after this move, it is legal

        if len(libertiesFriends) == 0: # No a single friend there...
            return True

        # Now checks that when we connect all the friends, we don't create
        # a zone with 0 liberties
        sumLibertiesFriends = 0
        for s in libertiesFriends:
            sumLibertiesFriends += libertiesFriends[s]
        if sumLibertiesFriends == 0:
            return True # At least one friend zone will be captured right after this move, it is unlegal

        return False

    
    def _is_super_ko(self, fcoord, color):
        '''
        Checks if the move leads to an already seen board
        By doing this, it has to "simulate" the move, and thus
        it computes also the sets of strings to be removed by the move.
        Check if it is a complex move (if it takes at least a stone) 
        '''
        tmpHash = self._currentHash ^ self._getPositionHash(fcoord, color)
        assert self._currentHash == tmpHash ^ self._getPositionHash(fcoord, color)
        i = self._neighborsEntries[fcoord]
        libertiesOpponents = {}
        opponent = MyBoard.flip(color)
        while self._neighbors[i] != -1:
            fn = self._neighbors[i]
            #print("superko looks at ", self.coord_to_name(fn), "for move", self.coord_to_name(fcoord))
            if self._board[fn] == opponent:
                s = self._getStringOfStone(fn)
                #print("superko sees string", self.coord_to_name(s))
                if s not in libertiesOpponents:
                    libertiesOpponents[s] = self._stringLiberties[s] - 1
                else:
                    libertiesOpponents[s] -= 1
            i += 1

        for s in libertiesOpponents:
            if libertiesOpponents[s] == 0:
                #print("superko computation for move ", self.coord_to_name(fcoord), ":")
                for fn in self._breadthSearchString(s):
                    #print(self.coord_to_name(fn)+" ", end="")
                    assert self._board[fn] == opponent
                    tmpHash ^= self._getPositionHash(fn, opponent)
                #print()

        if tmpHash in self._seenHashes:
            return True, tmpHash
        return False, tmpHash

    def _breadthSearchString(self, fc):
        ''' A partir d'une coordonnée, fabrique une chaine d'une même couleur (dont EMPTY) '''
        color = self._board[fc]
        string = set([fc])
        frontier = [fc]
        while frontier:
            current_fc = frontier.pop()
            string.add(current_fc)
            i = self._neighborsEntries[current_fc]
            while self._neighbors[i] != -1:
                fn = self._neighbors[i]
                i += 1
                if self._board[fn] == color and not fn in string:
                    frontier.append(fn)
        return string

    def _count_areas(self):
        ''' Costly function that computes the number of empty positions that only reach respectively BLACK  and WHITE
        stones (the third values is the number of places touching both colours)'''
        to_check = self._empties.copy() # We need to check all the empty positions
        only_blacks = 0
        only_whites = 0
        others = 0
        while len(to_check) > 0:
            s = to_check.pop()
            ssize = 0
            assert self._board[s] == MyBoard.__EMPTY
            frontier = [s]
            touched_blacks, touched_whites = 0, 0
            currentstring = []
            while frontier:
                current = frontier.pop()
                currentstring.append(current)
                ssize += 1 # number of empty places in this loop
                assert current not in to_check
                i = self._neighborsEntries[current]
                while self._neighbors[i] != -1:
                    n = self._neighbors[i]
                    i += 1
                    if self._board[n] == MyBoard.__EMPTY and n in to_check:
                        to_check.remove(n)
                        frontier.append(n)
                    elif self._board[n] == MyBoard.__BLACK:
                        touched_blacks += 1
                    elif self._board[n] == MyBoard.__WHITE:
                        touched_whites += 1
            # here we have gathered all the informations about an empty area
            assert len(currentstring) == ssize
            assert (self._nbBLACK == 0 and self._nbWHITE == 0) or touched_blacks > 0 or touched_whites > 0
            if touched_blacks == 0 and touched_whites > 0:
                only_whites += ssize
            elif touched_whites == 0 and touched_blacks > 0:
                only_blacks += ssize
            else:
                others += ssize
        return (only_blacks, only_whites, others)

    def _piece2str(self, c):
        if c==self.__WHITE:
            return 'O'
        elif c==self.__BLACK:
            return 'X'
        else:
            return '.'


    '''
    Internally, the board has a redundant information by keeping track of strings of stones.
    '''
    def _capture_string(self, fcoord):
        # The Union and Find data structure can efficiently handle 
        # the string number of which the stone belongs to. However,
        # to recover all the stones, given a string number, we must 
        # search for them.
        string = self._breadthSearchString(fcoord)
        for s in string:
            if self._nextPlayer == MyBoard.__WHITE:
                self._capturedBLACK += 1
                self._nbBLACK -= 1
                self._stonesBLACK.remove(s)
            else:
                self._capturedWHITE += 1
                self._nbWHITE -= 1
                self._stonesWHITE.remove(s)
            self._currentHash ^= self._getPositionHash(s, self._board[s])
            self._board[s] = self.__EMPTY
            self._empties.add(s)

            i = self._neighborsEntries[s]
            while self._neighbors[i] != -1:
                fn = self._neighbors[i]
                if self._board[fn] != MyBoard.__EMPTY:
                    st = self._getStringOfStone(fn)
                    if st != s:
                        self._stringLiberties[st] += 1
                        if self._board[fn] == MyBoard.__BLACK:
                            self._nbLiberties[MyBoard.__BLACK] += 1
                        else:
                            self._nbLiberties[MyBoard.__WHITE] += 1
                i += 1

            self._stringUnionFind[s] = -1
            self._stringSizes[s] = -1
            self._stringLiberties[s] = -1


    ''' Internal wrapper to full_play_move. Simply translate named move into
    internal coordinates system'''
    def _play_named_move(self, m):
        if m != "PASS":
            return self.play_move(MyBoard.name_to_flat(m))
        else:
            return self.play_move(-1)

    def _draw_cross(self, x,y,w):
        toret = '<line x1="'+str(x-w)+'" y1="'+str(y)+'" x2="'+str(x+w)+'" y2="'+str(y)+'" stroke-width="3" stroke="black" />'
        toret += '<line x1="'+str(x)+'" y1="'+str(y-w)+'" x2="'+str(x)+'" y2="'+str(y+w)+'" stroke-width="3" stroke="black" />'
        return toret

    def _create_svg_representation(self):
        
        text_width=20
        nb_cells = self.__BOARDSIZE 
        circle_width = 16
        border = 20
        width = 40
        wmax = str(width*(nb_cells-1) + border)
        
        board ='<svg height="'+str(text_width+border*2+(nb_cells-1)*width)+'" '+\
        ' width="'+str(text_width+border*2+(nb_cells-1)*width)+'" > '
        
        # The ABCD... line
        board += '<svg height="'+str(text_width)+'" width="' + str(text_width + border*2+(nb_cells-1)*width)+'">'
        letters = "ABCDEFGHJ"
        il = 0
        for i in range(border+text_width-5, text_width-5+border+nb_cells*width, width):
            board+= '<text x="'+str(i)+'" y="18" font-size="24" font-color="black">'+letters[il]+'</text>'
            il += 1
            #board += '<rect x=0 y=0 width=20 height=10 stroke="black" />'
        board += '</svg>'
        
        # The line numbers
        il = 0
        board += '<svg width="'+str(text_width)+'" height="' + str(text_width + border*2+(nb_cells-1)*width)+'">'
        for i in range(border+text_width+7, text_width+7+border+nb_cells*width, width):
            board+= '<text y="'+str(i)+'" x="0" font-size="24" font-color="black">'+str(9-il)+'</text>'
            il += 1
            #board += '<rect x=0 y=0 width=20 height=10 stroke="black" />'
        board += '</svg>'
        
        
        # The board by itself
        board += ' <svg x="'+str(text_width)+'" y="'+str(text_width)+'" height="' + \
        str(text_width+width*(nb_cells-1) + 2*border) + '" width="' + \
        str(text_width+width*(nb_cells-1) + 2*border) + '" > ' + \
        '<rect x="0" y="0" width="'+str(width*(nb_cells-1)+2*border)+'" height="' + str(width*(nb_cells-1)+ 2*border) + '" fill="#B4927A" />\
        <line x1="'+str(border)+'" y1="'+str(border)+'" x2="'+str(border)+'" y2="'+ wmax +'" stroke-width="4" stroke="black"/>\
        <line x1="' + wmax + '" y1="' + str(border) + '" x2="' + str(border) + '" y2="' + str(border) + '" stroke-width="4" stroke="black"/>\
        <line x1="' + wmax + '" y1="' + wmax + '" x2="' + wmax + '" y2="' + str(border) + '" stroke-width="4" stroke="black"/>\
        <line x1="' + str(border) + '" y1="' + wmax + '" x2="' + wmax + '" y2="' + wmax + '" stroke-width="4" stroke="black"/>'
        
        board += self._draw_cross(border+4*width, border+4*width, width/3)
        board += self._draw_cross(border+2*width, border+2*width, width/3)
        board += self._draw_cross(border+6*width, border+6*width, width/3)
        board += self._draw_cross(border+2*width, border+6*width, width/3)
        board += self._draw_cross(border+6*width, border+2*width, width/3)
    
        for i in range(border+width, width*(nb_cells-2)+2*border, width):
            board += '<line x1="'+str(i)+'" y1="'+str(border)+'" x2="'+str(i)+'" y2="' + wmax + '" stroke-width="2" stroke="#444444"/>'
            board += '<line y1="'+str(i)+'" x1="'+str(border)+'" y2="'+str(i)+'" x2="' + wmax + '" stroke-width="2" stroke="#444444"/>'

            
        # The stones    

        pieces = [(x,y,self._board[MyBoard.flatten((x,y))]) for x in range(self.__BOARDSIZE) for y in range(self.__BOARDSIZE) if
                self._board[MyBoard.flatten((x,y))] != MyBoard.__EMPTY]
        for (x,y,c) in pieces:
            board += '<circle cx="'+str(border+width*x) + \
                '" cy="'+str(border+width*(nb_cells-y-1))+'" r="' + str(circle_width) + \
                '" stroke="#333333" stroke-width="3" fill="' + \
                ("black" if c==1 else "white") +'" />'

        board += '</svg></svg>'
        #'\    <text x="100" y="100" font-size="30" font-color="black"> Hello </text>\
        return board


    ################################################################
    ################################################################
    ################################################################
    ################################################################

    ''' Extension du Goban original '''

    @property
    def currentHash(self) -> int:
        ''' MyBoard._currentHash property. Get current hash of the current board. '''
        return self._currentHash

        ########

    @property
    def nbStoneWHITE(self) -> int:
        ''' MyBoard._nbWHITE property. Get the number of white stone. '''
        return self._nbWHITE

        ########

    @property
    def nbStoneBLACK(self) -> int:
        ''' MyBoard._nbWHITE property. Get the number of black stone. '''
        return self._nbBLACK

        ########

    @property
    def next_player(self):
        return self._nextPlayer

        ########

    def nb_stones(self, color:int) -> int:
        if color == MyBoard.__WHITE:
            return self._nbWHITE
        elif color == MyBoard.__BLACK:
            return self._nbBLACK
        else:
            return (MyBoard.__BOARDSIZE - (self._nbBLACK + self._nbWHITE))

        ########

    def nb_liberties_at(self, fcoord:int) -> int:
        ''' MyBoard._stringLiberties property. Get the number of liberties for a stone at the coordinates {fcoord}.'''
        return self._stringLiberties[fcoord] 

        ########

    def nb_liberties(self, color:int) -> int:
        return self._nbLiberties[color] 

        ########

    def nb_strings(self, color:int) -> int:
        return self._nbStrings[color]

        ########

    def stones_list(self, color:int) -> set:
        assert color != MyBoard.__EMPTY
        if color == MyBoard.__BLACK:
            return self._stonesBLACK
        else:
            return self._stonesWHITE

        ########

    @property
    def winner(self):
        if MyBoard.__DEBUG:
            assert self._winner != MyBoard.__EMPTY 
        return self._winner

        ########

    @property
    def EMPTY(self):
        return self.__EMPTY

        ########

    def is_eye(self, fcoord, color) -> bool:
        if self._board[fcoord] is not None:
            return False

        i = self._neighborsEntries[fcoord]
        while self._neighbors[i] != -1:
            n = self._neighbors[i]
            if n != color:
                return False
            i += 1
        
        x, y  = unflatten(fcoord)
        corners = []
        friendly_corner = 0
        off_board_corner = 0

        if self._is_on_board(x+1, y+1):
            corners.append(flatten((x+1, y+1)))
        else:
            off_board_corner += 1
        if self._is_on_board(x+1, y-1):
            corners.append(flatten((x+1, y-1)))
        else:
            off_board_corner += 1
        if self._is_on_board(x-1, y+1):
            corners.append(flatten((x-1, y+1)))
        else: 
            off_board_corner += 1
        if self._is_on_board(x-1, y-1):
            corners.append(flatten((x-1, y-1)))
        else:
            off_board_corner += 1

        for c in corners:
            if self._board[fcoord] == color:
                friendly_corner += 1

        if off_board_corners > 0:
            return ((off_board_corners + friendly_corners) == 4)
        return (friendly_corners >= 3)

       

