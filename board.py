import pygame
import math
import random
import json
import copy

from piece import *
from utils import play_sound
from effect import *

MAP = '0'
SAVE_LOCATION = './state.json'

f = open('./data/layout.json')
LAYOUT = json.load(f)
f.close()

class Board :
    def __init__(self, game, board_size, dimension = [8, 8], disable_shift_constant = False) :
        self.board_size = board_size
        self.dimension = dimension
        self.board = pygame.Surface(board_size)
        self.game = game
        self.pieces = []
        self.white_pieces = []
        self.black_pieces = []
        self.locations = []
        self.white_piece_locations = []
        self.white_sight = set()
        self.black_piece_locations = []
        self.black_sight = set()
        self.state = []
        self.selected = (-1, -1)
        self.prev = tuple(self.selected)
        self.disable_shift_constant = disable_shift_constant
        self.message = False

        self.round = 0
        
        self.tile_width = board_size[0] / dimension[0]
        self.tile_height = board_size[1] / dimension[1]
        self.min_highlight_radius = min(self.tile_width, self.tile_height) / 5
        self.max_highlight_radius = min(self.tile_width, self.tile_height) / 2
        self.radius_direction = 1
        self.radius = self.min_highlight_radius
        self.shift_const = [self.tile_width / 4, self.tile_height / 4] if not self.disable_shift_constant else [0, 0]

    def copy(self) :
        c = copy.copy(self)
        c.locations = copy.copy(c.locations)        
        c.pieces = copy.copy(c.pieces)

        for piece in c.pieces :
            piece = piece.copy()

        c.update()

        return c

    def save_state(self, save = SAVE_LOCATION) :
        f = open(save, 'w')
        state = {}
        for piece in self.pieces :
            state[str(piece.pos)] = piece.to_json()
        json.dump(state, f)
        f.close()

    def load_state(self, save = SAVE_LOCATION) :
        self.pieces = []
        self.update()
        f = open(save)
        state = json.load(f)
        for coord in state :
            self.pieces.append(Piece.from_json(state[coord], self.game))
        f.close()
        self.update()

    def read(self) :
        for piece in self.pieces :
            print(f'[{piece.p_type}]\tat {piece.pos}')

    def draw_board(self) :
        self.board.fill((255, 255, 255))
        for x in range(self.dimension[0]) :
            for y in range(self.dimension[1]) :
                rect = pygame.Rect(x * self.tile_width, y * self.tile_height, (x + 1) * self.tile_width, (y + 1) * self.tile_height)
                if (x + y) & 1 :
                    self.board.fill(self.game.black, rect)
                    if self.game.coords :
                        text = self.game.font.render(f'{chr(x + 65)}{y + 1}', True, self.game.white)
                        textRect = text.get_rect()
                        textRect.topleft = (rect[0], rect[1])
                        self.board.blit(text, textRect)
                else :
                    self.board.fill(self.game.white, rect)
                    if self.game.coords :
                        text = self.game.font.render(f'{chr(x + 65)}{y + 1}', True, self.game.black)
                        textRect = text.get_rect()
                        textRect.topleft = (rect[0], rect[1])
                        self.board.blit(text, textRect)
        self.draw_pieces()

    def layout(self) :
        l = MAP # TODO : delete
        l = str(self.game.round)
        for pos in LAYOUT[l].keys() :
            target = LAYOUT[l][pos]
            self.pieces.append(makePiece(self.game, p_type = target[0], team = target[1], pos = eval(pos)))
        self.draw_pieces()
    
    def draw_pieces(self) :
        for piece in sorted(self.pieces, key = lambda x : x.pos[1]) :
            piece.render()
        
    def team_locations(self, team) :
        return self.white_piece_locations if team == 'white' else self.black_piece_locations
    
    def team_peices(self, team) :
        return list(filter(lambda piece : piece.team == team, self.pieces))

    def get_piece(self, loc) :
        return next((piece for piece in self.pieces if piece.pos == loc), None)
    
    def get_pieces(self, loc) :
        return [piece for piece in self.pieces if piece.pos == loc]

    def show_moves(self, loc, color = None, invert_shown = False) :
        if not color :
            color = self.game.highlight

        if loc in self.locations :
            curr = self.get_piece(loc)
            if not curr :
                return

            if not invert_shown :    
                for move in curr.moves() :
                    self.board.fill(color, (move[0] * self.tile_width + self.shift_const[0], move[1] * self.tile_height + self.shift_const[1], self.tile_width - 2 * self.shift_const[0], self.tile_height - 2 * self.shift_const[1]))
            else :    
                for move in curr.moves() :
                    self.board.fill(color, (move[0] * self.tile_width, move[1] * self.tile_height, self.tile_width, self.tile_height))
                    self.board.fill(self.game.transparent, (move[0] * self.tile_width + self.shift_const[0], move[1] * self.tile_height + self.shift_const[1], self.tile_width - 2 * self.shift_const[0], self.tile_height - 2 * self.shift_const[1]))
                self.board.set_colorkey(self.game.transparent)
            

            self.radius += math.cos(self.radius % 1) * self.radius_direction
            if self.radius < self.min_highlight_radius or self.radius > self.max_highlight_radius:
                self.radius_direction *= -1
            if self.get_piece(self.game.mtile) :
                pygame.draw.circle(self.board, self.game.highlight, ((self.game.mtile[0] + .5) * self.tile_width, (self.game.mtile[1] + .5) * self.tile_height), self.radius)

    def render(self) :
        self.draw_board()

        if self.selected in self.team_locations(self.game.turn) :

            self.show_moves(self.selected, color = self.game.inverted_highlight, invert_shown = True)

            if self.game.mtile in self.get_piece(self.selected).moves() :
                self.board.fill(self.game.move_color, (self.game.mtile[0] * self.tile_width + self.shift_const[0], self.game.mtile[1] * self.tile_height + self.shift_const[1], self.tile_width - self.shift_const[0] * 2, self.tile_height - self.shift_const[1] * 2))

        if self.game.mtile[0] >= 0 :
            self.show_moves(self.game.mtile)
        
        if self.game.show_white_sightlines :
            self.show_sightlines('white')
        if self.game.show_black_sightlines :
            self.show_sightlines('black')

        self.draw_pieces()
        return self.board
    
    def update_sight(self) :
        self.white_sight = set()
        self.black_sight = set()
        for piece in self.pieces :
            moves = piece.moves()
            if piece.p_type == 'pawn' :
                moves = list(filter(lambda pawn_move : pawn_move[0] != piece.pos[0], moves))
            if piece.team == 'white' :
                for move in moves :
                    self.white_sight.add(move)
            else :
                for move in moves :
                    self.black_sight.add(move)

    def fill_square(self, tile_coords, color = (64, 64, 64)) :
        self.board.fill(color, (tile_coords[0] * self.tile_width, tile_coords[1] * self.tile_height, self.tile_width, self.tile_height))

    def show_sightlines(self, team, color = (64, 64, 64, 0.1)) :
        team = self.white_sight if team == 'white' else self.black_sight
        for coords in team :
            self.fill_square(coords, color)

    def update(self) :

        self.white_pieces = self.team_peices('white')
        self.black_pieces = self.team_peices('black')
        self.white_piece_locations = [piece.pos for piece in filter(lambda piece : piece.team == 'white', self.pieces)]
        self.black_piece_locations = [piece.pos for piece in filter(lambda piece : piece.team == 'black', self.pieces)]
        self.locations = [piece.pos for piece in self.pieces]

        if self.game.lclick :
            self.prev = tuple(self.selected)
            self.selected = self.game.mtile
        
        self.update_sight()
    
    def king_pos(self, team) :
        k = list(filter(lambda piece : piece.p_type == 'king', self.team_peices(team)))
        if len(k) > 0 :
            return k[0].pos
        else :
            print('no king? huh?')
            return (-1, -1)

    def is_checkmate(self, team = None) :
        if self.message : 
            return 'neither'
        self.message = True
        if len(self.pieces) == 2 :
            return 'stalemate'
        if not team :
            team = self.game.turn
        king_pos = self.king_pos(team)
        enemy_sight = (self.black_sight if team == 'white' else self.white_sight)
        if king_pos not in enemy_sight : 
            for piece in self.white_pieces if team == 'white' else self.black_pieces :
                if len(piece.moves()) > 0 :
                    return 'neither'
        status = 'checkmate'
        self.save_state('./data/checkstate.json')
        for piece in self.team_peices(team) :
            for move in piece.moves() :
                self.load_state('./data/checkstate.json')
                self.move(piece.pos, move)
                if not self.king_pos(team) in (self.black_sight if team == 'white' else self.white_sight) :
                    status = 'check'
                    print(f'lmao simply [{piece.pos}] ==> [{move}] you dolt')
                    break
            if status == 'check' :
                break            
        
        self.load_state('./data/checkstate.json')
        self.game.switch_turn()
        return status

    def turn(self) :
        if self.prev in self.team_locations(self.game.turn) :
            self.move(self.prev, self.selected)
            self.message = False
        elif (-1, -1) not in [self.selected, self.prev] :
            print(f'[{self.selected, self.prev}] IT IS FORBIDDEN')
            pass

    def move(self, start_coord, end_coord) :
        old = tuple(start_coord)
        curr = self.get_piece(start_coord)
        self.save_state()        

        if not curr :
            self.prev = (-1, -1)
            self.selected = (-1, -1)
            return False
        
        elif end_coord in curr.moves() :
            # if castling
            if curr.p_type == 'king' and abs(end_coord[0] - curr.pos[0]) > 1 and not self.message :
                    play_sound(self.game, self.game.assets['sound']['sfx']['rizz'])
                    corner_piece = self.get_piece(end_coord)
                    x_shift = -1 if end_coord[0] == 0 else 1
                    end_coord = (curr.pos[0] + (2 * x_shift), curr.pos[1])
                    corner_piece.pos = (end_coord[0] - x_shift, corner_piece.pos[1])
            # if attacking
            elif end_coord in self.team_locations(curr.enemy) :
                target_color = self.game.white if curr.enemy == 'white' else self.game.black
                if not self.message :
                    play_sound(self.game, self.game.assets['sound']['sfx']['spongebob'] if (self.get_piece(end_coord).p_type == 'queen') else self.game.assets['sound']['sfx']['punch'] )
                self.pieces.remove(self.get_piece(end_coord))                 
                self.game.effects.append(Radius(self.game, (self.tile_width * (end_coord[0] + .5) + self.game.board_offset[0], self.tile_height * (end_coord[1] + .5) + self.game.board_offset[1]), target_color, 2, self.tile_width / 2, self.tile_width, thickness = self.tile_width / 8, board = False))

            # if en passanting
            elif curr.p_type == 'pawn' and old[0] != end_coord[0] and (end_coord[0], end_coord[1] - curr.forward) in self.team_locations(curr.enemy) :
                if not self.message :
                    play_sound(self.game, self.game.assets['sound']['sfx']['bowling'])
                
                self.pieces.remove(self.get_piece((end_coord[0], end_coord[1] - curr.forward)))
            curr.pos = end_coord
            self.update()

            # reset if position ends with endangering king
            enemy_sight = self.white_sight if curr.enemy == 'white' else self.black_sight
            if self.king_pos(curr.team) in (enemy_sight) :
                if not self.message :
                    print(f'nuh uh [{old}] ==> [{curr.pos}] would b game ovah')
                self.load_state()
                if not self.message :
                    play_sound(self.game.assets['sound']['sfx']['buzzer'])
                self.prev = (-1, -1)
                self.selected = (-1, -1)
                return False
                
            # en passant and pawn promotion
            for piece in self.pieces :
                piece.en_passantable = False        
            if curr.p_type == 'pawn' :
                if (curr.pos[1] == self.dimension[0] - 1 or curr.pos[1] == 0) :
                    curr.promote()
                    if not self.message :
                        play_sound(self.game, self.game.assets['sound']['sfx']['winrate'], volume = .2)
                elif abs(old[1] - curr.pos[1]) == 2 :
                    if not self.message and random.random() > 0.95 :
                        play_sound(self.game, self.game.assets['sound']['sfx'][f'boing_{random.randint(1, 3)}'], volume = .2)
                    curr.en_passantable = True
            
            curr.moved = True
            self.game.switch_turn()
            self.prev = (-1, -1)
            self.selected = (-1, -1)
            self.save_state()
            return True
        return False