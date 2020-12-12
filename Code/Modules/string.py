

class String:
    def __init__(self, color, liberties, stones):
        self.color = color
        self.liberties = liberties
        self.stones = stones

    def __repr__(self):
        return f"[color={self.color}, liberties={self.liberties}, stones={self.stones}]"
