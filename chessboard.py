import pygame
import sys
import os
from constants import *
from pprint import pprint
import io
from stockfish import Stockfish
import time
import copy

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


class ChessBoard:

    def __init__(self, type, white_top=False, testing=False, boardsquares=[]):
        self.testing = testing
        self.white_top = white_top
        self.currently_playing = WHITE_COLOR_IDENTIFIER
        if testing == True:
            self.boardsquares = boardsquares
        elif white_top == True:
            self.boardsquares = [  # 1
                ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],  # 1
                ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],  # 2
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 3
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 4
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 5
                ['--', '--', '--', '--', '--', '--', '--', '--'],  # 6
                ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],  # 7
                ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],  # 8
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
        self.playtype = type
        self.initialize_pieces()
        self.calculate_moves_for_all_pieces()

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
                            self.playtype, self.white_top, True, self.pieces_to_board())
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
                            self.playtype, self.white_top, True, self.pieces_to_board())
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

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7 and Helpers.is_enemy_or_empty(piece, self.boardpieces[move[0]][move[1]]):
                    if self.testing == False:
                        game_copy = ChessBoard(
                            self.playtype, self.white_top, True, self.pieces_to_board())
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
                            self.playtype, self.white_top, True, self.pieces_to_board())
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
                            self.playtype, self.white_top, True, self.pieces_to_board())
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
                            self.playtype, self.white_top, True, self.pieces_to_board())
                        game_copy.currently_playing = self.currently_playing
                        game_copy.make_move(move[0], move[1], r, c)
                        if not game_copy.is_in_check():
                            piece.possible_moves.append(move)
                    else:
                        piece.possible_moves.append(move)
            return len(piece.possible_moves)

    def pieces_to_board(self):
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
        to_pos = value[-2:]
        print(from_pos, to_pos)
        if self.white_top:
            from_pos = (int(from_pos[1])-1,
                        NUMBER_OF_COLUMNS-ALPHATONR[from_pos[0]]-1)
            to_pos = (int(to_pos[1])-1,
                      NUMBER_OF_COLUMNS-ALPHATONR[to_pos[0]]-1)
            print(from_pos, to_pos)
            return [from_pos, to_pos]
        if not self.white_top:
            from_pos = (
                NUMBER_OF_ROWS-int(from_pos[1]),  ALPHATONR[from_pos[0]])
            to_pos = (
                NUMBER_OF_ROWS-int(to_pos[1]), ALPHATONR[to_pos[0]])
            print(from_pos, to_pos)
            return [from_pos, to_pos]

    def calculate_moves_for_all_pieces(self):
        black_totalsum = 0
        white_totalsum = 0
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if not Helpers.is_empty(self.boardpieces[r][c]):
                    # pprint(self.pieces_to_board())
                    # print("INAINTE DE DEZASTRU", r, c)
                    total_moves = self.calculate_possible_moves(r, c)
                    if (self.testing == False):
                        if self.boardpieces[r][c].color == BLACK_COLOR_IDENTIFIER:
                            black_totalsum = black_totalsum+total_moves
                        if self.boardpieces[r][c].color == WHITE_COLOR_IDENTIFIER:
                            white_totalsum = white_totalsum+total_moves
        if self.testing==False:
            if black_totalsum == 0:
                print("NEGRU ESTE IN SAH MAT FRATILOR!!!!!!!!!!!!!")
            if white_totalsum == 0:
                print("ALB ESTE IN SAH MAT FRATILOR!!!!!!!!!!!!!")

    def check_queen_promotion(self, r, c, color):
        """
        Queen promotion for white pawns
        """
        if Helpers.is_pawn(self.boardpieces[r][c]) and (r == 0 and self.boardpieces[r][c].color == WHITE_COLOR_IDENTIFIER):
            self.boardpieces[r][c] = ChessPiece(
                WHITE_QUEEN_IDENTIFIER)
        if Helpers.is_pawn(self.boardpieces[r][c]) and (r == 7 and self.boardpieces[r][c].color == WHITE_COLOR_IDENTIFIER):
            self.boardpieces[r][c] = ChessPiece(
                WHITE_QUEEN_IDENTIFIER)
        """
        Queen promotion for black pawns
        """
        if Helpers.is_pawn(self.boardpieces[r][c]) and (r == 7 and self.boardpieces[r][c].color == BLACK_COLOR_IDENTIFIER):
            self.boardpieces[r][c] = ChessPiece(
                BLACK_QUEEN_IDENTIFIER)
        if Helpers.is_pawn(self.boardpieces[r][c]) and (r == 0 and self.boardpieces[r][c].color == BLACK_COLOR_IDENTIFIER):
            self.boardpieces[r][c] = ChessPiece(
                BLACK_QUEEN_IDENTIFIER)

    # def calculate_next_move(self):
    #     # self.currently_playing = WHITE_COLOR_IDENTIFIER if self.currently_playing == BLACK_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER

    #     best_move = stockfish.get_best_move()

    #     stockfish.make_moves_from_current_position([best_move])
    #     result = self.calculate_move_based_on_prediction(best_move)
    #     print(result, "saluuuuut")
    #     print(best_move)
    #     print("\n\n")
    #     will_capture = False
    #     if not Helpers.is_empty(self.boardpieces[result[1][0]][result[1][1]]):
    #         will_capture = True
    #     self.boardpieces[result[1][0]][result[1][1]
    #                                    ] = self.boardpieces[result[0][0]][result[0][1]]
    #     # self.boardpieces[result[1][0]][result[1][1]].moved = True

    #     self.boardpieces[result[0][0]][result[0][1]] = None
    #     if will_capture:
    #         pygame.mixer.Sound.play(pygame.mixer.Sound(
    #             os.path.join('sounds/capture.wav')))
    #     else:
    #         pygame.mixer.Sound.play(pygame.mixer.Sound(
    #             os.path.join('sounds/move.wav')))
    #     self.calculate_moves_for_all_pieces()
    #     self.is_in_check()

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

    def make_move(self, r, c, r2, c2):

        will_capture = False
        if not Helpers.is_empty(self.boardpieces[r][c]):
            will_capture = True
        self.boardpieces[r][c] = self.boardpieces[r2][c2]
        # pprint(self.pieces_to_board())
        # print("de la mine!!")
        self.boardpieces[r][c].moved = True

        self.boardpieces[r2][c2] = None
        self.calculate_moves_for_all_pieces()
        self.currently_playing = WHITE_COLOR_IDENTIFIER if self.currently_playing == BLACK_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER

        return will_capture
