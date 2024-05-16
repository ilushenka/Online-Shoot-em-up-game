from enum import IntEnum
from math import pow
import pygame as pg
import constants as const

class Sprite_features():
    def __init__(self, sprite_features, screen_width=const.WIDTH, 
                 screen_height=const.HEIGHT, is_player=False):
        
        forward = pg.image.load(sprite_features['forward']).convert_alpha()
        
        new_mob_size = (tuple(i*j for i, j in \
                               zip(forward.get_size(),
                                   (screen_width/const.WIDTH, 
                                    screen_height/const.HEIGHT))))

        forward = pg.transform.scale(forward, new_mob_size)
        
        self.direction_dict = {
            'forward': forward,
            'left': pg.transform.rotate(forward, 20),
            'right': pg.transform.rotate(forward, -20),
            'back': pg.transform.scale( \
                pg.image.load(sprite_features['back']).convert_alpha(), 
                new_mob_size)
        }

        self.bullet \
            = pg.image.load(sprite_features['bullet']).convert_alpha()
        self.bullet \
            = pg.transform.scale(self.bullet, 
                                 tuple(i*j for i,j in \
                                 zip(self.bullet.get_size(),
                                 (screen_width/const.WIDTH, 
                                 screen_height/const.HEIGHT))))

        self.sounds = {
            'shoot_sound':pg.mixer.Sound(sprite_features['shoot_sound']),
            'hurt_sound':pg.mixer.Sound(sprite_features['hurt_sound']),
            'dead_sound':pg.mixer.Sound(sprite_features['dead_sound'])
        }

        self.mov_speed \
            = sprite_features['speed'] \
              *pow((screen_height*screen_width)/(const.WIDTH*const.HEIGHT), 
                   0.5)
        self.bullet_speed \
            = sprite_features['bullet_speed'] \
              *pow((screen_height*screen_width)/(const.WIDTH*const.HEIGHT), 
                   0.5)
        self.health = sprite_features['health']
        if is_player:
            self.sounds['bonus_sound'] = pg.mixer.Sound(bonus_sound)
            self.disappear = pg.transform.scale( \
                pg.image.load(sprite_features['disappear']).convert_alpha(), 
                new_mob_size)
            self.forward_button = sprite_features['forward_button']
            self.right_button = sprite_features['right_button']
            self.left_button = sprite_features['left_button']
            self.back_button = sprite_features['back_button']
            self.shoot_button = sprite_features['shoot_button']
        else:
            self.bullet = pg.transform.rotate(self.bullet, 180)


class ShootModes(IntEnum):
    DEFAULT = 1
    TRIPLE_SHOT = 2
    PENTA_SHOT = 3
    SEVEN_SHOT = 4


def play_sound(sound, volume=100):
    sound.set_volume(volume/100)
    pg.mixer.find_channel(True).play(sound)

cursor_features = {
    'cursor_inactive':'./images/cursor_inactive.png',
    'cursor_active':'./images/cursor_active.png',
    'cursor_click_sound':'./sounds/cursor_click.ogg'
}

mob_features = {
    'forward':'./images/mob_forward.png', 
    'back':'./images/mob_back.png',
    'bullet':'./images/rocket.png',
    'shoot_sound':'./sounds/mob_shoot_sound.wav',    
    'dead_sound':'./sounds/mob_dead_sound.wav',   
    'hurt_sound':'./sounds/mob_hurt_sound.wav',     
    'health':const.DEFAULT_MOB_HEALTH,
    'speed':const.DEFAULT_MOB_MOV_SPEED,
    'bullet_speed':const.DEFAULT_MOB_BULLET_MOV_SPEED
}

player_one_features = {
    'forward':'./images/player_one_forward.png', 
    'back':'./images/player_one_back.png',
    'bullet':'./images/rocket.png',
    'disappear':'./images/disappear.png',
    'shoot_sound':'./sounds/player_shoot_sound.wav',    
    'dead_sound':'./sounds/player_dead_sound.wav',    
    'hurt_sound':'./sounds/player_hurt_sound.wav',    
    'health':const.DEFAULT_PLAYER_HEALTH,
    'speed':const.DEFAULT_PLAYER_MOV_SPEED,
    'bullet_speed':const.DEFAULT_PLAYER_BULLET_MOV_SPEED,
    'forward_button':const.DEFAULT_PLAYER_ONE_FORWARD_BUTTON,
    'right_button':const.DEFAULT_PLAYER_ONE_RIGHT_BUTTON,
    'left_button':const.DEFAULT_PLAYER_ONE_LEFT_BUTTON,
    'back_button':const.DEFAULT_PLAYER_ONE_BACK_BUTTON,
    'shoot_button':const.DEFAULT_PLAYER_ONE_SHOOT_BUTTON
}

player_two_features = {
    'forward':'./images/player_two_forward.png', 
    'back':'./images/player_two_back.png',
    'bullet':'./images/rocket.png',
    'disappear':'./images/disappear.png',
    'shoot_sound':'./sounds/player_shoot_sound.wav',    
    'dead_sound':'./sounds/player_dead_sound.wav',    
    'hurt_sound':'./sounds/player_hurt_sound.wav',    
    'health':const.DEFAULT_PLAYER_HEALTH,
    'speed':const.DEFAULT_PLAYER_MOV_SPEED,
    'bullet_speed':const.DEFAULT_PLAYER_BULLET_MOV_SPEED,
    'forward_button':const.DEFAULT_PLAYER_TWO_FORWARD_BUTTON,
    'right_button':const.DEFAULT_PLAYER_TWO_RIGHT_BUTTON,
    'left_button':const.DEFAULT_PLAYER_TWO_LEFT_BUTTON,
    'back_button':const.DEFAULT_PLAYER_TWO_BACK_BUTTON,
    'shoot_button':const.DEFAULT_PLAYER_TWO_SHOOT_BUTTON
}

bonus_textures = {
    'heal_bonus':['./images/heal_bonus.png'],
    'bullet_bonus':['./images/power_up/1.png', 
                    './images/power_up/2.png'],
    'delay_bonus':['./images/power_up/3.png',
                   './images/power_up/4.png']
}

bonus_sound = './sounds/bonus_sound.mp3'

bullet_angles = {
    'left_1':30,
    'left_2':20,
    'left_3':10,
    'right_1':-30,
    'right_2':-20,
    'right_3':-10,
    'forward':0
}

explosion_animation = ['./images/explosion/1.png',
                       './images/explosion/2.png',
                       './images/explosion/3.png',
                       './images/explosion/4.png',
                       './images/explosion/5.png']
