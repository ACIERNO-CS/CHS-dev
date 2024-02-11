import pygame
import copy

class Effect :
    def __init__(self, game, center, color, duration) :
        self.game = game
        self.center = center
        self.color = color
        self.duration = duration

class Radius(Effect) :
    def __init__(self, game, center, color, duration, starting_radius, ending_radius, thickness = 0, board = True) :
        super().__init__(game, center, color, duration)
        self.starting_radius = starting_radius
        self.ending_radius = ending_radius
        self.surf = pygame.Surface((ending_radius * 2, ending_radius * 2))
        self.rect = self.surf.get_rect()
        self.thickness = thickness
        self.board = board
        self.framerate = self.game.framerate
        self.inc = ((self.ending_radius - self.starting_radius) / 2) / (self.framerate * self.duration)
        self.radius = copy.copy(self.starting_radius)

    def draw(self, surf) :
        offsets = (0, 0) if not self.board else (self.game.board.shift_const)
        self.surf.fill(self.game.transparent)
        self.surf.set_colorkey(self.game.transparent)
        pygame.draw.circle(self.surf, self.color, (self.rect.centerx, self.rect.centery), self.radius, width = int(self.thickness))
        self.radius += self.inc
        surf.blit(self.surf, (self.center[0] - self.rect.centerx, self.center[1] - self.rect.centery))
        print(self.radius, self.ending_radius)
        if self.thickness != 0 :
            self.thickness = max(0, self.thickness - (self.thickness / (self.framerate * self.duration)))
        return self.radius <= self.ending_radius
