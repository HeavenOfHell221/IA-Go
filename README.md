<div align="justify">

# __Les points forts de notre joueur__

Nous avons fait de notre mieux pour commenter une grande partie du code, d'une part pour la lisibilité et d'autre part pour la compréhension de nos choix.
Pour éviter les redites, certains détails techniques seront omis dans ce README. Nous vous invitons donc, si vous souhaitez plus d'informations, à regarder l'implémentation des parties qui vous intéresse.

## __Modification du Goban__ 

Pour éviter des calculs trop intensifs dans nos heuristiques, et pour calculer des informations "en temps réel" (i.e. qu'on met à jour à chaque placement d'une pierre plutôt que de tout recalculer), nous avons décidé de modifier le Goban de M. Laurent Simon, pour en avoir une version améliorée.

1. __Nouvelles variables__

Plusieurs nouvelles variables ont été ajoutées. 

* `self._strings` : Un dictionnaire contenant deux listes (noir et blanc). Ces listes contiennent les objets *String* des joueurs. Nous en parlerons plus tard.

* `self._corners` et `self._cornersEntries` : Ce sont exactement les mêmes listes que `self._neighbors ` et `self._neighborsEntries`, mais avec les 4 coins (Nord-Est, Sud-Est, Sud-Ouest, Nord-Ouest). On les utilises pour calculer si une cellule vide est un œil ou non.

* Des propriétés : pour rester cohérent avec l'approche objet qu'offre Python, nous avons mis des propriétés afin d'accéder facilement à certaines variables, tout en les gardant "privée".

2. __Nouvelles méthodes__

Nous avons ajouté une multitude de méthode dans `MyGoban.py`. Elle ne seront pas toutes décrites ici, mais en voici quelques-unes :

* `self.weak_legal_useful_moves` : Au lieu tester si les coups sont des super KO, il retire les coups qui casserait un oeil. Elle teste toujours si les coups sont des suicides.

* `self.is_eye` : Teste, pour un coup donné, s'il casserait un oeil.

* `self.is_useless` : Teste, pour un coup donné, s'il est utile ou non. Un coup dit "inutile" est un coup qui place une pierre sur une cellule déjà acquise (i.e. que l'adversaire ne peut pas placer une pierre dessus).
        
* `self.compute_territory` : Calcul, pour chaque cellule du plateau, à quelle catégorie elle appartient. Pour cela, on utilise un territoire (les 4 voisins + les 4 coins autour de la cellule). La cellule peut appartenir au noir, au blanc, elle peut aussi être "en danger", c'est à dire qu'elle n'a pas encore de propriétaire.

* `self.get_data` : Calcul/récupère des données du plateau courant et les stockes dans un dictionnaire qui est retourné. Cela permet de rendre les heuristiques plus lisibles (plutôt que d'avoir plein d'appel au plateau, on lui demande les données et on n'a plus qu'à les utiliser).

## __Les structures de données__

Nous avons voulu avoir une architecture plutôt propre. Voici quelques classes qui nous on permis d'y arriver.

1. __AbstractGobanEval et AbstractAgent__

Nous avons fait une classe abstraite pour les heuristiques, ainsi que de l'héritage pour en créer plusieurs différentes. Les heuristiques sont alors décorrélées des agents. C'est a dire qu'un même agent (ItDeepAgent par exemple), peut utiliser n'importe quelle heuristique. 

De la même manière, AbstractAgent permet, indépendamment des joueurs, de créer des IA différentes. Un joueur (comme myPlayer) n'a alors plus qu'à instancier une IA et à lui donner l'heuristique de son choix. 

2. __String__

Cette classe, composée d'un ensemble de pierre, d'un ensemble de liberté et d'une couleur, permet de représenter une chaîne de pierre pour les joueurs. Nous avons essayé d'utiliser les tableaux déjà présent dans le Goban original, mais il était très difficile de l'utiliser comme on le voulait. 
Avec cette représentation, nous avons pu implémenter plusieurs primitifs très utiles (qui sont directement dans MyBoard).

