from abc import ABC as AbstractClass
from abc import abstractmethod 
from MyGoban import MyBoard

class AbstractGobanEval:
    '''
    Représente un objet qui permet d'évaluer un Goban.
    '''

    def __init__(self):
        pass

    @abstractmethod
    def board_value(self, board, maxDepth, maximizingPlayer, lastMove) -> float:
        '''
        Evalue le board {board}, et retourne une valeur.
        
        Plus la valeur est grande, plus {board} est bon.
        Plus la valeur est faible, plus {board} est mauvais.
        '''
        pass

