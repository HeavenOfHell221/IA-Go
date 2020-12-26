from abstractGobanEval import AbstractGobanEval

class MyGobanEval(AbstractGobanEval):
    def __init__(self):
        pass

    def board_value(self, board, maxDepth, maximizingPlayer, lastMove):
        ''' Heuristique d'un plateau de jeu de GO avec 9x9 cases '''
        from MyGoban import MyBoard

        ''' Récupération des couleurs suivant la profondeur d'où est calculé l'heuristique '''
        if maximizingPlayer:
            color = board.nextPlayer
            otherColor = MyBoard.flip(color)
        else:
            otherColor = board.nextPlayer
            color = MyBoard.flip(otherColor)


        if board.is_game_over():
            return board.INF if not maximizingPlayer else board.NINF
        
        ''' Passer son tour n'est jamais bien '''
        if lastMove == -1:
            return board.NINF if not maximizingPlayer else board.INF

        
        m = board.flat_to_name(lastMove)
        data = board.get_data(color, otherColor)
        col, line = board.name_to_coord(m)
        score = 0

        if col in [3, 4, 5]:
            score += 2
        if line in [3, 4, 5]:
            score += 2

        if col == 4:
            score += 1
        if line == 4:
            score += 1

        if m in ['F3', 'D3', 'E5', 'D7', 'G5', 'C6', 'D6', 'C4', 'C5', 'G6', 'C7', 'H7', 'C3', 'H3']:
            score += 2
        elif m in ['G4', 'G6', 'C6', 'E3', 'D7', 'D6', 'F7', 'E7', 'D3']:
            score += 1
        elif m in ['A2', 'A1', 'B1', 'H1', 'J1', 'J2', 'H9', 'J9', 'J8', 'A9', 'A8', 'B9']:
            score -= 2

        if board.is_useless(lastMove, color):
            score -= 35

        if data['other_nbStones'] > 0:
            score += (((data['my_nbStones'] / (data['my_nbStones'] + data['other_nbStones'])) * 2) - 1) * 50

        #score -= (data['other_nbStrings'] + data['my_nbStrings']) * 3
        score -= data['my_nbStrings'] * 4

        if data['my_nbWeakStrings1'] > 0:
            score -= 100
        if data['my_nbWeakStrings2'] > 0:
            score -= 50
        if data['my_nbWeakStrings3'] > 0:
            score -= 30
        if data['my_nbWeakStrings4'] > 0:
            score -= 10

        if data['other_nbWeakStrings1'] > 0:
            score += 100
        if data['other_nbWeakStrings2'] > 0:
            score += 50
        if data['other_nbWeakStrings3'] > 0:
            score += 30
        if data['other_nbWeakStrings4'] > 0:
            score += 10

        myLiberties = board.get_liberties(color)
        opLiberties = board.get_liberties(otherColor)

        for lbt in myLiberties:
            n, no = board.nb_shared_liberty(color, lbt)
            if n == 2 and no == 0:
                score += 4
            elif n == 3 and no <= 1:
                score += 6
            if no >= 2:
                score -= 3
            
        for lbt in opLiberties:
            n, no = board.nb_shared_liberty(otherColor, lbt)
            if no > 0:
                score += 3

        t_onlyColor, t_onlyOpColor, t_color, t_opColor, t_dangerous = board.compute_territory(color)
        score += (t_onlyColor*3 + t_color) - (t_onlyOpColor*2 + t_opColor) + min(20, t_dangerous)
    
        myStrings = board.get_strings(color)
        for s in myStrings:
            if len(s.liberties) >= 15:
                score += 8
            elif len(s.liberties) >= 10:
                score += 4
            elif len(s.liberties) >= 5:
                score += 2

        if maxDepth <= 1:
            return round(score/10)*10 if not maximizingPlayer else -round(score/10)*10
            
        return round(score, 6) if not maximizingPlayer else -round(score, 6)
