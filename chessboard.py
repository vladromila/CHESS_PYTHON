import pygame
import sys
import os
from constants import *
from pprint import pprint
import io
from stockfish import Stockfish
import time
import copy
import random
import chess
"""
Class that saves the data that matters for every piece
"""


class ChessPiece:

    def __init__(self, identifier, dir=0):
        self.possible_moves = []
        self.identifier = identifier
        self.dir = dir
        self.color = WHITE_COLOR_IDENTIFIER if identifier[
            0] == WHITE_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER
        self.moved = False


class Helpers:
    def __init__(self) -> None:
        pass

    @staticmethod
    def is_enemy_or_empty(piece1, piece2):
        if piece2 == None:
            return True
        if piece1.color == WHITE_COLOR_IDENTIFIER:
            if piece2.identifier[0] == BLACK_COLOR_IDENTIFIER:
                return True
        if piece1.color == BLACK_COLOR_IDENTIFIER:
            if piece2.identifier[0] == WHITE_COLOR_IDENTIFIER:
                return True
        return False

    @staticmethod
    def is_empty(piece):
        return piece == None

    @staticmethod
    def is_enemy(piece1, piece2):

        if piece2 == None:
            return False
        if piece1.color == WHITE_COLOR_IDENTIFIER:
            if piece2.identifier[0] == BLACK_COLOR_IDENTIFIER:
                return True
        if piece1.color == BLACK_COLOR_IDENTIFIER:
            if piece2.identifier[0] == WHITE_COLOR_IDENTIFIER:
                return True
        return False

    @staticmethod
    def is_pawn(piece):
        return piece.identifier[1] == 'p'

    @staticmethod
    def is_rook(piece):
        return piece.identifier[1] == 'R'

    @staticmethod
    def is_knight(piece):
        return piece.identifier[1] == 'N'

    @staticmethod
    def is_bishop(piece):
        return piece.identifier[1] == 'B'

    @staticmethod
    def is_queen(piece):
        return piece.identifier[1] == 'Q'

    @staticmethod
    def is_king(piece):
        return piece.identifier[1] == 'K'


stockfish = Stockfish(os.path.abspath("stockfish.exe"))
stockfish.update_engine_parameters({"Hash": 2048})
board = chess.Board()


