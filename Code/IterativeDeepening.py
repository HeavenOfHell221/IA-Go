import Goban
import time
from random import choice

# CurrentDepth impair => Niveau Ami (1, 3, ..)
# CurrentDepth pair => Niveau Ennemi (0, 2, 4, ..)

class Movement:

    def __init__(self, move = None, index = None, depth = 0, score = 0):
        self.move = move
        self.index = index
        self.depth = depth
        self.score = score

    def __repr__(self):
        return f"move=[{self.move}], index=[{self.index}], depth=[{self.depth}], score=[{self.score}]"

class IterativeDeepening:

    #############################################
    #############################################
    ''' Main '''

    def __init__(self, board, duration = 15):
        self._board = board
        self._itDeepDuration = duration
        self._stopDepth = 1
        self._timeToStop = 0

        self._bestMoves = {}

    #############################################
    #############################################
    ''' public functions for myPlayer '''

    def getMove(self):

        # Quand "self._timeToStop >= time.time()" sera vrai, alors il ce sera écoulé {self._itDeepDuration} seconde(s)
        self._timeToStop = time.time() + self._itDeepDuration

        lastMove = None
        run = True

        while run :
            m = self._startAlphaBeta()
            if m != None:
                lastMove = m
                self._stopDepth += 1
            else:
                run = False
                self._stopDepth -= 1 # Annulation du dernier AlphaBeta qui n'a pas terminé pour cause de manque de temps


        return lastMove
    

    #############################################
    #############################################
    ''' Internal functions '''


    def _boardValue(self, isFriendLevel):
        ''' 
        Heuristique d'un plateau de jeu de GO avec 9x9 cases 
        TODO : Avoir un objet pour gérer les heuristiques
        '''
        if isFriendLevel:
            l = [i for i in range(1, 100)]
            return choice(l)
        else:
            l = [i for i in range(-100, -1)]
            return choice(l)



    def _startAlphaBeta(self):
        isFriendLevel = True
        currentDepth = 1
        possibleMoves = []
        firstMoveToCheck = 0
        maxValue = -1000000 

        moves = self._board.generate_legal_moves()

        for i in range(firstMoveToCheck, len(moves)):
            
            self._push(moves[i]) 
            
            if currentDepth == self._stopDepth:
                valueCurrentMove = self._boardValue(isFriendLevel)
            else:
                valueCurrentMove = self._alphaBeta(currentDepth = currentDepth + 1, 
                                                    alpha = -1000000, beta = 1000000, 
                                                    isFriendLevel = not isFriendLevel)
            
            self._pop()

            if valueCurrentMove == None: # Si le temps est écoulé
                return None

            if valueCurrentMove > maxValue:
                maxValue = valueCurrentMove
                possibleMoves.clear()
                possibleMoves.append(moves[i])
            elif valueCurrentMove == maxValue:
                possibleMoves.append(moves[i])

        move = choice(possibleMoves)
        return move


    def _alphaBeta(self, currentDepth, alpha, beta, isFriendLevel):
        if time.time() >= self._timeToStop:
            return None

        if currentDepth == self._stopDepth or self._board.is_game_over():
            return self._boardValue(isFriendLevel)

        ''' 
        Plutot que de tester 2 fois si un mouvement est legal (ce qui coûte très chère), 
        on prend le risque d'utiliser des mouvements weak.
        De toute manière, le mouvement est testé pendant le push, donc pas besoin de tester avant... 
        Si il est weak, on pop et on passe au suivant, c'est beaucoup plus rentable.
        '''
        moves = self._board.weak_legal_moves()
        
        firstMove = 0

        '''if currentDepth in self._bestMoves:
            firstMove = self._bestMoves[currentDepth].index'''

        for i in range(firstMove, len(moves)):

            if self._push(moves[i]) == False: # Si le mouvement n'est pas légal
                self._pop()
                continue # On passe au mouvement suivant

            retValue = self._alphaBeta(currentDepth = currentDepth + 1, alpha = alpha, beta = beta, 
                                    isFriendLevel = not isFriendLevel)
            
            self._pop()
            
            if retValue == None:
                return None

            if isFriendLevel:
                alpha = max(alpha, retValue)
            else:
                beta = min(beta, retValue)
                
                '''
                if currentDepth in self._bestMoves:
                    if self._bestMoves[currentDepth].score < retValue:
                        self._bestMoves[currentDepth] = Movement(moves[i], i, currentDepth, retValue)
                else:
                    self._bestMoves[currentDepth] = Movement(moves[i], i, currentDepth, retValue)
                '''

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
    





