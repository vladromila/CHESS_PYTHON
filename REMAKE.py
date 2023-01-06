import pygame
import sys
import os
from constants import *
from pprint import pprint
import io
from stockfish import Stockfish
import time
import copy
from chessboard import ChessBoard, Helpers

"""
Class that saves the data that matters for every piece
"""


class MainGame:

    def __init__(self, type, white_top=False):

        self.chessboard = ChessBoard(type, white_top)
        pygame.init()
        pygame.display.set_caption("Chess by Vlad Romila@3A1")
        self.display = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.isdragging = False
        self.dragged_piece = None
        self.dragged_piece_initial_pos = (0, 0)
        self.lastMousePos = (0, 0)

    def get_texture(self, identifier, hovered):
        if hovered == True:
            return os.path.join(
                f'images/imgs-128px/{identifier}.png')
        else:
            return os.path.join(
                f'images/imgs-80px/{identifier}.png')

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
                        str(r+1 if self.chessboard.white_top else NUMBER_OF_ROWS-r), 1, color)
                    lbl_pos = (5, 5 + r * SQUARE_SIZE)
                    self.display.blit(lbl, lbl_pos)

                if c == 7:
                    color = WHITE_SQUARE_COLOR if r % 2 == 0 else BLACK_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        str(r+1 if self.chessboard.white_top else NUMBER_OF_ROWS-r), 1, color)
                    lbl_pos = ((c+1) * SQUARE_SIZE - 15, 5 + r * SQUARE_SIZE)
                    self.display.blit(lbl, lbl_pos)

                if r == 7:
                    color = BLACK_SQUARE_COLOR if (
                        r + c) % 2 == 0 else WHITE_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        ALPHACOLS[NUMBER_OF_COLUMNS - c-1] if self.chessboard.white_top else ALPHACOLS[c], 1, color)
                    lbl_pos = (c * SQUARE_SIZE + SQUARE_SIZE /
                               2 - 5, SCREEN_HEIGHT - 120)
                    # blit
                    self.display.blit(lbl, lbl_pos)

                if r == 0:
                    color = BLACK_SQUARE_COLOR if (
                        r + c) % 2 == 0 else WHITE_SQUARE_COLOR
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(
                        ALPHACOLS[NUMBER_OF_COLUMNS - c-1] if self.chessboard.white_top else ALPHACOLS[c], 1, color)
                    lbl_pos = (c * SQUARE_SIZE + SQUARE_SIZE/2 - 5, 0)
                    # blit
                    self.display.blit(lbl, lbl_pos)

    def display_possible_moves(self):
        possible_moves = self.chessboard.boardpieces[self.dragged_piece_initial_pos[0]
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
                if not Helpers.is_empty(self.chessboard.boardpieces[r][c]):
                    piece = self.chessboard.boardpieces[r][c]
                    texture = self.get_texture(piece.identifier, False)
                    img = pygame.image.load(texture)
                    img_center = c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2
                    texture_rect = img.get_rect(center=img_center)
                    self.display.blit(img, texture_rect)

    def display_dragged_piece(self):
        texture = self.get_texture(self.dragged_piece.identifier, True)
        to_show_image = pygame.image.load(texture)
        # rect
        img_center = (self.lastMousePos[0], self.lastMousePos[1])
        texture_rect = to_show_image.get_rect(
            center=img_center)
        # blit
        self.display.blit(to_show_image, texture_rect)

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
                    pressed_c = int(e.pos[0]//SQUARE_SIZE)
                    pressed_r = int(e.pos[1]//SQUARE_SIZE)
                    if not Helpers.is_empty(self.chessboard.boardpieces[pressed_r][pressed_c]) and (((self.chessboard.playtype == 2 and self.chessboard.white_top and self.chessboard.currently_playing == BLACK_COLOR_IDENTIFIER) or (self.chessboard.playtype == 2 and not self.chessboard.white_top and self.chessboard.currently_playing == WHITE_COLOR_IDENTIFIER)) or (self.chessboard.playtype == 1 and self.chessboard.boardpieces[pressed_r][pressed_c].color == self.chessboard.currently_playing)):
                        self.lastMousePos = (e.pos[0], e.pos[1])
                        self.dragged_piece = self.chessboard.boardpieces[pressed_r][pressed_c]
                        self.dragged_piece_initial_pos = (pressed_r, pressed_c)
                        self.isdragging = True
                elif e.type == pygame.MOUSEMOTION:
                    if self.isdragging:
                        self.lastMousePos = (e.pos[0], e.pos[1])
                elif e.type == pygame.MOUSEBUTTONUP:
                    if self.isdragging:
                        pressed_c = int(e.pos[0]//SQUARE_SIZE)
                        pressed_r = int(e.pos[1]//SQUARE_SIZE)
                        if (pressed_r, pressed_c) in self.chessboard.boardpieces[self.dragged_piece_initial_pos[0]][self.dragged_piece_initial_pos[1]].possible_moves:
                            will_capture = self.chessboard.make_move(
                                pressed_r, pressed_c, self.dragged_piece_initial_pos[0], self.dragged_piece_initial_pos[1])
                            self.chessboard.check_queen_promotion(
                                pressed_r, pressed_c, WHITE_COLOR_IDENTIFIER)
                            self.chessboard.check_queen_promotion(
                                pressed_r, pressed_c, BLACK_COLOR_IDENTIFIER)

                            if will_capture:
                                pygame.mixer.Sound.play(pygame.mixer.Sound(
                                    os.path.join('sounds/capture.wav')))
                            else:
                                pygame.mixer.Sound.play(pygame.mixer.Sound(
                                    os.path.join('sounds/move.wav')))

                            # if self.chessboard.playtype == 2:
                            #     self.wait_for_next_move = True
                            #     self.last_time = pygame.time.get_ticks()
                            # self.calculate_next_move()

                        self.isdragging = False
                        self.dragged_piece = None
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        self.__init__(self.chessboard.playtype,
                                      self.chessboard.white_top)
                elif e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(1)

            pygame.display.update()


maingame = MainGame(1, True)
maingame.maingameloop()
