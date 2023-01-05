import io
from pprint import pprint
from stockfish import Stockfish

stockfish = Stockfish("C:\\Users\\rvabo\Desktop\\chess_py\\stockfish.exe")


def fen_to_board(fen):
    board = []
    for row in fen.split('/'):
        brow = []
        for c in row:
            if c == ' ':
                break
            elif c in '12345678':
                brow.extend(['--'] * int(c))
            elif c == 'p':
                brow.append('bp')
            elif c == 'P':
                brow.append('wp')
            elif c > 'Z':
                brow.append('b'+c.upper())
            else:
                brow.append('w'+c)

        board.append(brow)
    return board


def board_to_fen(board, color):
    # Use StringIO to build string more efficiently than concatenating
    with io.StringIO() as s:
        for row in board:
            empty = 0
            for cell in row:
                c = cell[0]
                if c in ('w', 'b'):
                    if empty > 0:
                        s.write(str(empty))
                        empty = 0
                    s.write(cell[1].upper() if c == 'w' else cell[1].lower())
                else:
                    empty += 1
            if empty > 0:
                s.write(str(empty))
            s.write('/')
        # Move one position back to overwrite last '/'
        s.seek(s.tell() - 1)
        # If you do not have the additional information choose what to put
        s.write(f' {color} KQkq - 0 1')
        return s.getvalue()

# fen = 'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1'

# pprint( fen_to_board(fen) )


stockfish.set_fen_position(board_to_fen([
    ['bR', '--', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],  # 8
    ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],  # 7
    ['--', '--', '--', '--', '--', '--', '--', '--'],  # 6
    ['--', '--', '--', '--', '--', '--', '--', '--'],  # 5
    ['--', '--', '--', '--', '--', '--', '--', '--'],  # 4
    ['--', '--', '--', '--', '--', '--', '--', '--'],  # 3
    ['wp', 'wp', 'bN', 'wp', 'wp', 'wp', 'wp', 'wp'],  # 2
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']  # 1
], "b"))
# a      b     c     d     e     f     g     h
print(stockfish.get_best_move())
