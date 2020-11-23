import Goban
import time
from random import choice

class Movement:
    def __init__(self, movement, index):
        self.movement = movement
        self.index = index

    def __repr__(self):
        return f"movement : {Goban.Board.flat_to_name(self.movement)} with index : ({self.index})"

class IterativeDeepening:

    #############################################
    #############################################
    ''' Main '''

    def __init__(self, board):
        self._board = board

    #############################################
    #############################################
    ''' public functions for myPlayer '''

    def getMove(self, itDeepDuration = 1):
        depth = 0
        lastMove = None

        run = True
        timeToStop = time.time() + itDeepDuration

        while run :    
            m = self._startAlphaBeta(stopDepth = depth + 1,timeToStop = timeToStop)
            if m != None:
                lastMove = m
                depth += 1
            else:
                run = False

        return lastMove
    

    #############################################
    #############################################
    ''' Internal functions '''


    def _boardValue(self, isFriendLevel):
        return choice([10, -10, 5, -5, -20, 20, 0, 50, -50, 7, -7, 12, -12])


    def _startAlphaBeta(self, stopDepth, timeToStop):
        currentDepth = 1
        maxValue = -1000000
        possibleMoves = []
        firstMove = 0

        moves = self._board.generate_legal_moves()

        for i in range(firstMove, len(moves)):
            self._push(moves[i])
            if currentDepth == stopDepth :
                valueCurrentMove = self._boardValue(True) 
            else:
                valueCurrentMove = self._alphaBeta( currentDepth    = currentDepth + 1,
                                                    stopDepth       = stopDepth,
                                                    timeToStop      = timeToStop,
                                                    alpha           = -1000000,
                                                    beta            = 1000000,
                                                    isFriendLevel   = True)
            self._pop()

            if valueCurrentMove == None:
                return None

            if valueCurrentMove > maxValue:
                maxValue = valueCurrentMove
                possibleMoves.clear()
                possibleMoves.append(moves[i])
            elif valueCurrentMove == maxValue:
                possibleMoves.append(moves[i])

        move = choice(possibleMoves)
        return move


    def _alphaBeta(self, currentDepth, stopDepth, timeToStop, alpha, beta, isFriendLevel):
        if time.time() >= timeToStop:
            return None

        if currentDepth == stopDepth or self._board.is_game_over():
            return self._boardValue(isFriendLevel)

        moves = self._board.weak_legal_moves()
        
        firstMove = 0

        for i in range(firstMove, len(moves)):
            if self._push(moves[i]) == False:
                self._pop()
                continue

            value = self._alphaBeta(    currentDepth    = currentDepth + 1,
                                        stopDepth       = stopDepth,
                                        timeToStop      = timeToStop,
                                        alpha           = alpha,
                                        beta            = beta,
                                        isFriendLevel   = not isFriendLevel)
            
            self._pop()
            
            if value == None:
                return None

            if isFriendLevel:
                alpha = max(alpha, value)
            else:
                beta = min(beta, value)

            if alpha >= beta :
                return (beta if isFriendLevel else alpha)

        return (alpha if isFriendLevel else beta)


    #############################################
    #############################################
    ''' Delegation Goban functions '''
    
    def _push(self, move):
        return self._board.push(move)

    def _pop(self):
        self._board.pop()
    





