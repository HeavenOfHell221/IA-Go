from abstractGobanEval import AbstractGobanEval

class MediumGobanEval(AbstractGobanEval):
    def __init__(self):
        pass
    
    '''
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
        
        nbStone = board.nb_stones(color)
        nbStoneOther = board.nb_stones(otherColor)
        nbLiberties = board.nb_liberties(color)
        nbLibertiesOther = board.nb_liberties(otherColor)
        nbStrings = board.len_strings(color)
        nbStringsOther = board.len_strings(otherColor)

        score = nbStone - nbStoneOther
        score += nbLiberties - nbLibertiesOther
        score += nbStrings - nbStringsOther

        return score
    '''

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

        if params['nbLibertiesOther'] > 0:
            score += (((params['nbLiberties'] / (params['nbLiberties'] + params['nbLibertiesOther'])) * 2) - 1) * 10

        if params['nbStonesOther'] > 0:
            score += (((params['nbStones'] / (params['nbStones'] + params['nbStonesOther'])) * 2) - 1) * 10

        if params['nbStrings'] > 0:
            score += (((params['nbStringsOther'] / (params['nbStrings'] + params['nbStringsOther'])) * 2) - 1) * 20

        if weakStrings['myWS1'] > 0:
            score -= 5
        if weakStrings['myWS2'] > 0:
            score -= 3
        if weakStrings['myWS3'] > 0:
            score -= 1

        if weakStrings['otherWS1'] > 0:
            score += 5
        if weakStrings['otherWS2'] > 0:
            score += 3
        if weakStrings['otherWS3'] > 0:
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