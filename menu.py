import pygame
import math
from utils import *

class Interactable :
    def __init__(self, hitbox, func) :
        self.hitbox = hitbox
        self.func = func

    def collides(self, point) :
        return self.hitbox.collidepoint(point)
    
    def execute(self) :
        func, *args = self.func
        print(func)
        print(*args)
        func(*args)


class Menu :
    def __init__(self, game, corner = (25, 25)) :
        pygame.init()
        # print(pygame.font.get_fonts())
        self.game = game
        self.screen = self.game.screen
        self.corner = corner
        self.page = pygame.Surface((self.screen.get_rect().bottomright[0] - 4 * self.corner[0], self.screen.get_rect().bottomright[1] - 4 * self.corner[1]))
        self.border = pygame.Surface((self.screen.get_rect().bottomright[0] - 2 * self.corner[0], self.screen.get_rect().bottomright[1] - 2 * self.corner[1]))
        self.tenth = (math.floor(self.page.get_width() / 10), math.floor(self.page.get_height() / 10))
        self.twentieth = (math.floor(self.page.get_width() / 20), math.floor(self.page.get_height() / 20))
        self.half = (math.floor(self.page.get_width() / 2), math.floor(self.page.get_height() / 2))
        self.font_unit = math.floor(self.page.get_width() / 80)
        self.font = pygame.font.SysFont("monospace", self.font_unit * 2)
        self.game.font = self.font
        self.title_font = pygame.font.SysFont("impact", self.font_unit * 5)
        self.img_corner = (self.corner[0] * 2, self.corner[1] * 2)
        self.interactions = []

    def clear(self) :
        self.game.clear()

    def draw_to_screen(self, sliders = []) :
        self.screen.blit(self.border, self.corner)
        self.screen.blit(self.page, self.img_corner)

    def draw_slider(self, values, target, x_offset = 0, y_offset = 0, func = set_sfx_volume, slider_underline = None, slider_main = (70, 55, 48), slider_secondary = (242, 133, 0), slider_image = 'maxwell') :
        if slider_underline is None :
            slider_underline = self.game.black
        slider = pygame.Surface((math.floor(self.page.get_width() * 3 / 4), self.tenth[1]))
        slider.fill(self.game.transparent)
        rect = slider.get_rect()
        img = pygame.transform.scale(self.game.assets['images']['menu'][slider_image], self.tenth)
        star = pygame.transform.scale(self.game.assets['images']['menu'][slider_image], self.tenth) # set to twentieth to remove overlap
        y_buffer = surf_center(self.page, slider)[1] / 10
        slider_offsets = (surf_center(self.page, slider)[0] + x_offset, surf_center(self.page, slider)[1] - y_buffer * 3 + y_offset)
        
        for i in range(len(values)) :
            coords = pygame.Rect((rect.width - img.get_width()) * i / (len(values)) + img.get_width() / 2, rect.centery - star.get_height() / 2, img.get_width(), img.get_height())
            if values[i] != target :
                star.set_alpha(64)
                slider.blit(star, coords)
            else  : 
                star.set_alpha(255)
                slider.blit(star, coords)
            hitbox = pygame.Rect(coords[0] + slider_offsets[0] + self.img_corner[0], coords[1] + slider_offsets[1] + self.img_corner[1], star.get_width(), star.get_height())
            self.interactions.append(Interactable(hitbox, (func, self.game, values[i])))
        slider.set_colorkey(self.game.transparent)
        self.page.blit(slider, slider_offsets)
    
    def draw_border(self, color = None) :
        if color is None :
            color = self.game.white
        self.border.fill((abs(color[0] - 128), abs(color[1] - 128), abs(color[2] - 128)))
        self.border.fill(self.game.transparent, (self.corner[0], self.corner[1], self.border.get_width() - self.corner[0] * 2, self.border.get_height() - self.corner[1] * 2))
        self.border.set_colorkey(self.game.transparent)

    def draw_text(self, text, color, font = None, centered = False, centered_x = False, centered_y = False, coords = (0, 0), shadow = False) :
        if not font :
            font = self.font
        textobj = font.render(text, 1, color) 
        textrect = textobj.get_rect()
        coords = list(coords)

        if centered or centered_x :
            coords[0] = coords[0] + (self.half[0] - textrect.width / 2)
        if centered or centered_y :
            coords[1] = coords[1] + (self.half[1] - textrect.height / 2)
            
        textrect.topleft = tuple(coords)
        if shadow :
            shift = math.floor(font.get_linesize() / 10)
            shadowobj = font.render(text, 1, (abs(color[0] - 128), abs(color[1] - 128), abs(color[2] - 128)))
            self.page.blit(shadowobj, (textrect.topleft[0] - shift, textrect.topleft[1] - shift, textrect.width - shift, textrect.height - shift))
        
        self.page.blit(textobj, textrect) 

    def update(self) :
        self.interactions = []

class Main(Menu) :
    def __init__(self, game) :
        super().__init__(game)

    def draw_box(self, color = None, border = True, transparency = 256, img = None) :
        if img is None :
            img = self.game.assets['images']['menu']['eva_chess']
        background = pygame.transform.scale(img, (self.page.get_width(), self.page.get_height()))
        self.page.set_alpha(transparency)
        self.page.blit(background, (0, 0))

    
    def update(self) :
        self.interactions = []

    def draw(self) :
        self.update()
        self.draw_border()
        self.draw_box()
        self.draw_text('main menu', self.game.white, font = self.title_font, centered_x = True, coords = (0, self.twentieth[1]), shadow = True)
        # self.draw_to_screen()
        self.draw_slider([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], self.game.sfx_volume)
        self.draw_slider([2, 4, 6, 8, 10, 12, 14, 16], self.game.brightness, func = set_brightness, y_offset = self.tenth[1])
        if self.game.lclick :
            # print(self.interactions)
            for interactable in self.interactions :
                if interactable.collides(self.game.mpos) :
                    interactable.execute()
        self.game.screen.blit(self.border, self.corner)
        self.game.screen.blit(self.page, self.img_corner)
        
        

class Promotion(Menu) :
    def __init__(self, game) :
        super().__init__(game)

    def draw(self) :
        self.draw_text('promotion menu', self.game.white, coords = (20, 20))


class Error(Menu) :
    def __init__(self, game) :
        super().__init__(game)

    def draw(self) :
        self.draw_text('fatal error. my bad', self.game.white, coords = (20, 20))