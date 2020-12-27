from abstractGobanEval import AbstractGobanEval

'''
Contient une partie de nos anciennes IA.
Permet de les faire jouer contre notre IA actuelle.
'''


class MediumGobanEval_V1(AbstractGobanEval):
    def __init__(self):
        pass

    def board_value(self, board, maxDepth, maximizingPlayer, lastMove):
        from MyGoban import MyBoard

        m = board.flat_to_name(lastMove)
        
        if board.is_game_over():
            return board.INF if not maximizingPlayer else board.NINF
        
        if m == 'PASS':
            return board.NINF if not maximizingPlayer else board.INF

        if maximizingPlayer:
            color = board.nextPlayer
            otherColor = MyBoard.flip(color)
        else:
            otherColor = board.nextPlayer
            color = MyBoard.flip(otherColor)
        
        data = board.get_data(color, otherColor)

        score = 0
        score += data['my_nbStones'] - data['other_nbStones']
        score += data['my_nbLiberties'] - data['other_nbLiberties']
        #score += data['my_nbStrings'] - data['other_nbStrings']

        return score


class MediumGobanEval_V2(AbstractGobanEval):
    def __init__(self):
        pass

    def board_value(self, board, maxDepth, maximizingPlayer, lastMove):
        from MyGoban import MyBoard

        m = board.flat_to_name(lastMove)
        
        if board.is_game_over():
            return board.INF if not maximizingPlayer else board.NINF
        
        if m == 'PASS':
            return board.NINF if not maximizingPlayer else board.INF

        if maximizingPlayer:
            color = board.nextPlayer
            otherColor = MyBoard.flip(color)
        else:
            otherColor = board.nextPlayer
            color = MyBoard.flip(otherColor)

        data = board.get_data(color, otherColor)
        score = 0

        if data['other_nbLiberties'] > 0:
            score += (((data['my_nbLiberties'] / (data['my_nbLiberties'] + data['other_nbLiberties'])) * 2) - 1) * 10

        if data['other_nbStones'] > 0:
            score += (((data['my_nbStones'] / (data['my_nbStones'] + data['other_nbStones'])) * 2) - 1) * 10

        if data['my_nbStrings'] > 0:
            score += (((data['other_nbStrings'] / (data['my_nbStrings'] + data['other_nbStrings'])) * 2) - 1) * 20

        if data['my_nbWeakStrings1'] > 0:
            score -= 5
        if data['my_nbWeakStrings2'] > 0:
            score -= 3
        if data['my_nbWeakStrings3'] > 0:
            score -= 1

        if data['other_nbWeakStrings1'] > 0:
            score += 5
        if data['other_nbWeakStrings2'] > 0:
            score += 3
        if data['other_nbWeakStrings3'] > 0:
            score += 1

        myLiberties = board.get_liberties(color)
        opLiberties = board.get_liberties(otherColor)

        for lbt in myLiberties:
            n, no = board.nb_shared_liberty(color, lbt)
            if n == 1 and no == 0:
                score += 5
            if n == 2 and no == 0:
                score += 3
            if n == 3:
                score += 1

        if maxDepth <= 1:
            return round(score)
            
        return score if not maximizingPlayer else -score


class MediumGobanEval_V3(AbstractGobanEval):
    def __init__(self):
        pass

    def board_value(self, board, maxDepth, maximizingPlayer, lastMove):
        from MyGoban import MyBoard
       
        m = board.flat_to_name(lastMove)
        
        if board.is_game_over():
            return board.INF if not maximizingPlayer else board.NINF
        
        if m == 'PASS':
            return board.NINF if not maximizingPlayer else board.INF

        if maximizingPlayer:
            color = board.nextPlayer
            otherColor = MyBoard.flip(color)
        else:
            otherColor = board.nextPlayer
            color = MyBoard.flip(otherColor)

        data = board.get_data(color, otherColor)

        score = 0

        if m in ['F3', 'D3', 'E5', 'D7', 'G5', 'C6', 'D6', 'C4', 'C5', 'G6', 'C7', 'H7', 'C3', 'H3']:
            score += 8  
        elif m in ['G4', 'G6', 'C6', 'E3', 'D7', 'D6', 'F7', 'E7', 'D3']:
            score += 4

        if data['other_nbStones'] > 0:
            score += (((data['my_nbStones'] / (data['my_nbStones'] + data['other_nbStones'])) * 2) - 1) * 20

        score -= data['my_nbStrings'] * 2

        if data['my_nbWeakStrings1'] > 0:
            score -= 100
        if data['my_nbWeakStrings2'] > 0:
            score -= 30
        if data['my_nbWeakStrings3'] > 0:
            score -= 10

        if data['other_nbWeakStrings1'] > 0:
            score += 100
        if data['other_nbWeakStrings2'] > 0:
            score += 30
        if data['other_nbWeakStrings3'] > 0:
            score += 10

        myLiberties = board.get_liberties(color)
        opLiberties = board.get_liberties(otherColor)

        for lbt in myLiberties:
            n, no = board.nb_shared_liberty(color, lbt)
            if n == 1 and no == 0:
                score += 4
            if n == 2 and no == 0:
                score += 2
            if no == 0:
                score += 6

        for lbt in opLiberties:
            n, no = board.nb_shared_liberty(otherColor, lbt)
            if n == 2:
                score -= 1
            elif n == 3:
                score -= 2

        _, _, a, b, c = board.compute_territory(color)
        score += (a + c/4 - b)/4
       
        if maxDepth <= 1:
            return round(score) if not maximizingPlayer else -round(score)
            
        return score if not maximizingPlayer else -score

class MediumGobanEval_V4(AbstractGobanEval):
    def __init__(self):
        pass

    def board_value(self, board, maxDepth, maximizingPlayer, lastMove):
        from MyGoban import MyBoard

        m = board.flat_to_name(lastMove)
        
        if board.is_game_over():
            return board.INF if not maximizingPlayer else board.NINF
        
        ''' Passer son tour n'est jamais bien '''
        if m == 'PASS':
            return board.NINF if not maximizingPlayer else board.INF

        ''' Récupération des couleurs suivant la profondeur d'où est calculé l'heuristique '''
        if maximizingPlayer:
            color = board.nextPlayer
            otherColor = MyBoard.flip(color)
        else:
            otherColor = board.nextPlayer
            color = MyBoard.flip(otherColor)

        data = board.get_data(color, otherColor)

        score = 0

        if m in ['F3', 'D3', 'E5', 'D7', 'G5', 'C6', 'D6', 'C4', 'C5', 'G6', 'C7', 'H7', 'C3', 'H3']:
            score += 2
        elif m in ['G4', 'G6', 'C6', 'E3', 'D7', 'D6', 'F7', 'E7', 'D3']:
            score += 1

        if data['other_nbStones'] > 0:
            score += (((data['my_nbStones'] / (data['my_nbStones'] + data['other_nbStones'])) * 2) - 1) * 50

        score -= (data['other_nbStrings'] + data['my_nbStrings']) * 3

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
            if n <= 2 and no == 0:
                score += 3
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
                score += 6
            elif len(s.liberties) >= 10:
                score += 4
            elif len(s.liberties) >= 5:
                score += 2

        if maxDepth <= 1:
            return round(score) if not maximizingPlayer else -round(score)
            
        return round(score,4) if not maximizingPlayer else -round(score,4)
