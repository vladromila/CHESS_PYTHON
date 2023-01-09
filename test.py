import io
from pprint import pprint
from stockfish import Stockfish
from constants import *
stockfish = Stockfish("C:\\Users\\rvabo\Desktop\\chess_py\\stockfish.exe")

white_top=True
def calculate_move_based_on_prediction( value):
        from_pos = value[:2]
        to_pos = value[-2:]
        if white_top:
            from_pos = (int(from_pos[1])-1,
                        NUMBER_OF_COLUMNS-ALPHATONR[from_pos[0]]-1)
            to_pos = (int(to_pos[1])-1,
                      NUMBER_OF_COLUMNS-ALPHATONR[to_pos[0]]-1)
            return [from_pos, to_pos]
        if not white_top:
            from_pos = (
                NUMBER_OF_ROWS-int(from_pos[1]),  ALPHATONR[from_pos[0]])
            to_pos = (
                NUMBER_OF_ROWS-int(to_pos[1]), ALPHATONR[to_pos[0]])
            return [from_pos, to_pos]

stockfish.set_fen_position("rn5r/1p2kppp/p3pn2/1bb1N3/8/4PB2/PP3PPP/RNB2RK1 w - - 6 12")
print(calculate_move_based_on_prediction(stockfish.get_best_move()))
# stockfish.make_moves_from_current_position(["e7d8"])
 # a      b     c     d     e     f     g     h