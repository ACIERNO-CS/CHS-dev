import os
import pygame

BASE_PATH = 'data/'

def load_image(path) :
    img = pygame.image.load(path)#.convert() # convert helps computationally (?)
    img.set_colorkey((0, 0, 0)) # change color to transparent
    return img

def load_images(path) :
    images = []
                    # sorted makes the order consistent across OS (freakin' linux)
    for img_name in sorted(os.listdir(BASE_PATH + path)) :
        images.append(load_image(path + '/' + img_name))
    return images

def load_sound(path) :
    return pygame.mixer.Sound(path)

def surf_center(surf1, surf2) :
    return (surf1.get_rect().centerx - surf2.get_rect().width / 2, surf1.get_rect().centery - surf2.get_rect().height / 2)

def set_sfx_volume(game, volume) :
    game.sfx_volume = volume

def set_brightness(game, brightness) :
    game.brightness = brightness

def play_sound(game, sound, volume = 1) :
    if not pygame.mixer.Channel(5).get_busy() :
        sound.set_volume(volume * (game.sfx_volume / 10))
        pygame.mixer.Sound.play(sound)
        pygame.mixer.music.stop()

def pull_assets(lib = {}, root = BASE_PATH, level = 0) :
    level += 1
    for file in os.listdir(root) :
        file_name, file_extension = os.path.splitext(file)
        if os.path.isdir(root + file_name) :
            lib[file_name] = pull_assets(lib = {'level' : level}, root = root + file_name + '/', level = level)
        elif os.path.isfile(root + file) :
            match file_extension :
                case '.png' | '.jpeg' | '.jpg' :
                    lib[file_name] = load_image(root + file)
                case '.wav' :
                    lib[file_name] = load_sound(root + file)
                case '.json' | '.gif' | '.txt' :
                    pass
                case _ :
                    print('Failed to load [' + file + ' ] type unknown.')
    return lib