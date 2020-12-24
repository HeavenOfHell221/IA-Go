
class String:
    def __init__(self, color, liberties, stones):
        self.color = color
        self.liberties = liberties
        self.stones = stones

    def __repr__(self):
        from MyGoban import MyBoard
        return f"(liberties={[MyBoard.flat_to_name(l) for l in self.liberties]}, stones={[MyBoard.flat_to_name(m) for m in self.stones]})\n"
