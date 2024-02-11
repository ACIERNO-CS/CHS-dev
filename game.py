import os
import sys
import math
import pygame
from time import sleep

from board import Board
from utils import *
from menu import Main, Promotion, Error
#lets get it

BOARD_SIZE = (960, 960)
SCREEN_SIZE = (1280, 1000)

BLACK = (13, 1, 41)
WHITE = (250, 125, 135) # (255, 225, 156)


class Game :
    def __init__(self, board_size = BOARD_SIZE, screen_size = SCREEN_SIZE, round = 0, black = (0, 0, 0), white = (255, 255, 255), highlight = (125, 0, 6), turn = 'white', sfx_volume = 10, brightness = 16, framerate = 30) :
        pygame.init()
        self.clock = pygame.time.Clock()
        self.state = 'game'
        self.font = None

        self.board = Board(self, board_size, dimension = [5, 6])
        self.screen_size = screen_size
        self.sfx_volume = sfx_volume
        self.brightness = brightness
        self.framerate = framerate
        self.round = round
        self.dimension = 8
        self.black = black
        self.white = white
        self.turn = turn
        self.lclicking = [False, False]
        self.lclick = False
        self.coords = False
        self.show_white_sightlines = False
        self.show_black_sightlines = False
        self.highlight = highlight
        self.inverted_highlight = tuple(map(lambda x : 255 - x, highlight))
        self.transparent = (0, 177, 64) # TODO : Fix jank code
        self.move_color = (255, 0, 255)
        self.mpos = (0, 0)
        self.mtile = (-1, -1)

        self.effects = []

        self.highlighting = True # False

        self.assets = pull_assets()
        
        self.screen = pygame.display.set_mode(screen_size)
        #self.screen
        self.board_offset = [(self.screen.get_width() - self.board.board.get_width()) / 2, (self.screen.get_height() - self.board.board.get_height()) / 2]
        
    def mouse_update(self) :
        self.mpos = pygame.mouse.get_pos()
        if (self.board_offset[0] <= self.mpos[0] <= self.board_offset[0] + self.board.board_size[0]) and (self.board_offset[1] <= self.mpos[1] <= self.board_offset[1] + self.board.board_size[1]) :
            self.mtile = (int((self.mpos[0] - self.board_offset[0]) // (self.board.tile_width)), int((self.mpos[1] - self.board_offset[1]) // (self.board.tile_height)))
        else :
            self.mtile = (-1, -1)

    def switch_turn(self) :
        self.turn = 'white' if self.turn == 'black' else 'black'

    def clear(self) :
        self.screen.blit(pygame.transform.scale(self.assets['real_background'], self.screen_size), (0, 0))

    def run(self) :
        self.board.layout()
        self.board.update_sight()
        main_menu = Main(self)
        promotion_menu = Promotion(self)
        error_menu = Error(self)

        while True :
            self.mouse_update()

            self.clear()
            #self.screen.fill((0, 0, 0), (self.screen_size[0], self.screen_size[1], 0, 0))
            # keyboard / mouse input
            for event in pygame.event.get() : # for button press in button presses / mouse moves / ect
                match event.type :
                    case pygame.QUIT : # need to define x event
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN :
                        match event.key :
                            case pygame.K_w :
                                self.show_white_sightlines = True
                            case pygame.K_b :
                                self.show_black_sightlines = True
                            case pygame.K_h :
                                self.highlighting = not self.highlighting
                            case pygame.K_g :
                                self.coords = True
                            case pygame.K_ESCAPE :
                                self.state = 'main_menu' if self.state != 'main_menu' else 'game'
                            case _ :
                                print('waow')
                    case pygame.KEYUP :
                        match event.key :
                            case pygame.K_w :
                                self.show_white_sightlines = False
                            case pygame.K_b :
                                self.show_black_sightlines = False
                            case pygame.K_g :
                                self.coords = False
                    case pygame.MOUSEBUTTONDOWN :
                        match event.button :
                            case 1 :
                                self.lclicking[1] = True

                                # TODO : fix jank
                                if self.lclicking[1] and not self.lclicking[0] :
                                    self.lclick = True
                                else :
                                    self.lclick = False
                            case 2 :
                                print('white\n', self.board.team_locations('white'))
                                print('black\n', self.board.team_locations('black'))
                            case 3 :
                                self.board.read()
                            case _ :
                                print(':3')
                    case pygame.MOUSEBUTTONUP :
                        match event.button :
                            case 1 :
                                self.lclicking[1] = False
                            case _ :
                                print(':3')
                    case _ :
                        pass

            if self.lclicking[1] and not self.lclicking[0] :
                self.lclick = True
            else :
                self.lclick = False
            
            self.lclicking = [self.lclicking[1], False]

            match self.state :
                case 'game' :
                    self.board.update()
                    c = self.board.is_checkmate()
                    print(c)
                    match  c :
                        case 'check' :
                            play_sound(self, self.assets['sound']['sfx']['vine_boom'])
                        case 'checkmate' :
                            play_sound(self, self.assets['sound']['sfx']['goofy_ahh'])

                            sleep(5)
                            self.state = 'checkmate'
                        case 'stalemate' :
                            play_sound(self, self.assets['sound']['sfx']['winrate'])
                            pass
                        case 'neither' :
                            pass
                        case _ :
                            print('>:3')
                    if self.lclick :
                        self.board.turn()
                    self.board.render()
                    self.screen.blit(self.board.board, self.board_offset)
                    #effect handler
                    for effect in self.effects :
                        if not effect.draw(self.screen) :
                            self.effects.remove(effect)
                case 'main_menu' :
                    self.board.render()
                    self.screen.blit(self.board.board, self.board_offset)
                    main_menu.draw()
                case 'promoting' :
                    promotion_menu.draw()
                case 'checkmate' :
                    print('rip bozo')
                    self.round += 1

                    match self.round :
                        case 1 :
                            self.board = Board(self, BOARD_SIZE, dimension=[5, 6])

                    self.board.layout()
                    self.board.update_sight()
                    self.state = 'game'
                case _ :
                    error_menu.draw()
                    

            # place board in center of screen
            brightness = pygame.Surface(self.screen_size)
            brightness.fill((0, 0, 0))
            brightness.set_alpha(255 / self.brightness)
            self.screen.blit(brightness, (0, 0))
            pygame.display.update()

            self.clock.tick(self.framerate)
            
Game(black=BLACK, white=WHITE).run()
