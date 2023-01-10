import pygame
import sys
import os
from constants import *
from pprint import pprint
from stockfish import Stockfish
from chessboard import ChessBoard, Helpers
import chess
import random
import argparse

"""
Class that handles the main game logic, event handlers and pygame renderers
"""


class MainGame:

    def __init__(self, type, white_top, ai):

        self.chessboard = ChessBoard(type, white_top, ai)
        pygame.init()
        pygame.display.set_caption("Chess by Vlad Romila@3A1")
        self.display = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.startdragging = False
        self.isdragging = False
        self.ispicked = False
        self.dragged_piece = None
        self.dragged_piece_initial_pos = (0, 0)
        self.lastMousePos = (0, 0)

    """
    Function that returns the file path to the image of a piece based on its identifier and hovered state
    identifier --> String - identifier of the piece
    hovered --> Boolean - True if the piece is being tracked
    """

    def get_texture(self, identifier, hovered):
        if hovered == True:
            return os.path.join(
                f'images/imgs-128px/{identifier}.png')
        else:
            return os.path.join(
                f'images/imgs-80px/{identifier}.png')

    """
    Function that displays the background
    """
    def display_background(self):
        for cr in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                if (cr+c) % 2 == 1:
                    to_display_color = BLACK_SQUARE_COLOR
                else:
                    to_display_color = WHITE_SQUARE_COLOR

                if self.chessboard.last_move != None:
                    if (cr, c) in self.chessboard.last_move:
                        if (cr+c) % 2 == 1:
                            to_display_color = BLACK_YELLOW_COLOR
                        else:
                            to_display_color = WHITE_YELLOW_COLOR
                r = cr+1
                to_display_rect = (
                    c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

                pygame.draw.rect(
                    self.display, to_display_color, to_display_rect)

                if c == 0:
                    color = BLACK_SQUARE_COLOR if r % 2 == 1 else WHITE_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        str(r if self.chessboard.white_top else NUMBER_OF_ROWS-r+1), 1, color)
                    lbl_pos = (5, 5 + r * SQUARE_SIZE)
                    self.display.blit(lbl, lbl_pos)

                if c == 7:
                    color = WHITE_SQUARE_COLOR if r % 2 == 1 else BLACK_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        str(r if self.chessboard.white_top else NUMBER_OF_ROWS-r+1), 1, color)
                    lbl_pos = ((c+1) * SQUARE_SIZE - 15, 5 + r * SQUARE_SIZE)
                    self.display.blit(lbl, lbl_pos)

                if r == 8:
                    color = BLACK_SQUARE_COLOR if (
                        r + c) % 2 == 1 else WHITE_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        ALPHACOLS[NUMBER_OF_COLUMNS - c-1] if self.chessboard.white_top else ALPHACOLS[c], 1, color)
                    lbl_pos = (c * SQUARE_SIZE + SQUARE_SIZE /
                               2 - 5, SCREEN_HEIGHT - 120)
                    # blit
                    self.display.blit(lbl, lbl_pos)

                if r == 1:
                    color = BLACK_SQUARE_COLOR if (
                        r + c) % 2 == 1 else WHITE_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        ALPHACOLS[NUMBER_OF_COLUMNS - c-1] if self.chessboard.white_top else ALPHACOLS[c], 1, color)
                    lbl_pos = (c * SQUARE_SIZE + SQUARE_SIZE /
                               2 - 5, SQUARE_SIZE + 0)
                    # blit
                    self.display.blit(lbl, lbl_pos)
        top_capture_container = (
            0, 0, 8*SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(
            self.display, BLACK_SQUARE_COLOR, top_capture_container)
        top_capture_container_separator = (
            0, SQUARE_SIZE-3, 8*SQUARE_SIZE, 3)
        pygame.draw.rect(
            self.display, (0, 0, 0), top_capture_container_separator)

        bottom_capture_container = (
            0, 9*SQUARE_SIZE, 8*SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(
            self.display, WHITE_SQUARE_COLOR, bottom_capture_container)
        bottom_capture_container_separator = (
            0, 9*SQUARE_SIZE, 8*SQUARE_SIZE, 3)
        pygame.draw.rect(
            self.display, (0, 0, 0), bottom_capture_container_separator)
    """
    Function that displays the possible moves of a piece
    """
    def display_possible_moves(self):
        possible_moves = self.chessboard.boardpieces[self.dragged_piece_initial_pos[0]
                                                     ][self.dragged_piece_initial_pos[1]].possible_moves
        for move in possible_moves:
            to_display_rect = (
                move[1]*SQUARE_SIZE, (move[0]+1)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

            pygame.draw.rect(
                self.display, POSSIBLE_MOVE_HIGHLIGHT, to_display_rect, 3)

    """
    Function that displays the pieces
    """
    def display_pieces(self):
        for r in range(NUMBER_OF_ROWS):
            for c in range(NUMBER_OF_COLUMNS):
                # piece ?
                if not Helpers.is_empty(self.chessboard.boardpieces[r][c]):
                    if (self.isdragging == True and (self.dragged_piece_initial_pos != (r, c))) or self.isdragging == False:
                        piece = self.chessboard.boardpieces[r][c]
                        texture = self.get_texture(piece.identifier, False)
                        img = pygame.image.load(texture)
                        img_center = c * SQUARE_SIZE + \
                            SQUARE_SIZE // 2, (r+1) * \
                            SQUARE_SIZE + SQUARE_SIZE // 2
                        texture_rect = img.get_rect(center=img_center)
                        self.display.blit(img, texture_rect)
    """
    Function that displays the pieces captured by the white color
    """
    def display_white_captured_pieces(self):
        row_pos = 9 * SQUARE_SIZE + SQUARE_SIZE // 2 if self.chessboard.white_top == False else 0 * \
            SQUARE_SIZE + SQUARE_SIZE // 2
        has_pawns = 1 if self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_PAWN_IDENTIFIER] > 0 else 0
        pawns = self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_PAWN_IDENTIFIER]
        for i in range(pawns):
            texture = self.get_texture(BLACK_PAWN_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = 0.25*i * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        has_bishops = 1 if self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_BISHOP_IDENTIFIER] > 0 else 0
        bishops = self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_BISHOP_IDENTIFIER]
        for i in range(bishops):
            texture = self.get_texture(BLACK_BISHOP_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = (has_pawns*0.5 + pawns*0.25 + 0.25*i) * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        has_knights = 1 if self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_KNIGHT_IDENTIFIER] > 0 else 0
        knights = self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_KNIGHT_IDENTIFIER]
        for i in range(knights):
            texture = self.get_texture(BLACK_KNIGHT_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = (has_pawns*0.5 + has_bishops*0.5 + pawns*0.25 + bishops*0.25 + 0.25*i) * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        has_rooks = 1 if self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_ROOK_IDENTIFIER] > 0 else 0
        rooks = self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_ROOK_IDENTIFIER]
        for i in range(rooks):
            texture = self.get_texture(BLACK_ROOK_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = (has_pawns*0.5 + has_bishops*0.5 + has_knights*0.5 + pawns*0.25 + bishops*0.25 + knights*0.25 + 0.25*i) * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        queens = self.chessboard.captures[WHITE_COLOR_IDENTIFIER][BLACK_QUEEN_IDENTIFIER]
        for i in range(queens):
            texture = self.get_texture(BLACK_QUEEN_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = (has_pawns*0.5 + has_bishops*0.5 + has_knights*0.5 + has_rooks*0.5 + pawns*0.25 + bishops*0.25 + knights*0.25 + rooks*0.25 + 0.25*i) * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        # for i in range(2):
        #     texture = self.get_texture(WHITE_KNIGHT_IDENTIFIER, False)
        #     img = pygame.image.load(texture)
        #     img_center = (0.5 + 8*0.25 + 0.25*i) * SQUARE_SIZE + \
        #         SQUARE_SIZE // 2, 9 * SQUARE_SIZE + SQUARE_SIZE // 2
        #     texture_rect = img.get_rect(center=img_center)
        #     self.display.blit(img, texture_rect)
    """
    Function that displays the pieces captured by the black color
    """
    def display_black_captured_pieces(self):
        has_pawns = 1 if self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_PAWN_IDENTIFIER] > 0 else 0
        row_pos = 0 * SQUARE_SIZE + SQUARE_SIZE // 2 if self.chessboard.white_top == False else 9 * \
            SQUARE_SIZE + SQUARE_SIZE // 2
        pawns = self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_PAWN_IDENTIFIER]
        for i in range(pawns):
            texture = self.get_texture(WHITE_PAWN_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = 0.25*i * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        has_bishops = 1 if self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_BISHOP_IDENTIFIER] > 0 else 0
        bishops = self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_BISHOP_IDENTIFIER]
        for i in range(bishops):
            texture = self.get_texture(WHITE_BISHOP_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = (has_pawns*0.5 + pawns*0.25 + 0.25*i) * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        has_knights = 1 if self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_KNIGHT_IDENTIFIER] > 0 else 0
        knights = self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_KNIGHT_IDENTIFIER]
        for i in range(knights):
            texture = self.get_texture(WHITE_KNIGHT_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = (has_pawns*0.5 + has_bishops*0.5 + pawns*0.25 + bishops*0.25 + 0.25*i) * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        has_rooks = 1 if self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_ROOK_IDENTIFIER] > 0 else 0
        rooks = self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_ROOK_IDENTIFIER]
        for i in range(rooks):
            texture = self.get_texture(WHITE_ROOK_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = (has_pawns*0.5 + has_bishops*0.5 + has_knights*0.5 + pawns*0.25 + bishops*0.25 + knights*0.25 + 0.25*i) * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        queens = self.chessboard.captures[BLACK_COLOR_IDENTIFIER][WHITE_QUEEN_IDENTIFIER]
        for i in range(queens):
            texture = self.get_texture(WHITE_QUEEN_IDENTIFIER, False)
            img = pygame.image.load(texture)
            img_center = (has_pawns*0.5 + has_bishops*0.5 + has_knights*0.5 + has_rooks*0.5 + pawns*0.25 + bishops*0.25 + knights*0.25 + rooks*0.25 + 0.25*i) * SQUARE_SIZE + \
                SQUARE_SIZE // 2, row_pos
            texture_rect = img.get_rect(center=img_center)
            self.display.blit(img, texture_rect)

        # for i in range(2):
        #     texture = self.get_texture(WHITE_KNIGHT_IDENTIFIER, False)
        #     img = pygame.image.load(texture)
        #     img_center = (0.5 + 8*0.25 + 0.25*i) * SQUARE_SIZE + \
        #         SQUARE_SIZE // 2, 9 * SQUARE_SIZE + SQUARE_SIZE // 2
        #     texture_rect = img.get_rect(center=img_center)
        #     self.display.blit(img, texture_rect)

    """
    Function that renders the dragged piece
    """
    def display_dragged_piece(self):
        texture = self.get_texture(self.dragged_piece.identifier, True)
        to_show_image = pygame.image.load(texture)
        # rect
        img_center = (self.lastMousePos[0], self.lastMousePos[1])
        texture_rect = to_show_image.get_rect(
            center=img_center)
        # blit
        self.display.blit(to_show_image, texture_rect)

    """
    Function that displays the game ended screen
    """
    def display_game_ended_screen(self):
        to_display_rect = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        pygame.draw.rect(
            self.display, WHITE_SQUARE_COLOR, to_display_rect)
        color = BLACK_SQUARE_COLOR
        title = pygame.font.SysFont('monospace', 60, bold=True).render(
            "Game Over", 1, color)
        title_rect = title.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2-25))
        # blit
        self.display.blit(title, title_rect)
        subtitle = pygame.font.SysFont('monospace', 45, bold=True).render(
            self.chessboard.game_ended_reason, 1, color)
        subtitle_rect = subtitle.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2+25))
        # blit
        self.display.blit(subtitle, subtitle_rect)

    """
    Function that handles the loop where the elements are rendered, and the event listeners are being handles
    """
    def maingameloop(self):
        is_loop_active = True
        while is_loop_active:
            if self.chessboard.show_end_screen:
                self.display_game_ended_screen()
            else:
                self.display_background()
                if self.isdragging or self.ispicked:
                    self.display_possible_moves()
                self.display_pieces()
                self.display_white_captured_pieces()
                self.display_black_captured_pieces()
            if self.isdragging:
                self.display_dragged_piece()
            if not self.chessboard.game_ended:
                if self.chessboard.wait_for_next_move:
                    if (self.chessboard.last_time == None):
                        self.chessboard.last_time = pygame.time.get_ticks()
                    if pygame.time.get_ticks() - self.chessboard.last_time > 10:
                        will_capture = self.chessboard.calculate_next_move()
                        if will_capture:
                            pygame.mixer.Sound.play(pygame.mixer.Sound(
                                os.path.join('sounds/capture.wav')))
                        else:
                            pygame.mixer.Sound.play(pygame.mixer.Sound(
                                os.path.join('sounds/move.wav')))

                        self.wait_for_next_move = False
                        self.last_time = None
                        if (self.chessboard.playtype == 3):
                            self.chessboard.wait_for_next_move = True
                            self.chessboard.last_time = pygame.time.get_ticks()
            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if not self.chessboard.game_ended:
                        pressed_c = int(e.pos[0]//SQUARE_SIZE)
                        pressed_r = int(e.pos[1]//SQUARE_SIZE)-1
                        if pressed_c >= 0 and pressed_c <= 7 and pressed_r >= 0 and pressed_r <= 7:
                            if not Helpers.is_empty(self.chessboard.boardpieces[pressed_r][pressed_c]) and (((self.chessboard.playtype == 2 and self.chessboard.white_top and self.chessboard.currently_playing == BLACK_COLOR_IDENTIFIER and self.chessboard.boardpieces[pressed_r][pressed_c].color == self.chessboard.currently_playing) or (self.chessboard.playtype == 2 and not self.chessboard.white_top and self.chessboard.currently_playing == WHITE_COLOR_IDENTIFIER and self.chessboard.boardpieces[pressed_r][pressed_c].color == self.chessboard.currently_playing)) or (self.chessboard.playtype == 1 and self.chessboard.boardpieces[pressed_r][pressed_c].color == self.chessboard.currently_playing)):
                                self.lastMousePos = (e.pos[0], e.pos[1])
                                self.dragged_piece = self.chessboard.boardpieces[pressed_r][pressed_c]
                                self.dragged_piece_initial_pos = (
                                    pressed_r, pressed_c)
                                self.startdragging = True
                                self.ispicked = True
                elif e.type == pygame.MOUSEMOTION:
                    if self.startdragging == True and self.isdragging == False:
                        self.isdragging = True
                    if self.isdragging:
                        self.lastMousePos = (e.pos[0], e.pos[1])
                elif e.type == pygame.MOUSEBUTTONUP:
                    self.startdragging = False
                    if self.isdragging or self.ispicked:
                        pressed_c = int(e.pos[0]//SQUARE_SIZE)
                        pressed_r = int(e.pos[1]//SQUARE_SIZE)-1
                        if (pressed_r, pressed_c) in self.chessboard.boardpieces[self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]].possible_moves:
                            will_capture = self.chessboard.make_move(
                                pressed_r, pressed_c, self.dragged_piece_initial_pos[0], self.dragged_piece_initial_pos[1])

                            if will_capture:
                                pygame.mixer.Sound.play(pygame.mixer.Sound(
                                    os.path.join('sounds/capture.wav')))
                            else:
                                pygame.mixer.Sound.play(pygame.mixer.Sound(
                                    os.path.join('sounds/move.wav')))
                        if self.dragged_piece_initial_pos != (pressed_r, pressed_c) and self.ispicked == True:
                            self.dragged_piece = None
                            self.ispicked = False
                    self.isdragging = False

                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        if self.chessboard.show_end_screen == False:
                            self.chessboard.__init__(self.chessboard.playtype,
                                                     self.chessboard.white_top, self.chessboard.ai)
                        if self.chessboard.show_end_screen == True:
                            self.chessboard.show_end_screen = False
                elif e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(1)

            pygame.display.update()


parser = argparse.ArgumentParser(description='Get chess parameters.')
parser.add_argument(
    'mode',  help='Insert the mode of the game. 1: Player vs Player; 2: Player vs Computer; 3: Computer vs Computer;')
parser.add_argument('--ai',
                    help='Insert the type of the AI behind the computer moves. 1: Random Moves; 2: Stockfish', required=False)
args = parser.parse_args()
print(args)
if (int(args.mode) == 1 or int(args.mode) == 2 or int(args.mode) == 3):
    computer_type = 1 if int(args.ai) == 1 or args.ai == None else 2
    white_top = False if int(args.mode) == 1 or args.mode == 3 else random.choice([
        True, False])
    maingame = MainGame(int(args.mode), white_top, computer_type)
    maingame.maingameloop()
