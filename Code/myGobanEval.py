from abstractGobanEval import AbstractGobanEval


class MyGobanEval(AbstractGobanEval):

    '''
    L'heuristique de notre IA finale.
    Principe :
    - On a un score qui vaut 0 de base.
    - On va chercher à maximiser des caractéristiques qui feront augmenter le score tout en minimisant les
    caractéristiques qui feront diminuer le score.
    - Les caractéristiques peuvent être des valeurs du board, des valeurs qu'on calcul, un emplacement sur le board, ...
    '''

    def __init__(self):
        pass

    def board_value(self, board, maxDepth, maximizingPlayer, lastMove):
        ''' Heuristique d'un plateau de jeu de GO avec 9x9 cases '''
        from MyGoban import MyBoard

        # Récupération des couleurs suivant la profondeur d'où est calculé l'heuristique
        if maximizingPlayer:
            color = board.nextPlayer
            otherColor = MyBoard.flip(color)
        else:
            otherColor = board.nextPlayer
            color = MyBoard.flip(otherColor)

        # Si la partie est terminée, on retourne INF ou NINF pour être sûr de :
        # - Jouer la racine du sous arbre menant ici si on gagne
        # - Ne pas jouer la racine du sous arbre menant ici si on perd
        #
        # A savoir que si l'adversaire passe son tour et qu'en passant on gagne, on 
        # passe dans ce if
        if board.is_game_over():
            return board.INF if not maximizingPlayer else board.NINF
        
        # Passer son tour n'est jamais bon
        # Si on est ici c'est que passer ne nous ferra pas gagner (car l'adverseaire n'a pas passé)
        if lastMove == -1:
            return board.NINF if not maximizingPlayer else board.INF

        # Récupération des données du board
        data = board.get_data(color, otherColor)
        
        m = board.flat_to_name(lastMove)
        col, line = board.name_to_coord(m)
        score = 0 # On commence à zéro

        # Jouer dans les 3 couloirs centraux (petit bonus)
        # Cela permet de moins facilement se faire piéger dans l'un des coins du Goban
        if col in [3, 4, 5]:
            score += 4
        if line in [3, 4, 5]:
            score += 4

        # Jouer au centre pour former des connexions entre le Nord, le Sud, l'Ouest et L'est du Goban
        if col == 4:
            score += 2
        if line == 4:
            score += 2

        # On attribut un poids à certaines cellules (suivant si elle sont souvent jouée ou non sur 
        # des parties professionelles)
        if m in ['F3', 'D3', 'E5', 'D7', 'G5', 'C6', 'D6', 'C4', 'C5', 'G6', 'C7', 'H7', 'C3', 'H3']:
            score += 6
        elif m in ['G4', 'G6', 'C6', 'E3', 'D7', 'D6', 'F7', 'E7', 'D3']:
            score += 4
        elif m in ['A2', 'A1', 'B1', 'H1', 'J1', 'J2', 'H9', 'J9', 'J8', 'A9', 'A8', 'B9']:
            score -= 4

        # Si le coup est considéré comme inutile, on ne l'interdit pas, on lui donne un gros malus
        # On l'autorise car dans de rare cas, il permet de fusionner deux String, ce qui permettra de
        # ne pas ce faire capturer
        if board.is_useless(lastMove, color):
            score -= 35

        # On cherche à maximiser le ratio de pierre de notre couleur (entre -50 et 50)
        # 0 correspond à 50% de pierre de notre couleur et 50% adverse
        # 50 correspond à 100% de pierre de notre couleur et 0% adverse
        if data['other_nbStones'] > 0:
            score += (((data['my_nbStones'] / (data['my_nbStones'] + data['other_nbStones'])) * 2) - 1) * 50

        # On cherche a ne pas avoir trop de String, le but étant d'avoir des String assez long pour
        # être difficile à capturer et/ou qu'ils finisse par entourer des String adverse
        score -= data['my_nbStrings'] * 4

        # On cherche à ne pas avoir de String qui n'ont pas beaucoup de liberté 
        # Moins elle en a, plus le malus est fort, l'IA va alors chercher à les sauver
        if data['my_nbWeakStrings1'] > 0: # Si j'ai au moins une String avec seulement 1 liberté
            score -= 100
        if data['my_nbWeakStrings2'] > 0: # Si j'ai au moins une String avec seulement 2 libertés
            score -= 50
        if data['my_nbWeakStrings3'] > 0: # Si j'ai au moins une String avec seulement 3 libertés
            score -= 30
        if data['my_nbWeakStrings4'] > 0: # Si j'ai au moins une String avec seulement 4 libertés
            score -= 10

        # Inversement, on cherche à avoir des String adverse qui n'ont pas beaucoup de liberté
        # Moins une String a de liberté, plus le bonus est fort
        # La particularité, c'est qu'on ne cherche pas à capturer. Simplement à diminuer le nombre de liberté de chacune 
        # des String adverse
        if data['other_nbWeakStrings1'] > 0:
            score += 100
        if data['other_nbWeakStrings2'] > 0:
            score += 50
        if data['other_nbWeakStrings3'] > 0:
            score += 30
        if data['other_nbWeakStrings4'] > 0:
            score += 10

        # Récupération des ensembles de libertés
        myLiberties = board.get_liberties(color)
        opLiberties = board.get_liberties(otherColor)

        # On va chercher à avoir des libertés avec certaine propriété :
        # Plusieurs String allié autour, pour la protéger
        # Pas de String adverse
        for lbt in myLiberties:
            nb, nbOp = board.nb_shared_liberty(color, lbt) # On calcul combien de String différente sont autour de cette liberté 
            if nb == 2 and nbOp == 0:
                score += 4
            elif nb == 3 and nbOp <= 1:
                score += 6
            if nbOp >= 2:
                score -= 3

        # Pour les libertés adverse, on va chercher à avoir au moins 1 String allié autour
        for lbt in opLiberties:
            nb, nbOp = board.nb_shared_liberty(otherColor, lbt)
            if nbOp > 0:
                score += 3
            if nb > 2 and nbOp == 0:
                score -= 10

        # Calcul des territoires
        t_onlyColor, t_onlyOpColor, t_color, t_opColor, t_dangerous = board.compute_territory(color)
        # Formule pour maximiser les territoires "OnlyColor" et "Color"
        score += (t_onlyColor*3 + t_color) - (t_onlyOpColor*2 + t_opColor) + min(20, t_dangerous)
    
        # On va chercher à favoriser les String avec plein de liberté (et indirectement les String avec beaucoup de pierre)
        myStrings = board.get_strings(color)
        for s in myStrings:
            if len(s.liberties) >= 15:
                score += 8
            elif len(s.liberties) >= 10:
                score += 4
            elif len(s.liberties) >= 5:
                score += 2

        if maxDepth <= 1:
            # On divise par 10 pour permettre de ne pas avoir 1 seul coup meilleur que les autres, et de selectionner tous ceux
            # qui peuvent être viable (c'est à depth > 1 qu'on va chercher LE meilleur coup)
            # exemple : si un coup vaut 29 et qu'un autre vaut 30 : round(29/10) = round(30/10) = 3
            return round(score/10)*10 
            
        return round(score, 6)
