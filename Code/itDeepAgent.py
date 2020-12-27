#!/usr/bin/python3 +x
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

    On va utiliser {self.__bestMoves} pour restreindre les coups qu'on va utiliser lors des alpha-beta à profondeur > 1.
    Si à profondeur 1, on trouve les coups ['A1', 'B6', 'C7'], alors à profondeur 1+{incrementStep} on va regarder uniquement les 
    sous arbre commencant par ces 3 coups. 
    
    - La profondeur 1 permet de selectionner les coups viables.
    - Les profondeurs suivantes servent à chercher le meilleur coup parmis les coups viables, 
    en réduisant la taille de {self.__bestMoves} de plus en plus.
    '''

    ############################################
    '''             Constructor              '''

    INF = np.inf
    NINF = np.NINF

    def __init__(self, board, color, duration):
        super(ItDeepAgent, self).__init__()

        ''' Le plateau de jeu '''
        self.__board = board
        ''' La durée de recherche d'un coup ''' 
        self.__itDeepDuration = duration
        ''' La profondeur maximum de recherche '''
        self.__maxDepth = 1
        ''' Le temps (dans le futur) où doit s'arrêter l'algorithme '''
        self.__timeToStop = 0
        ''' La couleur de l'IA '''
        self.__myColor = color
        ''' 
        Les meilleurs coups trouvé.
        '''
        self.__bestMoves = []
        ''' L'objet permettant d'évaluer un plateau '''
        self.__evalHandler = None

    @property
    def maxDepth(self):
        return self.__maxDepth

    def get_next_move(self, lastOpponentMove:FlattenMove, evalHandler, incrementStep:int=2) -> FlattenMove:

        # L'algorithme va s'arrêter une fois que time.time() vaut self.__timeToStop
        self.__timeToStop = time.time() + self.__itDeepDuration  
        self.__evalHandler = evalHandler

        # On ne continue pas après la profondeur 5 pour éviter de prendre trop de temps
        while True and self.__maxDepth <= 5:
            print()
            print(f"Start AlphaBeta with depth max at {self.__maxDepth}")
            start = time.time()

            # {moves} contient les meilleurs coups trouvé via l'appel à self._start_alpha_beta
            # {score} contient le score attribué par {evalHandler} aux coups dans {moves}
            moves, score = self._start_alpha_beta(  lastMove=None, 
                                                    depth=self.__maxDepth, 
                                                    alpha=self.NINF, 
                                                    beta=self.INF, 
                                                    maximizingPlayer=True)
            if score is None or len(moves) == 0: # Si l'alpha beta c'est arrêté à cause du manque de temps
                break

            # Pour éviter d'avoir une liste de coup trop grande, on la raccourci dans certain cas
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
            if len(self.__bestMoves) == 1:  # S'il n'y a qu'un seul bon coup, on arrête car refaire un alpha beta dessus ne servirait à rien
                break
            if score == self.INF or score == self.NINF:
                break
        
        if len(self.__bestMoves) == 0:
            return -1

        # On choisi au hasard parmi tous les coups dans {self.__bestMoves}
        moveSelected = choice(self.__bestMoves)
        return moveSelected
        
        return choice(self.__bestMoves)

    def _start_alpha_beta(self, lastMove, depth, alpha, beta, maximizingPlayer):
        # S'il n'y a plus de temps, on retourne {None, None} pour la méthode {self.get_next_move}
        if time.time() >= self.__timeToStop:
            return None, None

        moves = self.__board.weak_legal_useful_moves()
        bestMoves = []
        bestScore = self.NINF if maximizingPlayer else self.NINF

        for m in moves:
            # Si {self.__bestMoves} contient déjà des coups, alors on ne regarde que les sous arbres qui commence par ces coups
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

            # Si {self._alpha_beta} à retourné None, c'est qu'il n'y avait plus de temps et qu'on a dépiler tous les appels
            if value is None:
                return None, None

            # Si la valeur en meilleur, on clear la liste pour ne gardé que le meilleur coup
            if value > bestScore:
                bestScore = value
                bestMoves.clear()
                bestMoves.append(m)
            elif value == bestScore: # Si la valeur est égale, on garde le coup pour avoir une liste des meilleurs coups (qui on une valeur max égale)
                bestMoves.append(m)
        return bestMoves, bestScore


    def _alpha_beta(self, lastMove, depth, alpha, beta, maximizingPlayer):
        # S'il n'y a plus de temps, on dépile les appels en renvoyant None
        if time.time() >= self.__timeToStop:
            return None

        # Calcul de l'heuristique
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

            # On continue de dépiler les appels en renvoyant None si {self._alpha_beta} à renvoyé None
            if currentValue is None:
                return None

            # mise a jour de alpha ou beta
            if maximizingPlayer:
                maxValue = max(maxValue, currentValue)
                alpha = max(alpha, maxValue)
            else:
                maxValue = min(maxValue, currentValue)
                beta = min(beta, maxValue)

            # Coupe alpha beta
            if alpha >= beta:
                return alpha if maximizingPlayer else beta

        return alpha if maximizingPlayer else beta



