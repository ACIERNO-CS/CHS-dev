import pygame
import copy

KNIGHT_MOVES = [(-2, 1), (-2, -1), (2, 1), (2, -1), (-1, 2), (-1, -2), (1, 2), (1, -2)]
PAWN_MOVES = [(1, 0)]
KING_MOVES = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


class Piece :
    def __init__(self, game, team, pos, p_type, upgrades = [], moved = False) :
        self.game = game
        self.team = team
        self.enemy = 'white' if team == 'black' else 'black'
        self.forward = 1 if self.team == 'black' else -1
        self.p_type = p_type
        self.pos = pos
        self.upgrades = upgrades
        self.board = self.game.board
        self.moved = moved
        self.en_passantable = False
        self.img = pygame.transform.scale(self.game.assets['images'][self.team][self.p_type], (2 * self.board.tile_width // 3, 2 * self.board.tile_height // 3))
    
    def render(self) :
        self.board.board.blit(self.img, (self.pos[0] * self.board.tile_width + ((self.board.tile_width - self.img.get_width()) / 2), self.pos[1] * self.board.tile_height + ((self.board.tile_height - self.img.get_height()) / 2)))

    def copy(self) :
        return copy.copy(self) # makePiece(self.game, str(self.team), tuple(self.pos), str(self.p_type), upgrades = list(self.upgrades), moved = bool(self.moved))

    def to_json (self) :
        obj = { 
            'team' : self.team,
            'p_type' : self.p_type,
            'pos' : self.pos,
            'upgrades' : str(self.upgrades),
            'moved' : self.moved,
            'en_passantable' : self.en_passantable
        }
        return obj
    
    def from_json (obj, game) :
                                                                                            # TODO : fix jank code
        piece = makePiece(game, team = obj['team'], pos = tuple(obj['pos']), p_type = obj['p_type'], upgrades = eval(obj['upgrades']), moved = bool(obj['moved']))
        piece.enemy = 'white' if piece.team == 'black' else 'black'
        piece.forward = 1 if piece.team == 'black' else -1
        piece.en_passantable = obj['en_passantable']
        return piece

# pieces extending
class Pawn(Piece) :
    def __init__(self, game, team, pos, p_type = 'pawn', upgrades = [], moved = False) :
        super().__init__(game, team, pos, p_type, upgrades, moved)

    def moves(self) :
        moves = [(self.pos[0], self.pos[1] + self.forward)]

        if not self.moved :
            moves.append((self.pos[0], self.pos[1] + self.forward * 2))
        
        moves = list(filter(lambda move : move not in self.game.board.locations and -1 < move[0] < self.game.board.dimension[0] and -1 < move[1] < self.game.board.dimension[0], moves))

        attacking_squares = [(self.pos[0] - 1, self.pos[1] + self.forward), (self.pos[0] + 1, self.pos[1] + self.forward)]

        for square in attacking_squares :
            if square in self.game.board.team_locations(self.enemy) or (square[0], square[1] - self.forward) in self.game.board.team_locations(self.enemy) and self.game.board.get_piece((square[0], square[1] - self.forward)).en_passantable:
                moves.append(square)

        return moves
    
    def promote(self, change_to = 'queen') :
        self.board.pieces.remove(self)
        self.board.pieces.append(makePiece(self.game, team = self.team, pos = self.pos, p_type = change_to, moved = True))

class Knight(Piece) :
    def __init__(self, game, team, pos, p_type = 'knight', upgrades = [], moved = False) :
        super().__init__(game, team, pos, p_type, upgrades = upgrades, moved = moved)
    
    def moves(self) :
        moves = [(self.pos[0] + 1, self.pos[1] + 2), (self.pos[0] + 1, self.pos[1] - 2), (self.pos[0] - 1, self.pos[1] + 2), (self.pos[0] - 1, self.pos[1] - 2), (self.pos[0] + 2, self.pos[1] + 1), (self.pos[0] + 2, self.pos[1] - 1), (self.pos[0] - 2, self.pos[1] + 1), (self.pos[0] - 2, self.pos[1] - 1)]
        
        moves = list(filter(lambda move : move not in self.game.board.team_locations(self.team) and -1 < move[0] < self.game.board.dimension[0] and -1 < move[1] < self.game.board.dimension[0], moves))         

        return moves

class Rook(Piece) :
    def __init__(self, game, team, pos, p_type = 'rook', upgrades = [], moved = False) : 
        super().__init__(game, team, pos, p_type, upgrades, moved)
    
    def moves(self) :
        moves = []
        boardstate = self.board.locations
        enemies = self.board.team_locations(self.enemy)
        for dir in [[0, -1], [0, 1], [-1, 0], [1, 0]] :
            for squares in range(1, max(self.game.board.dimension)) :
                attempt = (self.pos[0] + dir[0] * squares, self.pos[1] + dir[1] * squares)
                if attempt not in boardstate :
                    moves.append(attempt)
                elif attempt in enemies :
                    moves.append(attempt)
                    break
                else :
                    break


        moves = list(filter(lambda move : 0 <= move[0] < self.game.board.dimension[0] and 0 <= move[1] < self.game.board.dimension[0], moves))
        return moves

class Bishop(Piece) :
    def __init__(self, game, team, pos, p_type = 'bishop', upgrades = [], moved = False) : 
        super().__init__(game, team, pos, p_type, upgrades, moved)

    
    def moves(self) :
        moves = []
        boardstate = self.board.locations
        enemies = self.board.team_locations(self.enemy)
        for dir in [[-1, -1], [1, 1], [-1, 1], [1, -1]] :
            for squares in range(1, max(self.game.board.dimension)) :
                attempt = (self.pos[0] + dir[0] * squares, self.pos[1] + dir[1] * squares)
                if attempt not in boardstate :
                    moves.append(attempt)
                elif attempt in enemies :
                    moves.append(attempt)
                    break
                else :
                    break

        
        moves = list(filter(lambda move : 0 <= move[0] < self.game.board.dimension[0] and 0 <= move[1] < self.game.board.dimension[0], moves))
        return moves

class King(Piece) :
    def __init__(self, game, team, pos, p_type = 'king', upgrades = [], moved = False) : 
        super().__init__(game, team, pos, p_type, upgrades, moved)

    
    def moves(self) :
        moves = []
        teammates = self.board.team_locations(self.team)
        for dir in [[0, -1], [0, 1], [-1, 0], [1, 0], [-1, -1], [1, 1], [-1, 1], [1, -1]] :
                attempt = (self.pos[0] + dir[0], self.pos[1] + dir[1])
                if attempt not in teammates :
                    moves.append(attempt)
        self.castle(moves)
        
        moves = list(filter(lambda move : 0 <= move[0] < self.game.board.dimension[0] and 0 <= move[1] < self.game.board.dimension[0], moves))
        return moves
    
    def castle(self, moves) :
        enemy_sight = self.board.white_sight if self.enemy == 'white' else self.board.black_sight
        if self.moved or self.pos in enemy_sight :
            return
        corners = [(0, self.game.board.dimension[0] - 1), (self.game.board.dimension[0] - 1, self.game.board.dimension[1] - 1)] if self.team == 'white' else [(0, 0), (self.game.board.dimension[0] - 1, 0)]
        for corner in list(filter(lambda c : c in self.board.team_locations(self.team), corners)) :
            corner_is_valid = True
            corner_piece = self.board.get_piece(corner)
            if not corner_piece.moved :
                dir = -1 if corner[0] == 0 else 1
                slots = (corner[0] - dir, self.pos[0] + dir)
                for x in range(min(*slots), max(*slots) + 1) :
                    if (x, corner[1]) in list(enemy_sight) + self.board.team_locations(self.team) :
                        corner_is_valid = False
                if corner_is_valid :
                    moves.append(corner)

class Queen(Piece) :
    def __init__(self, game, team, pos, p_type = 'queen', upgrades = [], moved = False) : 
        super().__init__(game, team, pos, p_type, upgrades, moved)

    
    def moves(self) :
        moves = []
        boardstate = self.board.locations
        enemies = self.board.team_locations(self.enemy)
        for dir in [[0, -1], [0, 1], [-1, 0], [1, 0], [-1, -1], [1, 1], [-1, 1], [1, -1]] :
            for squares in range(1, max(self.game.board.dimension)) :
                attempt = (self.pos[0] + dir[0] * squares, self.pos[1] + dir[1] * squares)
                if attempt not in boardstate :
                    moves.append(attempt)
                elif attempt in enemies :
                    moves.append(attempt)
                    break
                else :
                    break
        
        moves = list(filter(lambda move : 0 <= move[0] < self.game.board.dimension[0] and 0 <= move[1] < self.game.board.dimension[0], moves))
        return moves


def makePiece(game, team = 'white', pos = (0, 0), p_type = 'pawn', upgrades = [], moved = False) :
    sourceKeys = [game, team, pos, p_type, upgrades, moved]
    match p_type :
        case 'pawn' :
            return Pawn(*sourceKeys)
        case 'rook' :
            return Rook(*sourceKeys)
        case 'knight' :
            return Knight(*sourceKeys)
        case 'bishop' :
            return Bishop(*sourceKeys)
        case 'queen' :
            return Queen(*sourceKeys)
        case 'king' :
            return King(*sourceKeys)
        case _ :
            print(f'ERROR : piece [{p_type}] not recognized')