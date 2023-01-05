import pygame
import sys
import os
from constants import *

"""
Class that saves the data that matters for every piece
"""


class ChessPiece:

    def __init__(self, name, color, texture=None, texture_rect=None):
        self.name = name
        self.color = color
        self.moves = []
        self.moved = False
        self.texture = texture
        self.set_texture(False)
        self.texture_rect = texture_rect
    """
    Sets the path to the image that will be used to display the piece, based on the color, the type and if the piece is being dragged or not
    """

    def set_texture(self, hovered):
        if hovered == True:
            self.texture = os.path.join(
                f'images/imgs-128px/{self.color}_{self.name}.png')
        else:
            self.texture = os.path.join(
                f'images/imgs-80px/{self.color}_{self.name}.png')

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves = []


class Pawn(ChessPiece):

    def __init__(self, color):
        self.dir = -1 if color == 'white' else 1
        self.en_passant = False
        super().__init__('pawn', color)


class Knight(ChessPiece):

    def __init__(self, color):
        super().__init__('knight', color)


class Bishop(ChessPiece):

    def __init__(self, color):
        super().__init__('bishop', color)


class Queen(ChessPiece):

    def __init__(self, color):
        super().__init__('queen', color)


class Rook(ChessPiece):

    def __init__(self, color):
        super().__init__('rook', color)


class King(ChessPiece):

    def __init__(self, color):
        super().__init__('king', color)


