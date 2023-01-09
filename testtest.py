from constants import *
test = {WHITE_COLOR_IDENTIFIER: [0, 0, 0, 0],
        BLACK_COLOR_IDENTIFIER: [0, 1, 2, 3]}

test["w"][1] = 4
print(test["w"][1])
