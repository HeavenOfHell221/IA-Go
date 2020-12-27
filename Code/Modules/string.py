from Modules.aliasesType import *

class String:
    '''
    Représente une chaine de pierre.
    Utilisé dans MyBoard, et mis à jour en temps réel après chaque push d'un coup sur le board.
    '''
    
    def __init__(self, color:Color, liberties:Set[FlattenMove], stones:Set[FlattenMove]):
        ''' La couleur a qui appartient cette chaine de pierre '''
        self.color = color
        ''' L'ensemble des libertés de cette chaine de pierre '''
        self.liberties = liberties
        ''' L'ensemble des pierres constituant cette chaine de pierre '''
        self.stones = stones

    def __repr__(self):
        from MyGoban import MyBoard
        return f"(liberties={[MyBoard.flat_to_name(l) for l in self.liberties]}, stones={[MyBoard.flat_to_name(m) for m in self.stones]})\n"
