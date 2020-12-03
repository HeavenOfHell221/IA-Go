from dataclasses import dataclass
from aliasesType import *

@dataclass(init=True, repr=True, eq=False, order=False, unsafe_hash=False, frozen=False)
class Movement:
    ''' Représente un mouvement à jouer '''
    self.move:FlattenMove
    self.index:int
    self.depth:int
    self.score:int