* Les primitifs de base : Créer un String, le supprimer, le fusionner avec un autre, trouver à partir d'une cellule le String dans lequel elle appartient...

* `self.compute_weak_strings_k_liberties` : Permet de connaître le nombre de String qui a k liberté. Utilisé dans les heuristiques, cela permet de rendre compte à l'IA de si elle va (bientôt) perdre une chaîne et/ou en capturer une.

* Compter le nombre de String pour chacun des joueurs, compter et itérer sur les libertés de chacun des String, etc.

## __Les agents__

1. __ItDeepAgent__

Nous avons choisi d'utiliser Iterative Deepening pour notre IA. Cela permet une bonne gestion du temps.

Pour la gestion du temps, lorsque la méthode `alpha_beta` n'a plus de temps disponible, elle retourne None. Quand `alpha_beta` récupère None, elle retourne None à son tour, etc... Cela permet de dépiler proprement tous les appels récursifs (notamment pour ne pas oublier de `board.pop()`).

Nous commençons à profondeur 1, où nous allons calculer les valeurs des plateaux. Cela permettra de garder tous les coups qui permettent d'avoir un "bon" plateau à la fin de notre tour. 

Pour la récupération des coups, nous avons une méthode `start_alpha_beta` qui se charge de récupérer les valeurs remontées par `alpha_beta`, pour sélectionner les coups à garder. 
Pour une valeur maximum, elle va garder en mémoire tous les coups ayant eu cette même valeur.

Nous utilisons une liste `bestMoves` qui contient tous les meilleurs coups du dernier `start_alpha_beta` que nous avons effectué.

Du coup, une fois `start_alpha_beta` terminé à profondeur 1, `bestMoves` contient le/les coup(s) viable(s).

La particularité de notre Iterative Deepening est d'utiliser cette liste `bestMoves` pour restreindre les sous-arbres qu'on nous visitons lorsque nous appelons `start_alpha_beta` avec une profondeur maximum supérieur à 1. Une seconde particularité est de calculer l'heuristique seulement sur les profondeurs impaires.

Ainsi, à profondeur 3 (soit la deuxième boucle d'Iterative Deepening), nous allons dérouler seulement les sous-arbres qui ont comme racines les coups contenu dans `bestMoves`. 

Cela a pour but de chercher, parmi les coups dans `bestMoves`, lequel est réellement mieux que les autres.

La liste des coups que retourne `start_alpha_beta` à profondeur 3 est strictement inclue dans `bestMoves` : 
- Soit tous les coups de `bestMoves` se valent à profondeur 3  (donc `bestMoves` ne change pas)
- Soit on retourne un sous-ensemble de taille au moins 1 (et `bestMoves` vaudra ce sous-ensemble)

On recommence le procédé à profondeur 5. S'il y a toujours plusieurs coups possible dans `bestMoves`, alors on en choisi un au hasard.

Peut importe la profondeur, si `bestMoves` n'a qu'un seul coup, on arrête Iterative Deepening et on le retourne.

## __Les heuristiques__

1. __MyGobanEval__

Ceci est notre heuristique finale. Nous utilisons un système de score. Suivant certain critère, nous allons augmenter ce score, suivant d'autre critères, nous allons le diminuer.
Un bon plateau est alors un plateau où le score est élevé. 

Nous utilisons notamment le système de territoire, les String des deux joueurs, les données calculés dans `board.get_data`, des poids pour certaines cellules (qui permettent d'orienter un peu l'IA pour les premiers coups).

Nous vous invitons fortement à regarder myGobanEval.py où nous avons beaucoup détaillé l'heuristique. Notre heuristique n'est pas compliquée, mais l'expliquer ici n'aurait pas de sens car ce n'est que des `if`. Il n'y à une logique, mais plein de critère indépendant les uns des autres qui rendent un plateau bon. 

2. __MediumGobanEval__

Les MediumGobanEval_VX (contenu dans mediumGobanEval.py) sont nos anciennes heuristiques. Nous les avons gardé pour jouer contre MyGobanEval et voir si les changements qu'on apportait rendait le joueur plus performant ou non.

</div>