class Square:

    ALPHACOLS = {0: 'a', 1: 'b', 2: 'c',
                 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece
        self.alphacol = self.ALPHACOLS[col]
        self.possible_moves = []

    def has_piece(self):
        return self.piece != None

    def isempty(self):
        return not self.has_piece()

    def has_enemy_piece(self, color):
        return self.has_piece() and self.piece.color != color

    def has_opposite_piece_or_empty(self, color):
        return self.isempty() or self.has_enemy_piece(color)

    def calculate_possible_moves(self, boardsquares):
        self.possible_moves = []
        if isinstance(self.piece, Pawn):
            if self.col >= 1:
                if boardsquares[self.row+self.piece.dir*1][self.col-1].has_enemy_piece(self.piece.color):
                    self.possible_moves.append(
                        (self.row+self.piece.dir*1, self.col-1))
            if self.col <= 6:
                if boardsquares[self.row+self.piece.dir*1][self.col+1].has_enemy_piece(self.piece.color):
                    self.possible_moves.append(
                        (self.row+self.piece.dir*1, self.col+1))
            if boardsquares[self.row+self.piece.dir*1][self.col].isempty():
                self.possible_moves.append(
                    (self.row+self.piece.dir*1, self.col))
            else:
                return
            if self.piece.moved == False:
                if boardsquares[self.row+self.piece.dir*2][self.col].isempty():
                    self.possible_moves.append(
                        (self.row+self.piece.dir*2, self.col))
        elif isinstance(self.piece, Knight):
            possible_move_options = [(self.row+2, self.col+1),
                                     (self.row+2, self.col-1),
                                     (self.row+1, self.col+2),
                                     (self.row+1, self.col-2),
                                     (self.row-2, self.col+1),
                                     (self.row-2, self.col-1),
                                     (self.row-1, self.col+2),
                                     (self.row-1, self.col-2),
                                     ]

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7 and boardsquares[move[0]][move[1]].has_opposite_piece_or_empty(self.piece.color):
                    self.possible_moves.append(move)
        elif isinstance(self.piece, King):
            possible_move_options = [(self.row+1, self.col),
                                     (self.row+1, self.col-1),
                                     (self.row+1, self.col+1),
                                     (self.row, self.col+1),
                                     (self.row, self.col-1),
                                     (self.row-1, self.col),
                                     (self.row-1, self.col-1),
                                     (self.row-1, self.col+1),
                                     ]

            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7 and boardsquares[move[0]][move[1]].has_opposite_piece_or_empty(self.piece.color):
                    self.possible_moves.append(move)
        elif isinstance(self.piece, Queen):
            print("salut bro!")
            possible_move_options = []

            current_r = self.row
            current_c = self.col

            for c in range(current_c+1, NUMBER_OF_COLUMNS, 1):
                if boardsquares[current_r][c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((current_r, c))
                    if boardsquares[current_r][c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break

            for c in range(current_c-1, -1, - 1):
                if boardsquares[current_r][c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((current_r, c))
                    if boardsquares[current_r][c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break

            for r in range(current_r-1, -1, -1):
                if boardsquares[r][current_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((r, current_c))
                    if boardsquares[r][current_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break

            for r in range(current_r+1, NUMBER_OF_ROWS, 1):
                if boardsquares[r][current_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((r, current_c))
                    if boardsquares[r][current_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break

            copy_c = current_c-1
            copy_r = current_r-1
            while copy_c >= 0 and copy_r >= 0:
                if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((copy_r, copy_c))
                    if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break
                copy_c = copy_c-1
                copy_r = copy_r-1

            copy_c = current_c+1
            copy_r = current_r+1
            while copy_c < NUMBER_OF_COLUMNS and copy_r < NUMBER_OF_ROWS:
                if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((copy_r, copy_c))
                    if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break
                copy_c = copy_c+1
                copy_r = copy_r+1

            copy_c = current_c-1
            copy_r = current_r+1
            while copy_c >= 0 and copy_r < NUMBER_OF_ROWS:
                if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((copy_r, copy_c))
                    if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break
                copy_c = copy_c-1
                copy_r = copy_r+1

            copy_c = current_c+1
            copy_r = current_r-1
            while copy_c < NUMBER_OF_COLUMNS and copy_r >= 0:
                if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((copy_r, copy_c))
                    if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break
                copy_c = copy_c+1
                copy_r = copy_r-1

            print(possible_move_options)
            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    self.possible_moves.append(move)
        elif isinstance(self.piece, Rook):
            possible_move_options = []

            current_r = self.row
            current_c = self.col

            for c in range(current_c+1, NUMBER_OF_COLUMNS, 1):
                if boardsquares[current_r][c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((current_r, c))
                    if boardsquares[current_r][c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break

            for c in range(current_c-1, -1, - 1):
                if boardsquares[current_r][c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((current_r, c))
                    if boardsquares[current_r][c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break

            for r in range(current_r-1, -1, -1):
                if boardsquares[r][current_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((r, current_c))
                    if boardsquares[r][current_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break

            for r in range(current_r+1, NUMBER_OF_ROWS, 1):
                if boardsquares[r][current_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((r, current_c))
                    if boardsquares[r][current_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break

            print(possible_move_options)
            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    self.possible_moves.append(move)
        elif isinstance(self.piece, Bishop):
            possible_move_options = []

            current_r = self.row
            current_c = self.col

            copy_c = current_c-1
            copy_r = current_r-1
            while copy_c >= 0 and copy_r >= 0:
                if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((copy_r, copy_c))
                    if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break
                copy_c = copy_c-1
                copy_r = copy_r-1

            copy_c = current_c+1
            copy_r = current_r+1
            while copy_c < NUMBER_OF_COLUMNS and copy_r < NUMBER_OF_ROWS:
                if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((copy_r, copy_c))
                    if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break
                copy_c = copy_c+1
                copy_r = copy_r+1

            copy_c = current_c-1
            copy_r = current_r+1
            while copy_c >= 0 and copy_r < NUMBER_OF_ROWS:
                if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((copy_r, copy_c))
                    if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break
                copy_c = copy_c-1
                copy_r = copy_r+1

            copy_c = current_c+1
            copy_r = current_r-1
            while copy_c < NUMBER_OF_COLUMNS and copy_r >= 0:
                if boardsquares[copy_r][copy_c].has_opposite_piece_or_empty(self.piece.color):
                    possible_move_options.append((copy_r, copy_c))
                    if boardsquares[copy_r][copy_c].has_enemy_piece(self.piece.color):
                        break
                else:
                    break
                copy_c = copy_c+1
                copy_r = copy_r-1

            print(possible_move_options)
            for move in possible_move_options:
                if move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7:
                    self.possible_moves.append(move)


class MainGame:

    def __init__(self):
        self.boardsquares = [[Square for c in range(
            NUMBER_OF_COLUMNS)] for r in range(NUMBER_OF_ROWS)]
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                self.boardsquares[r][c] = Square(r, c)
        self.initialize_pieces("white")
        self.initialize_pieces("black")
        pygame.init()
        pygame.display.set_caption("Chess by Vlad Romila@3A1")
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.isdragging = False
        self.dragged_piece = None
        self.dragged_piece_initial_pos = (0, 0)
        self.lastMousePos = (0, 0)

        self.possible_moves = []

        self.currently_playing = "white"

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
        possible_moves = self.boardsquares[self.dragged_piece_initial_pos[0]
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
                if self.boardsquares[r][c].has_piece():
                    piece = self.boardsquares[r][c].piece
                    piece.set_texture(False)
                    img = pygame.image.load(piece.texture)
                    img_center = c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2
                    piece.texture_rect = img.get_rect(center=img_center)
                    self.display.blit(img, piece.texture_rect)

    def initialize_pieces(self, color):
        if color == "white":
            fr = 6
            sr = 7
        else:
            fr = 1
            sr = 0

        # pawns
        for c in range(NUMBER_OF_COLUMNS):
            self.boardsquares[fr][c] = Square(fr, c, Pawn(color))
            self.boardsquares[fr][c].calculate_possible_moves(
                self.boardsquares)
        # Initializing the knights
        self.boardsquares[sr][1] = Square(sr, 1, Knight(color))
        self.boardsquares[sr][6] = Square(sr, 6, Knight(color))
        self.boardsquares[sr][1].calculate_possible_moves(self.boardsquares)
        self.boardsquares[sr][6].calculate_possible_moves(self.boardsquares)
        # bishops
        self.boardsquares[sr][2] = Square(sr, 2, Bishop(color))
        self.boardsquares[sr][5] = Square(sr, 5, Bishop(color))
        self.boardsquares[sr][2].calculate_possible_moves(self.boardsquares)
        self.boardsquares[sr][5].calculate_possible_moves(self.boardsquares)
        # rooks
        self.boardsquares[sr][0] = Square(sr, 0, Rook(color))
        self.boardsquares[sr][7] = Square(sr, 7, Rook(color))
        self.boardsquares[sr][0].calculate_possible_moves(self.boardsquares)
        self.boardsquares[sr][7].calculate_possible_moves(self.boardsquares)
        # queen
        self.boardsquares[sr][3] = Square(sr, 3, Queen(color))
        self.boardsquares[sr][3].calculate_possible_moves(self.boardsquares)
        # king
        self.boardsquares[sr][4] = Square(sr, 4, King(color))
        self.boardsquares[sr][4].calculate_possible_moves(self.boardsquares)

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
        for squares_r in self.boardsquares:
            for square in squares_r:
                square.calculate_possible_moves(self.boardsquares)

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
                    print(pressed_c, pressed_r)
                    print(self.boardsquares[pressed_r][pressed_c].has_piece())
                    if self.boardsquares[pressed_r][pressed_c].has_piece() and self.boardsquares[pressed_r][pressed_c].piece.color == self.currently_playing:
                        self.lastMousePos = (e.pos[0], e.pos[1])
                        self.dragged_piece = self.boardsquares[pressed_r][pressed_c].piece
                        self.dragged_piece_initial_pos = (pressed_r, pressed_c)
                        self.isdragging = True
                        print(self.boardsquares[pressed_r]
                              [pressed_c].possible_moves)
                elif e.type == pygame.MOUSEMOTION:
                    if self.isdragging:
                        self.lastMousePos = (e.pos[0], e.pos[1])
                elif e.type == pygame.MOUSEBUTTONUP:
                    if self.isdragging:
                        pressed_c = int(e.pos[0]//SQUARE_SIZE)
                        pressed_r = int(e.pos[1]//SQUARE_SIZE)
                        if (pressed_r, pressed_c) in self.boardsquares[self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]].possible_moves:
                            self.boardsquares[pressed_r][pressed_c].piece = self.boardsquares[
                                self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]].piece
                            self.boardsquares[pressed_r][pressed_c].piece.moved = True
                            self.boardsquares[self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]] = Square(
                                self.dragged_piece_initial_pos[0], self.dragged_piece_initial_pos[1], None)
                            """
                            Queen promotion for white pawns
                            """
                            if isinstance(self.boardsquares[pressed_r][pressed_c].piece, Pawn) and (pressed_r == 0 and self.boardsquares[pressed_r][pressed_c].piece.color == "white"):
                                self.boardsquares[pressed_r][pressed_c] = Square(
                                    pressed_r, pressed_c, Queen("white"))
                            """
                            Queen promotion for black pawns
                            """
                            if isinstance(self.boardsquares[pressed_r][pressed_c].piece, Pawn) and (pressed_r == 7 and self.boardsquares[pressed_r][pressed_c].piece.color == "black"):
                                self.boardsquares[pressed_r][pressed_c] = Square(
                                    pressed_r, pressed_c, Queen("black"))
                            self.calculate_moves_for_all_pieces()
                            self.currently_playing = "white" if self.currently_playing == "black" else "black"
                        self.isdragging = False
                        self.dragged_piece = None
                        
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        self.__init__()
                elif e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(1)

            pygame.display.update()


maingame = MainGame()
maingame.maingameloop()
