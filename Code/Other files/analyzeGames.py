import json
from MyGoban import MyBoard


with open('games.json') as json_data:
    games = json.load(json_data)
    games_white = [g for g in games if g['winner'] == 'W']
    games_black = [g for g in games if g['winner'] == 'B']
    
    nbEachMovePlayed = {}
    for m in range(0, 81, 1):
        move_str = MyBoard.flat_to_name(m)
        games_with_m = [g for g in games_black if move_str in g['moves']] 
        nbEachMovePlayed[len(games_with_m)] = move_str

    #for i in sorted(nbEachMovePlayed.items()):
    #    print(i, end="\n")




'''
Nombre d'occurence de chaque move :
(31, 'J9')
(40, 'A1')
(41, 'J1')
(44, 'A9')
(121, 'J2')
(123, 'J8')
(124, 'A2')
(127, 'B1')
(128, 'H9')
(131, 'A3')
(133, 'A7')
(134, 'B9')
(137, 'A8')
(140, 'C9')
(146, 'J3')
(147, 'G9')
(161, 'F1')
(162, 'D1')
(163, 'F9')
(164, 'D9')
(165, 'J6')
(172, 'A6')
(175, 'J4')
(176, 'A4')
(177, 'E9')
(178, 'E1')
(187, 'J5')
(190, 'A5')
(244, 'H8')
(256, 'B2')
(274, 'B8')
(296, 'H3')
(304, 'G8')
(312, 'B7')
(313, 'C8')
(314, 'B3')
(317, 'H7')
(334, 'D8')
(336, 'C2')
(341, 'D2')
(350, 'F2')
(354, 'F8')
(356, 'H6')
(357, 'E2')
(362, 'B6')
(365, 'E8')
(367, 'H4')
(370, 'H5')
(383, 'B5')
(393, 'C7')
(405, 'E6')
(406, 'D4')
(407, 'F6')
(408, 'G7')
(409, 'G3')
(410, 'F5')
(411, 'C4')
(414, 'C3')
(417, 'G5')
(419, 'F3')
(420, 'C5')
(421, 'D3')
(422, 'E7')
(425, 'F7')
(426, 'D6')
(427, 'D7')
(428, 'E3')
(431, 'C6')
(433, 'E5')
(435, 'G6')
(444, 'G4')
'''


''' 
Occurence des meilleurs moves pour les games white :
(100, 'E1')
(102, 'F1')
(107, 'A5')
(111, 'J5')
(125, 'H8')
(130, 'H2')
(135, 'B2')
(137, 'B8')
(156, 'G8')
(157, 'H3')
(163, 'H7')
(164, 'C8')
(167, 'B3')
(172, 'G2')
(176, 'C2')
(177, 'D8')
(179, 'B4')
(184, 'D2')
(188, 'F2')
(189, 'E8')
(190, 'F8')
(193, 'E2')
(196, 'B6')
(199, 'B5')
(200, 'H5')
(207, 'C7')
(212, 'E6')
(213, 'G7')
(214, 'C3')
(216, 'G3')
(217, 'D4')
(218, 'C4')
(219, 'F6')
(220, 'C6')
(221, 'D6')
(222, 'G5')
(223, 'D7')
(225, 'D3')
(228, 'E7')
(229, 'G6')
(230, 'F7')
(231, 'E5')
(236, 'G4')
'''

'''
Occurence des meilleurs moves pour les games black :
(114, 'H2')
(119, 'H8')
(121, 'B2')
(137, 'B8')
(139, 'H3')
(142, 'G2')
(147, 'B3')
(148, 'G8')
(149, 'C8')
(154, 'H7')
(157, 'D8')
(160, 'C2')
(162, 'F2')
(164, 'F8')
(166, 'B6')
(167, 'H6')
(170, 'H5')
(171, 'H4')
(176, 'E8')
(177, 'B4')
(184, 'B5')
(186, 'C7')
(187, 'E4')
(188, 'F6')
(189, 'D4')
(193, 'E6')
(194, 'E7')
(195, 'G7')
(196, 'D3')
(197, 'D5')
(198, 'F4')
(199, 'F3')
(200, 'C3')
(201, 'C5')
(202, 'E5')
(204, 'D7')
(205, 'D6')
(206, 'G6')
(208, 'G4')
(210, 'E3')
(211, 'C6')
'''