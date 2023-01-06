import pygame
import sys
import os
from constants import *
from pprint import pprint
import io
from stockfish import Stockfish
import time
import copy

stockfish = Stockfish(os.path.abspath("stockfish.exe"))

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
        self.set_texture(False)
    """
    Sets the path to the image that will be used to display the piece, based on the color, the type and if the piece is being dragged or not
    """

    def set_texture(self, hovered):
        if hovered == True:
            self.texture = os.path.join(
                f'images/imgs-128px/{self.identifier}.png')
        else:
            self.texture = os.path.join(
                f'images/imgs-80px/{self.identifier}.png')

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves = []


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


class MainGame:

    def __init__(self, type, white_top=False, testing=False):
        self.testing = testing
        self.white_top = white_top
        if white_top == True:
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
        if not testing:
            pygame.init()
            pygame.display.set_caption("Chess by Vlad Romila@3A1")
            self.display = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.isdragging = False
        self.dragged_piece = None
        self.dragged_piece_initial_pos = (0, 0)
        self.lastMousePos = (0, 0)

        self.currently_playing = WHITE_COLOR_IDENTIFIER
        stockfish.set_fen_position(self.pieces_to_fen(WHITE_COLOR_IDENTIFIER))
        if not testing:
            self.wait_for_next_move = white_top
            self.last_time = pygame.time.get_ticks() if white_top else None

    def initialize_pieces(self):
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

    def display_background(self):
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if (r+c) % 2 == 1:
                    to_display_color = BLACK_SQUARE_COLOR
                else:
                    to_display_color = WHITE_SQUARE_COLOR

                to_display_rect = (
                    c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

                pygame.draw.rect(
                    self.display, to_display_color, to_display_rect)

                if c == 0:
                    color = BLACK_SQUARE_COLOR if r % 2 == 0 else WHITE_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        str(r+1 if self.white_top else NUMBER_OF_ROWS-r), 1, color)
                    lbl_pos = (5, 5 + r * SQUARE_SIZE)
                    self.display.blit(lbl, lbl_pos)

                if c == 7:
                    color = WHITE_SQUARE_COLOR if r % 2 == 0 else BLACK_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        str(r+1 if self.white_top else NUMBER_OF_ROWS-r), 1, color)
                    lbl_pos = ((c+1) * SQUARE_SIZE - 15, 5 + r * SQUARE_SIZE)
                    self.display.blit(lbl, lbl_pos)

                if r == 7:
                    color = BLACK_SQUARE_COLOR if (
                        r + c) % 2 == 0 else WHITE_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        ALPHACOLS[NUMBER_OF_COLUMNS - c-1] if self.white_top else ALPHACOLS[c], 1, color)
                    lbl_pos = (c * SQUARE_SIZE + SQUARE_SIZE /
                               2 - 5, SCREEN_HEIGHT - 120)
                    # blit
                    self.display.blit(lbl, lbl_pos)

                if r == 0:
                    color = BLACK_SQUARE_COLOR if (
                        r + c) % 2 == 0 else WHITE_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        ALPHACOLS[NUMBER_OF_COLUMNS - c-1] if self.white_top else ALPHACOLS[c], 1, color)
                    lbl_pos = (c * SQUARE_SIZE + SQUARE_SIZE/2 - 5, 0)
                    # blit
                    self.display.blit(lbl, lbl_pos)

    def display_possible_moves(self):
        possible_moves = self.boardpieces[self.dragged_piece_initial_pos[0]
                                          ][self.dragged_piece_initial_pos[1]].possible_moves
        for move in possible_moves:
            to_display_rect = (
                move[1]*SQUARE_SIZE, move[0]*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

            pygame.draw.rect(
                self.display, POSSIBLE_MOVE_HIGHLIGHT, to_display_rect, 3)

    def display_pieces(self):
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                # piece ?
                if not Helpers.is_empty(self.boardpieces[r][c]):
                    piece = self.boardpieces[r][c]
                    piece.set_texture(False)
                    img = pygame.image.load(piece.texture)
                    img_center = c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2
                    piece.texture_rect = img.get_rect(center=img_center)
                    self.display.blit(img, piece.texture_rect)

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
                    # if self.testing == False:
                    #     game_copy = MainGame(
                    #         self.playtype, self.white_top, True)
                    #     game_copy.boardpieces = copy.deepcopy(self.boardpieces)
                    #     if not game_copy.is_in_check_after_move((r, c), move):
                    #         piece.possible_moves.append(move)
                    # else:
                        piece.possible_moves.append(move)

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
                    # if self.testing == False:
                    #     game_copy = MainGame(
                    #         self.playtype, self.white_top, True)
                    #     game_copy.boardpieces = copy.deepcopy(self.boardpieces)
                    #     if not game_copy.is_in_check_after_move((r, c), move):
                    #         piece.possible_moves.append(move)
                    # else:
                        piece.possible_moves.append(move)
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
                    # if self.testing == False:
                    #     game_copy = MainGame(
                    #         self.playtype, self.white_top, True)
                    #     game_copy.boardpieces = copy.deepcopy(self.boardpieces)
                    #     if not game_copy.is_in_check_after_move((r, c), move):
                    #         piece.possible_moves.append(move)
                    # else:
                        piece.possible_moves.append(move)
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

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    # if self.testing == False:
                    #     game_copy = MainGame(
                    #         self.playtype, self.white_top, True)
                    #     game_copy.boardpieces = copy.deepcopy(self.boardpieces)
                    #     if not game_copy.is_in_check_after_move((r, c), move):
                    #         piece.possible_moves.append(move)
                    # else:
                        piece.possible_moves.append(move)
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

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    # if self.testing == False:
                    #     game_copy = MainGame(
                    #         self.playtype, self.white_top, True)
                    #     game_copy.boardpieces = copy.deepcopy(self.boardpieces)
                    #     if not game_copy.is_in_check_after_move((r, c), move):
                    #         piece.possible_moves.append(move)
                    # else:
                        piece.possible_moves.append(move)
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

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    # if self.testing == False:
                    #     game_copy = MainGame(
                    #         self.playtype, self.white_top, True)
                    #     game_copy.boardpieces = copy.deepcopy(self.boardpieces)
                    #     if not game_copy.is_in_check_after_move((r, c), move):
                    #         piece.possible_moves.append(move)
                    # else:
                        piece.possible_moves.append(move)

    def display_dragged_piece(self):
        self.dragged_piece.set_texture(True)
        used_texture = self.dragged_piece.texture
        to_show_image = pygame.image.load(used_texture)
        # rect
        img_center = (self.lastMousePos[0], self.lastMousePos[1])
        self.dragged_piece.texture_rect = to_show_image.get_rect(
            center=img_center)
        # blit
        self.display.blit(to_show_image, self.dragged_piece.texture_rect)

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
        #pprint(board)
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
            #print(s.getvalue())
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
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if not Helpers.is_empty(self.boardpieces[r][c]):
                    self.calculate_possible_moves(r, c)

    def calculate_next_move(self):
        #self.currently_playing = WHITE_COLOR_IDENTIFIER if self.currently_playing == BLACK_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER

        best_move = stockfish.get_best_move()

        stockfish.make_moves_from_current_position([best_move])
        result = self.calculate_move_based_on_prediction(best_move)
        print(result,"saluuuuut")
        print(best_move)
        print("\n\n")
        will_capture = False
        if not Helpers.is_empty(self.boardpieces[result[1][0]][result[1][1]]):
            will_capture = True
        self.boardpieces[result[1][0]][result[1][1]
                                       ] = self.boardpieces[result[0][0]][result[0][1]]
        #self.boardpieces[result[1][0]][result[1][1]].moved = True
        
        self.boardpieces[result[0][0]][result[0][1]] = None
        if will_capture:
            pygame.mixer.Sound.play(pygame.mixer.Sound(
                os.path.join('sounds/capture.wav')))
        else:
            pygame.mixer.Sound.play(pygame.mixer.Sound(
                os.path.join('sounds/move.wav')))
        self.calculate_moves_for_all_pieces()
        self.is_in_check()

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
        to_check_board = self.pieces_to_board()
        copied_board = MainGame(self.playtype, self.white_top, True)
        # print(copied_board.boardsquares)
        # pprint(to_check_board)
        # print(is_check, to_save_pieces)

    def is_in_check_after_move(self, from_pos, to_pos):
        king_pos = (-1, -1)
        self.boardpieces[to_pos[0]][to_pos[1]
                                    ] = self.boardpieces[from_pos[0]][from_pos[1]]
        # self.boardpieces[to_pos[0]][to_pos[1]].moved = True
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

    def maingameloop(self):
        is_loop_active = True
        while is_loop_active:
            self.display_background()
            if self.isdragging:
                self.display_possible_moves()
            self.display_pieces()

            if self.isdragging:
                self.display_dragged_piece()
            # if self.wait_for_next_move:
            #     if pygame.time.get_ticks() - self.last_time > 1000:
            #         self.calculate_next_move()
            #         self.wait_for_next_move = False
            #         self.last_time = None
            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    print(self.playtype,"nu mai inteleg nimic smm")
                    pprint(self.currently_playing)
                    pressed_c = int(e.pos[0]//SQUARE_SIZE)
                    pressed_r = int(e.pos[1]//SQUARE_SIZE)
                    if not Helpers.is_empty(self.boardpieces[pressed_r][pressed_c]) and (((self.playtype == 2 and self.white_top and self.currently_playing == BLACK_COLOR_IDENTIFIER) or (self.playtype == 2 and not self.white_top and self.currently_playing == WHITE_COLOR_IDENTIFIER)) or (self.playtype == 1 and self.boardpieces[pressed_r][pressed_c].color == self.currently_playing)):
                        self.lastMousePos = (e.pos[0], e.pos[1])
                        self.dragged_piece = self.boardpieces[pressed_r][pressed_c]
                        self.dragged_piece_initial_pos = (pressed_r, pressed_c)
                        self.isdragging = True
                elif e.type == pygame.MOUSEMOTION:
                    if self.isdragging:
                        self.lastMousePos = (e.pos[0], e.pos[1])
                elif e.type == pygame.MOUSEBUTTONUP:
                    if self.isdragging:
                        pressed_c = int(e.pos[0]//SQUARE_SIZE)
                        pressed_r = int(e.pos[1]//SQUARE_SIZE)
                        if (pressed_r, pressed_c) in self.boardpieces[self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]].possible_moves:
                            will_capture = False
                            if not Helpers.is_empty(self.boardpieces[pressed_r][pressed_c]):
                                will_capture = True
                            self.boardpieces[pressed_r][pressed_c] = self.boardpieces[
                                self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]]
                            self.boardpieces[pressed_r][pressed_c].moved = True
                            self.boardpieces[self.dragged_piece_initial_pos[0]
                                             ][self.dragged_piece_initial_pos[1]] = None
                            if will_capture:
                                pygame.mixer.Sound.play(pygame.mixer.Sound(
                                    os.path.join('sounds/capture.wav')))
                            else:
                                pygame.mixer.Sound.play(pygame.mixer.Sound(
                                    os.path.join('sounds/move.wav')))
                            """
                            Queen promotion for white pawns
                            """
                            if Helpers.is_pawn(self.boardpieces[pressed_r][pressed_c]) and (pressed_r == 0 and self.boardpieces[pressed_r][pressed_c].color == WHITE_COLOR_IDENTIFIER):
                                self.boardpieces[pressed_r][pressed_c] = ChessPiece(
                                    WHITE_QUEEN_IDENTIFIER)
                            if Helpers.is_pawn(self.boardpieces[pressed_r][pressed_c]) and (pressed_r == 7 and self.boardpieces[pressed_r][pressed_c].color == WHITE_COLOR_IDENTIFIER):
                                self.boardpieces[pressed_r][pressed_c] = ChessPiece(
                                    WHITE_QUEEN_IDENTIFIER)
                            """
                            Queen promotion for black pawns
                            """
                            if Helpers.is_pawn(self.boardpieces[pressed_r][pressed_c]) and (pressed_r == 7 and self.boardpieces[pressed_r][pressed_c].color == BLACK_COLOR_IDENTIFIER):
                                self.boardpieces[pressed_r][pressed_c] = ChessPiece(
                                    BLACK_QUEEN_IDENTIFIER)
                            if Helpers.is_pawn(self.boardpieces[pressed_r][pressed_c]) and (pressed_r == 0 and self.boardpieces[pressed_r][pressed_c].color == BLACK_COLOR_IDENTIFIER):
                                self.boardpieces[pressed_r][pressed_c] = ChessPiece(
                                    BLACK_QUEEN_IDENTIFIER)
                            print(self.calculate_move_code_from_coordinates(
                                self.dragged_piece_initial_pos[0], self.dragged_piece_initial_pos[1])+self.calculate_move_code_from_coordinates(pressed_r, pressed_c))
                            print("\n\n")
                            if self.playtype==2:
                                stockfish.make_moves_from_current_position([self.calculate_move_code_from_coordinates(
                                    self.dragged_piece_initial_pos[0], self.dragged_piece_initial_pos[1])+self.calculate_move_code_from_coordinates(pressed_r, pressed_c)])
                            self.calculate_moves_for_all_pieces()
                            print("gata",self.currently_playing)
                            if self.playtype==1:
                                self.currently_playing = WHITE_COLOR_IDENTIFIER if self.currently_playing == BLACK_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER
                            print("gata2",self.currently_playing)
                            # if self.playtype == 2:
                            #     self.wait_for_next_move = True
                            #     self.last_time = pygame.time.get_ticks()
                            self.calculate_next_move()

                        self.isdragging = False
                        self.dragged_piece = None
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        self.__init__()
                elif e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(1)

            pygame.display.update()


maingame = MainGame(2, False)
maingame.maingameloop()
