import pygame
import sys
import os
from constants import *

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

    def __init__(self, type, white_top=False):
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
        self.initialize_pieces()
        self.calculate_moves_for_all_pieces()
        self.playtype = type

        pygame.init()
        pygame.display.set_caption("Chess by Vlad Romila@3A1")
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.isdragging = False
        self.dragged_piece = None
        self.dragged_piece_initial_pos = (0, 0)
        self.lastMousePos = (0, 0)

        self.possible_moves = []

        self.currently_playing = "w"

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
            if c >= 1:
                if Helpers.is_enemy(piece, self.boardpieces[r+piece.dir*1][c-1]):
                    piece.possible_moves.append(
                        (r+piece.dir*1, c-1))
            if c <= 6:
                if Helpers.is_enemy(piece, self.boardpieces[r+piece.dir*1][c+1]):
                    piece.possible_moves.append(
                        (r+piece.dir*1, c+1))
            if Helpers.is_empty(self.boardpieces[r+piece.dir*1][c]):
                piece.possible_moves.append(
                    (r+piece.dir*1, c))
            else:
                return
            if piece.moved == False:
                if Helpers.is_empty(self.boardpieces[r+piece.dir*2][c]):
                    piece.possible_moves.append(
                        (r+piece.dir*2, c))
        # elif isinstance(self.piece, Knight):
        #     possible_move_options = [(self.row+2, self.col+1),
        #                              (self.row+2, self.col-1),
        #                              (self.row+1, self.col+2),
        #                              (self.row+1, self.col-2),
        #                              (self.row-2, self.col+1),
        #                              (self.row-2, self.col-1),
        #                              (self.row-1, self.col+2),
        #                              (self.row-1, self.col-2),
        #                              ]

        #     for move in possible_move_options:
        #         if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7 and boardsquares[move[0]][move[1]].has_opposite_piece_or_empty(self.piece.color):
        #             self.possible_moves.append(move)
        # elif isinstance(self.piece, King):
        #     possible_move_options = [(self.row+1, self.col),
        #                              (self.row+1, self.col-1),
        #                              (self.row+1, self.col+1),
        #                              (self.row, self.col+1),
        #                              (self.row, self.col-1),
        #                              (self.row-1, self.col),
        #                              (self.row-1, self.col-1),
        #                              (self.row-1, self.col+1),
        #                              ]

        #     for move in possible_move_options:
        #         if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7 and boardsquares[move[0]][move[1]].has_opposite_piece_or_empty(self.piece.color):
        #             self.possible_moves.append(move)
        # elif isinstance(self.piece, Queen):
        #     print("salut bro!")
        #     possible_move_options = []

        #     current_r = self.row
        #     current_c = self.col

        #     for c in range(current_c+1, NUMBER_OF_COLUMNS, 1):
        #         if boardsquares[current_r][c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((current_r, c))
        #             if boardsquares[current_r][c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break

        #     for c in range(current_c-1, -1, - 1):
        #         if boardsquares[current_r][c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((current_r, c))
        #             if boardsquares[current_r][c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break

        #     for r in range(current_r-1, -1, -1):
        #         if boardsquares[r][current_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((r, current_c))
        #             if boardsquares[r][current_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break

        #     for r in range(current_r+1, NUMBER_OF_ROWS, 1):
        #         if boardsquares[r][current_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((r, current_c))
        #             if boardsquares[r][current_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break

        #     copy_c = current_c-1
        #     copy_r = current_r-1
        #     while copy_c >= 0 and copy_r >= 0:
        #         if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((copy_r, copy_c))
        #             if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break
        #         copy_c = copy_c-1
        #         copy_r = copy_r-1

        #     copy_c = current_c+1
        #     copy_r = current_r+1
        #     while copy_c < NUMBER_OF_COLUMNS and copy_r < NUMBER_OF_ROWS:
        #         if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((copy_r, copy_c))
        #             if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break
        #         copy_c = copy_c+1
        #         copy_r = copy_r+1

        #     copy_c = current_c-1
        #     copy_r = current_r+1
        #     while copy_c >= 0 and copy_r < NUMBER_OF_ROWS:
        #         if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((copy_r, copy_c))
        #             if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break
        #         copy_c = copy_c-1
        #         copy_r = copy_r+1

        #     copy_c = current_c+1
        #     copy_r = current_r-1
        #     while copy_c < NUMBER_OF_COLUMNS and copy_r >= 0:
        #         if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((copy_r, copy_c))
        #             if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break
        #         copy_c = copy_c+1
        #         copy_r = copy_r-1

        #     print(possible_move_options)
        #     for move in possible_move_options:
        #         if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
        #             self.possible_moves.append(move)
        # elif isinstance(self.piece, Rook):
        #     possible_move_options = []

        #     current_r = self.row
        #     current_c = self.col

        #     for c in range(current_c+1, NUMBER_OF_COLUMNS, 1):
        #         if boardsquares[current_r][c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((current_r, c))
        #             if boardsquares[current_r][c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break

        #     for c in range(current_c-1, -1, - 1):
        #         if boardsquares[current_r][c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((current_r, c))
        #             if boardsquares[current_r][c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break

        #     for r in range(current_r-1, -1, -1):
        #         if boardsquares[r][current_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((r, current_c))
        #             if boardsquares[r][current_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break

        #     for r in range(current_r+1, NUMBER_OF_ROWS, 1):
        #         if boardsquares[r][current_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((r, current_c))
        #             if boardsquares[r][current_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break

        #     print(possible_move_options)
        #     for move in possible_move_options:
        #         if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
        #             self.possible_moves.append(move)
        # elif isinstance(self.piece, Bishop):
        #     possible_move_options = []

        #     current_r = self.row
        #     current_c = self.col

        #     copy_c = current_c-1
        #     copy_r = current_r-1
        #     while copy_c >= 0 and copy_r >= 0:
        #         if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((copy_r, copy_c))
        #             if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break
        #         copy_c = copy_c-1
        #         copy_r = copy_r-1

        #     copy_c = current_c+1
        #     copy_r = current_r+1
        #     while copy_c < NUMBER_OF_COLUMNS and copy_r < NUMBER_OF_ROWS:
        #         if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((copy_r, copy_c))
        #             if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break
        #         copy_c = copy_c+1
        #         copy_r = copy_r+1

        #     copy_c = current_c-1
        #     copy_r = current_r+1
        #     while copy_c >= 0 and copy_r < NUMBER_OF_ROWS:
        #         if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((copy_r, copy_c))
        #             if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break
        #         copy_c = copy_c-1
        #         copy_r = copy_r+1

        #     copy_c = current_c+1
        #     copy_r = current_r-1
        #     while copy_c < NUMBER_OF_COLUMNS and copy_r >= 0:
        #         if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
        #             possible_move_options.append((copy_r, copy_c))
        #             if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
        #                 break
        #         else:
        #             break
        #         copy_c = copy_c+1
        #         copy_r = copy_r-1

        #     print(possible_move_options)
        #     for move in possible_move_options:
        #         if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
        #             self.possible_moves.append(move)

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

    def calculate_moves_for_all_pieces(self):
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if not Helpers.is_empty(self.boardpieces[r][c]):
                    self.calculate_possible_moves(r, c)

    def maingameloop(self):
        is_loop_active = True
        while is_loop_active:
            self.display_background()
            if self.isdragging:
                self.display_possible_moves()
            self.display_pieces()

            if self.isdragging:
                self.display_dragged_piece()

            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    pressed_c = int(e.pos[0]//SQUARE_SIZE)
                    pressed_r = int(e.pos[1]//SQUARE_SIZE)
                    if not Helpers.is_empty(self.boardpieces[pressed_r][pressed_c]) and self.boardpieces[pressed_r][pressed_c].color == self.currently_playing:
                        print("saluttt!!!")
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
                            self.boardpieces[pressed_r][pressed_c] = self.boardpieces[
                                self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]]
                            self.boardpieces[pressed_r][pressed_c].moved = True
                            self.boardpieces[self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]] = None
                            # """
                            # Queen promotion for white pawns
                            # """
                            # if isinstance(self.boardsquares[pressed_r][pressed_c].piece, Pawn) and (pressed_r == 0 and self.boardsquares[pressed_r][pressed_c].piece.color == "white"):
                            #     self.boardsquares[pressed_r][pressed_c] = Square(
                            #         pressed_r, pressed_c, Queen("white"))
                            # """
                            # Queen promotion for black pawns
                            # """
                            # if Helpers.is_pawn(self.boardsquares[pressed_r][pressed_c]) and (pressed_r == 7 and self.boardsquares[pressed_r][pressed_c].piece.color == "black"):
                            #     self.boardpieces[pressed_r][pressed_c] = ChessPiece(BLACK_QUEEN_IDENTIFIER)
                            self.calculate_moves_for_all_pieces()
                            self.currently_playing = WHITE_COLOR_IDENTIFIER if self.currently_playing == BLACK_COLOR_IDENTIFIER else BLACK_COLOR_IDENTIFIER
                        self.isdragging = False
                        self.dragged_piece = None

                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        self.__init__()
                elif e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(1)

            pygame.display.update()


maingame = MainGame(1, True)
maingame.maingameloop()