class ChessBoard:

    def __init__(self, type, white_top=False, testing=False, boardsquares=[]):
        self.testing = testing
        self.white_top = white_top
        self.currently_playing = WHITE_COLOR_IDENTIFIER
        self.game_ended = False
        self.show_end_screen = False
        self.game_ended_reason = None
        if testing == True:
            self.boardsquares = boardsquares
        elif white_top == True:
            self.boardsquares = [  # 1
                ['wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR'],  # 1
                ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],  # 2
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 3
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 4
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 5
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 6
                ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],  # 7
                ['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR'],  # 8
                #  a     b     c     d     e     f     g     h
            ]
        else:
            self.boardsquares = [
                ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],  # 8
                ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],  # 7
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 6
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 5
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 4
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 3
                ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],  # 2
                ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']  # 1
                #  a     b     c     d     e     f     g     h
            ]
        self.boardpieces = [[None for c in range(
            NUMBER_OF_COLUMNS)]for r in range(NUMBER_OF_ROWS)]
        self.captures = {WHITE_COLOR_IDENTIFIER: {BLACK_PAWN_IDENTIFIER: 0, BLACK_ROOK_IDENTIFIER: 0, BLACK_QUEEN_IDENTIFIER: 0, BLACK_BISHOP_IDENTIFIER: 0, BLACK_KNIGHT_IDENTIFIER: 0},
                         BLACK_COLOR_IDENTIFIER: {WHITE_PAWN_IDENTIFIER: 0, WHITE_ROOK_IDENTIFIER: 0, WHITE_QUEEN_IDENTIFIER: 0, WHITE_BISHOP_IDENTIFIER: 0, WHITE_KNIGHT_IDENTIFIER: 0}}
        self.playtype = type
        self.initialize_pieces()
        self.calculate_moves_for_all_pieces()
        self.wait_for_next_move = False
        self.last_time = None
        self.last_move = None

        if not self.testing:
            board.reset()
            stockfish.set_fen_position(
                self.pieces_to_fen(WHITE_COLOR_IDENTIFIER))
            if self.playtype != 1 and (self.white_top == True or self.playtype == 3):
                self.wait_for_next_move = True
        # self.stockfish.update_engine_parameters({"Threads": 2, "Hash": 12})

    def initialize_pieces(self):
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if self.boardsquares[r][c] != EMPTY_IDENTIFIER:
                    if self.boardsquares[r][c] == BLACK_PAWN_IDENTIFIER and self.white_top == True:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c], -1)
                        if r != 6:
                            self.boardpieces[r][c].moved = True
                    elif self.boardsquares[r][c] == BLACK_PAWN_IDENTIFIER and self.white_top == False:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c], 1)
                        if r != 1:
                            self.boardpieces[r][c].moved = True
                    elif self.boardsquares[r][c] == WHITE_PAWN_IDENTIFIER and self.white_top == True:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c], 1)
                        if r != 1:
                            self.boardpieces[r][c].moved = True
                    elif self.boardsquares[r][c] == WHITE_PAWN_IDENTIFIER and self.white_top == False:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c], -1)
                        if r != 6:
                            self.boardpieces[r][c].moved = True
                    else:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c])

    def calculate_possible_moves(self, r, c):
        self.possible_moves = []
        piece = self.boardpieces[r][c]
        piece.possible_moves = []

        if Helpers.is_pawn(piece):
            possible_moves = []
            if r <= 6 and r > 0:
                if c >= 1:
                    if Helpers.is_enemy(piece, self.boardpieces[r+piece.dir*1][c-1]):
                        possible_moves.append(
                            (r+piece.dir*1, c-1))
                if c <= 6:
                    if Helpers.is_enemy(piece, self.boardpieces[r+piece.dir*1][c+1]):
                        possible_moves.append(
                            (r+piece.dir*1, c+1))
                if Helpers.is_empty(self.boardpieces[r+piece.dir*1][c]):
                    possible_moves.append(
                        (r+piece.dir*1, c))
                    if piece.moved == False:
                        if Helpers.is_empty(self.boardpieces[r+piece.dir*2][c]):
                            possible_moves.append(
                                (r+piece.dir*2, c))
                for move in possible_moves:
                    if self.testing == False:
                        game_copy = ChessBoard(
                            self.playtype, self.white_top, True, self.pieces_to_board(True))
                        game_copy.currently_playing = self.currently_playing
                        game_copy.make_move(move[0], move[1], r, c)
                        if not game_copy.is_in_check():
                            piece.possible_moves.append(move)
                    else:
                        piece.possible_moves.append(move)
            return len(piece.possible_moves)

        elif Helpers.is_knight(piece):
            possible_move_options = [(r+2, c+1),
                                     (r+2, c-1),
                                     (r+1, c+2),
                                     (r+1, c-2),
                                     (r-2, c+1),
                                     (r-2, c-1),
                                     (r-1, c+2),
                                     (r-1, c-2),
                                     ]

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7 and Helpers.is_enemy_or_empty(piece, self.boardpieces[move[0]][move[1]]):
                    if self.testing == False:
                        game_copy = ChessBoard(
                            self.playtype, self.white_top, True, self.pieces_to_board(True))
                        game_copy.currently_playing = self.currently_playing
                        game_copy.make_move(move[0], move[1], r, c)
                        if not game_copy.is_in_check():
                            piece.possible_moves.append(move)
                    else:
                        piece.possible_moves.append(move)
            return len(piece.possible_moves)

        elif Helpers.is_king(piece):
            possible_move_options = [(r+1, c),
                                     (r+1, c-1),
                                     (r+1, c+1),
                                     (r, c+1),
                                     (r, c-1),
                                     (r-1, c),
                                     (r-1, c-1),
                                     (r-1, c+1),
                                     ]
            if self.white_top:
                if (r == 0 or r == 7) and c == 3 and piece.moved == False:
                    if self.boardpieces[r][c-1] == None and self.boardpieces[r][c-2] == None and not Helpers.is_empty(self.boardpieces[r][c-3]) and Helpers.is_rook(self.boardpieces[r][c-3]) and self.boardpieces[r][c-3].moved == False:
                        possible_move_options.append((r, c-2))
                    if self.boardpieces[r][c+1] == None and self.boardpieces[r][c+2] == None and self.boardpieces[r][c+3] == None and not Helpers.is_empty(self.boardpieces[r][c+4]) and Helpers.is_rook(self.boardpieces[r][c+4]) and self.boardpieces[r][c+4].moved == False:
                        possible_move_options.append((r, c+2))
            else:
                if (r == 0 or r == 7) and c == 4 and piece.moved == False:
                    if self.boardpieces[r][c-1] == None and self.boardpieces[r][c-2] == None and self.boardpieces[r][c-3] == None and not Helpers.is_empty(self.boardpieces[r][c-4]) and Helpers.is_rook(self.boardpieces[r][c-4]) and self.boardpieces[r][c-4].moved == False:
                        possible_move_options.append((r, c-2))
                    if self.boardpieces[r][c+1] == None and self.boardpieces[r][c+2] == None and not Helpers.is_empty(self.boardpieces[r][c+3]) and Helpers.is_rook(self.boardpieces[r][c+3]) and self.boardpieces[r][c+3].moved == False:
                        possible_move_options.append((r, c+2))

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7 and Helpers.is_enemy_or_empty(piece, self.boardpieces[move[0]][move[1]]):
                    if self.testing == False:
                        game_copy = ChessBoard(
                            self.playtype, self.white_top, True, self.pieces_to_board(True))
                        game_copy.currently_playing = self.currently_playing
                        game_copy.make_move(move[0], move[1], r, c)
                        if not game_copy.is_in_check():
                            piece.possible_moves.append(move)
                    else:
                        piece.possible_moves.append(move)
            return len(piece.possible_moves)

        elif Helpers.is_queen(piece):
            possible_move_options = []

            current_r = r
            current_c = c

            for c in range(current_c+1, NUMBER_OF_COLUMNS, 1):
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[current_r][c]):
                    possible_move_options.append((current_r, c))
                    if Helpers.is_enemy(piece, self.boardpieces[current_r][c]):
                        break
                else:
                    break

            for c in range(current_c-1, -1, - 1):
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[current_r][c]):
                    possible_move_options.append((current_r, c))
                    if Helpers.is_enemy(piece, self.boardpieces[current_r][c]):
                        break
                else:
                    break

            for r in range(current_r-1, -1, -1):
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[r][current_c]):
                    possible_move_options.append((r, current_c))
                    if Helpers.is_enemy(piece, self.boardpieces[r][current_c]):
                        break
                else:
                    break

            for r in range(current_r+1, NUMBER_OF_ROWS, 1):
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[r][current_c]):
                    possible_move_options.append((r, current_c))
                    if Helpers.is_enemy(piece, self.boardpieces[r][current_c]):
                        break
                else:
                    break

            copy_c = current_c-1
            copy_r = current_r-1
            while copy_c >= 0 and copy_r >= 0:
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[copy_r][copy_c]):
                    possible_move_options.append((copy_r, copy_c))
                    if Helpers.is_enemy(piece, self.boardpieces[copy_r][copy_c]):
                        break
                else:
                    break
                copy_c = copy_c-1
                copy_r = copy_r-1

            copy_c = current_c+1
            copy_r = current_r+1
            while copy_c < NUMBER_OF_COLUMNS and copy_r < NUMBER_OF_ROWS:
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[copy_r][copy_c]):
                    possible_move_options.append((copy_r, copy_c))
                    if Helpers.is_enemy(piece, self.boardpieces[copy_r][copy_c]):
                        break
                else:
                    break
                copy_c = copy_c+1
                copy_r = copy_r+1

            copy_c = current_c-1
            copy_r = current_r+1
            while copy_c >= 0 and copy_r < NUMBER_OF_ROWS:
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[copy_r][copy_c]):
                    possible_move_options.append((copy_r, copy_c))
                    if Helpers.is_enemy(piece, self.boardpieces[copy_r][copy_c]):
                        break
                else:
                    break
                copy_c = copy_c-1
                copy_r = copy_r+1

            copy_c = current_c+1
            copy_r = current_r-1
            while copy_c < NUMBER_OF_COLUMNS and copy_r >= 0:
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[copy_r][copy_c]):
                    possible_move_options.append((copy_r, copy_c))
                    if Helpers.is_enemy(piece, self.boardpieces[copy_r][copy_c]):
                        break
                else:
                    break
                copy_c = copy_c+1
                copy_r = copy_r-1
            c = current_c
            r = current_r
            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    if self.testing == False:
                        game_copy = ChessBoard(
                            self.playtype, self.white_top, True, self.pieces_to_board(True))
                        game_copy.currently_playing = self.currently_playing
                        game_copy.make_move(move[0], move[1], r, c)
                        if not game_copy.is_in_check():
                            piece.possible_moves.append(move)
                    else:
                        piece.possible_moves.append(move)
            return len(piece.possible_moves)

        elif Helpers.is_rook(piece):
            possible_move_options = []

            current_r = r
            current_c = c

            for c in range(current_c+1, NUMBER_OF_COLUMNS, 1):
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[current_r][c]):
                    possible_move_options.append((current_r, c))
                    if Helpers.is_enemy(piece, self.boardpieces[current_r][c]):
                        break
                else:
                    break

            for c in range(current_c-1, -1, - 1):
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[current_r][c]):
                    possible_move_options.append((current_r, c))
                    if Helpers.is_enemy(piece, self.boardpieces[current_r][c]):
                        break
                else:
                    break

            for r in range(current_r-1, -1, -1):
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[r][current_c]):
                    possible_move_options.append((r, current_c))
                    if Helpers.is_enemy(piece, self.boardpieces[r][current_c]):
                        break
                else:
                    break

            for r in range(current_r+1, NUMBER_OF_ROWS, 1):
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[r][current_c]):
                    possible_move_options.append((r, current_c))
                    if Helpers.is_enemy(piece, self.boardpieces[r][current_c]):
                        break
                else:
                    break
            c = current_c
            r = current_r
            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    if self.testing == False:
                        game_copy = ChessBoard(
                            self.playtype, self.white_top, True, self.pieces_to_board(True))
                        game_copy.currently_playing = self.currently_playing
                        game_copy.make_move(move[0], move[1], r, c)
                        if not game_copy.is_in_check():
                            piece.possible_moves.append(move)
                    else:
                        piece.possible_moves.append(move)
            return len(piece.possible_moves)

        elif Helpers.is_bishop(piece):
            possible_move_options = []

            current_r = r
            current_c = c

            copy_c = current_c-1
            copy_r = current_r-1
            while copy_c >= 0 and copy_r >= 0:
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[copy_r][copy_c]):
                    possible_move_options.append((copy_r, copy_c))
                    if Helpers.is_enemy(piece, self.boardpieces[copy_r][copy_c]):
                        break
                else:
                    break
                copy_c = copy_c-1
                copy_r = copy_r-1

            copy_c = current_c+1
            copy_r = current_r+1
            while copy_c < NUMBER_OF_COLUMNS and copy_r < NUMBER_OF_ROWS:
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[copy_r][copy_c]):
                    possible_move_options.append((copy_r, copy_c))
                    if Helpers.is_enemy(piece, self.boardpieces[copy_r][copy_c]):
                        break
                else:
                    break
                copy_c = copy_c+1
                copy_r = copy_r+1

            copy_c = current_c-1
            copy_r = current_r+1
            while copy_c >= 0 and copy_r < NUMBER_OF_ROWS:
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[copy_r][copy_c]):
                    possible_move_options.append((copy_r, copy_c))
                    if Helpers.is_enemy(piece, self.boardpieces[copy_r][copy_c]):
                        break
                else:
                    break
                copy_c = copy_c-1
                copy_r = copy_r+1

            copy_c = current_c+1
            copy_r = current_r-1
            while copy_c < NUMBER_OF_COLUMNS and copy_r >= 0:
                if Helpers.is_enemy_or_empty(piece, self.boardpieces[copy_r][copy_c]):
                    possible_move_options.append((copy_r, copy_c))
                    if Helpers.is_enemy(piece, self.boardpieces[copy_r][copy_c]):
                        break
                else:
                    break
                copy_c = copy_c+1
                copy_r = copy_r-1

            c = current_c
            r = current_r

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    if self.testing == False:
                        game_copy = ChessBoard(
                            self.playtype, self.white_top, True, self.pieces_to_board(True))
                        game_copy.currently_playing = self.currently_playing
                        game_copy.make_move(move[0], move[1], r, c)
                        if not game_copy.is_in_check():
                            piece.possible_moves.append(move)
                    else:
                        piece.possible_moves.append(move)
            return len(piece.possible_moves)

    def pieces_to_board(self, for_testing=False):
        board = [['' for c in range(NUMBER_OF_COLUMNS)]
                 for r in range(NUMBER_OF_ROWS)]
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if self.white_top and for_testing == False:
                    if not Helpers.is_empty(self.boardpieces[r][c]):
                        board[NUMBER_OF_ROWS-r-1][NUMBER_OF_COLUMNS -
                                                  c-1] = self.boardpieces[r][c].identifier
                    else:
                        board[NUMBER_OF_ROWS-r-1][NUMBER_OF_COLUMNS -
                                                  c-1] = EMPTY_IDENTIFIER
                else:
                    if not Helpers.is_empty(self.boardpieces[r][c]):
                        board[r][c] = self.boardpieces[r][c].identifier
                    else:
                        board[r][c] = EMPTY_IDENTIFIER
        return board

    def board_to_pieces(self):
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if self.boardsquares[r][c] != EMPTY_IDENTIFIER:
                    if self.boardsquares[r][c] == BLACK_PAWN_IDENTIFIER and self.white_top == True:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c], -1)
                    elif self.boardsquares[r][c] == BLACK_PAWN_IDENTIFIER and self.white_top == False:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c], 1)
                    elif self.boardsquares[r][c] == WHITE_PAWN_IDENTIFIER and self.white_top == True:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c], 1)
                    elif self.boardsquares[r][c] == WHITE_PAWN_IDENTIFIER and self.white_top == False:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c], -1)
                    else:
                        self.boardpieces[r][c] = ChessPiece(
                            self.boardsquares[r][c])

    def pieces_to_fen(self, color):
        board = [['' for c in range(NUMBER_OF_COLUMNS)]
                 for r in range(NUMBER_OF_ROWS)]
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if self.white_top:
                    if not Helpers.is_empty(self.boardpieces[r][c]):
                        board[NUMBER_OF_ROWS-r-1][NUMBER_OF_COLUMNS -
                                                  c-1] = self.boardpieces[r][c].identifier
                    else:
                        board[NUMBER_OF_ROWS-r-1][NUMBER_OF_COLUMNS -
                                                  c-1] = EMPTY_IDENTIFIER
                else:
                    if not Helpers.is_empty(self.boardpieces[r][c]):
                        board[r][c] = self.boardpieces[r][c].identifier
                    else:
                        board[r][c] = EMPTY_IDENTIFIER
        # pprint(board)
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
                        s.write(cell[1].upper() if c ==
                                'w' else cell[1].lower())
                    else:
                        empty += 1
                if empty > 0:
                    s.write(str(empty))
                s.write('/')

            s.seek(s.tell() - 1)
            # If you do not have the additional information choose what to put
            s.write(f' {color} KQkq - 0 1')
            # print(s.getvalue())
            return s.getvalue()

    def calculate_move_based_on_prediction(self, value):
        from_pos = value[:2]
        to_pos = value[2:len(value)]
        print(value, to_pos, to_pos[1], "HAI SA VEDEM DE CE CRAPA OK? THANKS!")
        if self.white_top:
            from_pos = (int(from_pos[1])-1,
                        NUMBER_OF_COLUMNS-ALPHATONR[from_pos[0]]-1)
            to_pos = (int(to_pos[1])-1,
                      NUMBER_OF_COLUMNS-ALPHATONR[to_pos[0]]-1)
            return [from_pos, to_pos]
        if not self.white_top:
            from_pos = (
                NUMBER_OF_ROWS-int(from_pos[1]),  ALPHATONR[from_pos[0]])
            to_pos = (
                NUMBER_OF_ROWS-int(to_pos[1]), ALPHATONR[to_pos[0]])
            return [from_pos, to_pos]

    def calculate_moves_for_all_pieces(self):
        if not self.testing:
            pprint(self.captures)
        black_totalsum = 0
        white_totalsum = 0
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if not Helpers.is_empty(self.boardpieces[r][c]):
                    total_moves = self.calculate_possible_moves(r, c)
                    if (self.testing == False):
                        if self.boardpieces[r][c].color == BLACK_COLOR_IDENTIFIER:
                            black_totalsum = black_totalsum+total_moves
                        if self.boardpieces[r][c].color == WHITE_COLOR_IDENTIFIER:
                            white_totalsum = white_totalsum+total_moves

        if board.is_stalemate():
            self.game_ended = True
            self.show_end_screen = True
            self.game_ended_reason = "Draw: Stalemate"
            return
        if board.is_insufficient_material():
            self.game_ended = True
            self.show_end_screen = True
            self.game_ended_reason = "Draw: Stalemate"
            return
        if board.is_fivefold_repetition():
            self.game_ended = True
            self.show_end_screen = True
            self.game_ended_reason = "Draw: Five Fold Repetition"
            return
        if board.is_seventyfive_moves():
            self.game_ended = True
            self.show_end_screen = True
            self.game_ended_reason = "Draw: 75 Moves Rule"
            return

        if self.testing == False:
            if black_totalsum == 0:
                self.game_ended = True
                self.show_end_screen = True
                self.game_ended_reason = "White wins by Checkmate"
                return
            if white_totalsum == 0:
                self.game_ended = True
                self.show_end_screen = True
                self.game_ended_reason = "Black wins by Checkmate"
                return

    def check_queen_promotion(self, r, c):
        """
        Queen promotion for white pawns
        """
        if Helpers.is_pawn(self.boardpieces[r][c]) and (r == 0 and self.boardpieces[r][c].color == WHITE_COLOR_IDENTIFIER):
            self.boardpieces[r][c] = ChessPiece(
                WHITE_QUEEN_IDENTIFIER)
            self.captures[BLACK_COLOR_IDENTIFIER][WHITE_PAWN_IDENTIFIER] = self.captures[BLACK_COLOR_IDENTIFIER][WHITE_PAWN_IDENTIFIER]+1
            return True
        if Helpers.is_pawn(self.boardpieces[r][c]) and (r == 7 and self.boardpieces[r][c].color == WHITE_COLOR_IDENTIFIER):
            self.boardpieces[r][c] = ChessPiece(
                WHITE_QUEEN_IDENTIFIER)
            self.captures[BLACK_COLOR_IDENTIFIER][WHITE_PAWN_IDENTIFIER] = self.captures[BLACK_COLOR_IDENTIFIER][WHITE_PAWN_IDENTIFIER]+1
            return True
        """
        Queen promotion for black pawns
        """
        if Helpers.is_pawn(self.boardpieces[r][c]) and (r == 7 and self.boardpieces[r][c].color == BLACK_COLOR_IDENTIFIER):
            self.boardpieces[r][c] = ChessPiece(
                BLACK_QUEEN_IDENTIFIER)
            self.captures[WHITE_COLOR_IDENTIFIER][BLACK_PAWN_IDENTIFIER] = self.captures[WHITE_COLOR_IDENTIFIER][BLACK_PAWN_IDENTIFIER]+1
            return True

        if Helpers.is_pawn(self.boardpieces[r][c]) and (r == 0 and self.boardpieces[r][c].color == BLACK_COLOR_IDENTIFIER):
            self.boardpieces[r][c] = ChessPiece(
                BLACK_QUEEN_IDENTIFIER)
            self.captures[WHITE_COLOR_IDENTIFIER][BLACK_PAWN_IDENTIFIER] = self.captures[WHITE_COLOR_IDENTIFIER][BLACK_PAWN_IDENTIFIER]+1
            return True

        return False

    def is_in_check(self):
        king_pos = (-1, -1)
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if self.currently_playing == BLACK_COLOR_IDENTIFIER:
                    if not Helpers.is_empty(self.boardpieces[r][c]) and self.boardpieces[r][c].identifier == BLACK_KING_IDENTIFIER:
                        king_pos = (r, c)
                        break
                if self.currently_playing == WHITE_COLOR_IDENTIFIER:
                    if not Helpers.is_empty(self.boardpieces[r][c]) and self.boardpieces[r][c].identifier == WHITE_KING_IDENTIFIER:
                        king_pos = (r, c)
                        break
        to_find_color = WHITE_COLOR_IDENTIFIER if self.currently_playing == BLACK_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER
        is_check = False
        to_save_pieces = []
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if not Helpers.is_empty(self.boardpieces[r][c]) and self.boardpieces[r][c].color == to_find_color:
                    if king_pos in self.boardpieces[r][c].possible_moves:
                        is_check = True
                        to_save_pieces.append((r, c))
        return is_check
        # print(copied_board.boardsquares)
        # pprint(to_check_board)
        # print(is_check, to_save_pieces)

    def is_in_check_after_move(self, from_pos, to_pos):
        king_pos = (-1, -1)
        self.boardpieces[to_pos[0]][to_pos[1]
                                    ] = self.boardpieces[from_pos[0]][from_pos[1]]
        self.boardpieces[to_pos[0]][to_pos[1]].moved = True
        self.boardpieces[from_pos[0]][from_pos[1]] = None
        self.calculate_moves_for_all_pieces()
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if self.currently_playing == BLACK_COLOR_IDENTIFIER:
                    if not Helpers.is_empty(self.boardpieces[r][c]) and self.boardpieces[r][c].identifier == BLACK_KING_IDENTIFIER:
                        king_pos = (r, c)
                        break
                if self.currently_playing == WHITE_COLOR_IDENTIFIER:
                    if not Helpers.is_empty(self.boardpieces[r][c]) and self.boardpieces[r][c].identifier == WHITE_KING_IDENTIFIER:
                        king_pos = (r, c)
                        break
        to_find_color = WHITE_COLOR_IDENTIFIER if self.currently_playing == BLACK_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER
        is_check = False
        to_save_pieces = []
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if not Helpers.is_empty(self.boardpieces[r][c]) and self.boardpieces[r][c].color == to_find_color:
                    if king_pos in self.boardpieces[r][c].possible_moves:
                        is_check = True
                        to_save_pieces.append((r, c))
        return is_check

    def calculate_move_code_from_coordinates(self, r, c):
        if self.white_top:
            code = ALPHACOLS[NUMBER_OF_COLUMNS-c-1]+str(r+1)
            return code
        else:
            code = ALPHACOLS[c]+str(NUMBER_OF_ROWS-r)
            return code

    def calculate_next_move(self):
        # print(self.currently_playing, "AICI S AR PUTEA SA PICE",
        #       stockfish.get_fen_position())
        # stockfish_move = stockfish.get_best_move()
        # print("alegerea facuta:", stockfish_move)
        # if stockfish_move != None:
        #     result = self.calculate_move_based_on_prediction(stockfish_move)
        #     print(result[1][0], result[1][1], result[0][0], result[0][1])
        #     return self.make_move(result[1][0], result[1][1],
        #                           result[0][0], result[0][1])
        # else:
        #     self.wait_for_next_move = False
        #     self.last_time = None

        to_choose_list = []
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if not Helpers.is_empty(self.boardpieces[r][c]) and self.boardpieces[r][c].color == self.currently_playing:
                    for move in self.boardpieces[r][c].possible_moves:
                        to_choose_list.append([(r, c), move])
        result = random.choice(to_choose_list)
        if result:
            return self.make_move(result[1][0], result[1][1],
                                  result[0][0], result[0][1])
        else:
            self.wait_for_next_move = False
            self.last_time = None

        return False

    def make_move(self, r, c, r2, c2):
        will_capture = False
        if not Helpers.is_empty(self.boardpieces[r][c]):
            will_capture = True
            if not self.testing:
                self.captures[self.currently_playing][self.boardpieces[r]
                                                      [c].identifier] = self.captures[self.currently_playing][self.boardpieces[r][c].identifier]+1
        if Helpers.is_king(self.boardpieces[r2][c2]):
            if abs(c-c2) == 2:
                if c2 > c:
                    self.boardpieces[r][int((c+c2)/2)] = self.boardpieces[r][0]
                    self.boardpieces[r][0] = None
                if c2 < c:
                    self.boardpieces[r][int((c+c2)/2)] = self.boardpieces[r][7]
                    self.boardpieces[r][7] = None
        self.boardpieces[r][c] = self.boardpieces[r2][c2]
        self.boardpieces[r][c].moved = True

        if not self.testing:
            if self.check_queen_promotion(r, c):
                board.push(chess.Move.from_uci(self.calculate_move_code_from_coordinates(
                    r2, c2)+self.calculate_move_code_from_coordinates(r, c)+"q"))
                stockfish.make_moves_from_current_position([self.calculate_move_code_from_coordinates(
                    r2, c2)+self.calculate_move_code_from_coordinates(r, c)+"q"])
            else:
                board.push(chess.Move.from_uci(self.calculate_move_code_from_coordinates(
                    r2, c2)+self.calculate_move_code_from_coordinates(r, c)))
                stockfish.make_moves_from_current_position([self.calculate_move_code_from_coordinates(
                    r2, c2)+self.calculate_move_code_from_coordinates(r, c)])
        self.last_move = [(r2, c2), (r, c)]
        self.boardpieces[r2][c2] = None
        self.calculate_moves_for_all_pieces()
        self.currently_playing = WHITE_COLOR_IDENTIFIER if self.currently_playing == BLACK_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER
        if not self.testing:
            print(self.pieces_to_fen(self.currently_playing))
        if not self.game_ended:
            if self.playtype == 2 and self.testing == False:
                if (self.currently_playing == WHITE_COLOR_IDENTIFIER and self.white_top == True) or (self.currently_playing == BLACK_COLOR_IDENTIFIER and self.white_top == False):
                    self.wait_for_next_move = True
                else:
                    self.wait_for_next_move = False
                    self.last_time = None
            elif self.playtype == 3:

                self.wait_for_next_move = False
                self.last_time = None
        return will_capture
