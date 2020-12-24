from abstractGobanEval import AbstractGobanEval

class MyGobanEval(AbstractGobanEval):
    def __init__(self):
        pass

    def board_value(self, board, maxDepth, maximizingPlayer, lastMove):
        from MyGoban import MyBoard
        ''' Heuristique d'un plateau de jeu de GO avec 9x9 cases '''

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

        nbStone = board.nb_stones(color)
        nbStoneOther = board.nb_stones(otherColor)
        nbLiberties = board.nb_liberties(color)
        nbLibertiesOther = board.nb_liberties(otherColor)
        nbStrings = board.nb_strings(color)
        nbStringsOther = board.nb_strings(otherColor)

        (nb_my_weakStrings_1, nb_other_weakStrings_1) = board.compute_weak_strings_k_liberties(color, 1)
        (nb_my_weakStrings_2, nb_other_weakStrings_2) = board.compute_weak_strings_k_liberties(color, 2)
        (nb_my_weakStrings_3, nb_other_weakStrings_3) = board.compute_weak_strings_k_liberties(color, 3)

        params = {
            'nbStones':nbStone, 'nbStonesOther':nbStoneOther, 
            'nbLiberties':nbLiberties, 'nbLibertiesOther':nbLibertiesOther, 
            'nbStrings':nbStrings, 'nbStringsOther':nbStringsOther
            }

        weakStrings = {
            'myWS1': nb_my_weakStrings_1,
            'otherWS1': nb_other_weakStrings_1,
            'myWS2': nb_my_weakStrings_2,
            'otherWS2': nb_other_weakStrings_2,
            'myWS3': nb_my_weakStrings_3,
            'otherWS3': nb_other_weakStrings_3
            }

        score = 100

        if m in ['F3', 'D3', 'E5', 'D7', 'G5', 'C6', 'D6', 'C4', 'C5', 'G6', 'C7', 'H7', 'C3', 'H3']:
            score += 8
        elif m in ['G4', 'G6', 'C6', 'E3', 'D7', 'D6', 'F7', 'E7', 'D3']:
            score += 4

        #if params['nbLibertiesOther'] > 0:
        #    score += (((params['nbLiberties'] / (params['nbLiberties'] + params['nbLibertiesOther'])) * 2) - 1) * 10

        if params['nbStonesOther'] > 0:
            score += (((params['nbStones'] / (params['nbStones'] + params['nbStonesOther'])) * 2) - 1) * 20

        score -= params['nbStrings'] * 2

        if weakStrings['myWS1'] > 0:
            score -= 100
        if weakStrings['myWS2'] > 0:
            score -= 30
        if weakStrings['myWS3'] > 0:
            score -= 10

        if weakStrings['otherWS1'] > 0:
            score += 100
        if weakStrings['otherWS2'] > 0:
            score += 30
        if weakStrings['otherWS3'] > 0:
            score += 10

        myLiberties = board.get_liberties(color)
        opLiberties = board.get_liberties(otherColor)

        for lbt in myLiberties:
            n, no = board.nb_shared_liberty(color, lbt)
            if n == 1 and no == 0:
                score += 6
            if n == 2 and no == 0:
                score += 3

        #for lbt in opLiberties:
        #    n, no = board.nb_shared_liberty(otherColor, lbt)
        #    if no >= n:
        #        score += 3

        a, b, c, d = board.compute_territory(color)
        score += (a + c/4 - b)/4
       
        if maxDepth <= 1:
            return round(score) if not maximizingPlayer else -round(score)
            
        return score if not maximizingPlayer else -score

