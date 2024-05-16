import socket
import json
import pygame as pg
import sprite_utilities as su

class Client:

    def __init__(self, addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = 'Game'
        self.score = 0
        self.wave_num = 0
        self.players_features = [su.Sprite_features(su.player_one_features, 
                                                    is_player=True), 
                                 su.Sprite_features(su.player_two_features, 
                                                    is_player=True)]
        self.mob_features = su.Sprite_features(su.mob_features)
        self.players_health = [10] * 20
        self.max_players = 2

        try:
            self.sock.connect(addr) # подключаемся к айпи адресу сервера
            self.is_connected = True
        except:
            self.is_connected = False

    def handle_server(self):
        self.data = self.sock.recv(1024*20).decode('UTF-8')
        try:
            self.data = json.loads(self.data)
            self.insert_recv_data()
        except:
            print('Server was closed')
            self.sock.close()
            self.is_connected = False
    
    def check_pressed_keys(self):
        res = {'name':'keys', 'keys':{'forward':False, 
                                      'back':False, 
                                      'left':False, 
                                      'right':False,
                                      'shoot':False}}
        key = pg.key.get_pressed()
        if(key[self.players_features[0].forward_button]):
            res['keys']['forward'] = True
        if(key[self.players_features[0].back_button]):
            res['keys']['back'] = True
        if(key[self.players_features[0].left_button]):
            res['keys']['left'] = True
        if(key[self.players_features[0].right_button]):
            res['keys']['right'] = True
        if(key[self.players_features[0].shoot_button]):
            res['keys']['shoot'] = True
        self.data += [res]
    
    def send_info(self):
        self.data = [{'name':'state', 'state':self.state}]
        if self.state == 'Game':
            self.check_pressed_keys()
        self.data = json.dumps(self.data)
        self.sock.sendall(bytes(self.data, 'UTF-8'))

    def insert_recv_data(self):
        self.sprites_to_show = []
        self.sounds_to_play = []
        if self.state == 'Pause menu':
            self.other_players_state = self.data['Other_players_state']
            return

        is_player_alive = [False] * self.max_players     
        for data in self.data:
            match data['name']:
                case 'Player':
                    player_features \
                        = self.players_features[data['player_num']%2]


                    if data['is_invincible']:
                        animation \
                        = [player_features.direction_dict[data['direction']], 
                           player_features.disappear]
                        
                        self.sprites_to_show.append(tuple(\
                            [animation[int(data['anim_num'])%2], 
                             data['x'], data['y']]))
                    else:
                        self.sprites_to_show.append(tuple(\
                        [player_features.direction_dict[data['direction']], 
                         data['x'], data['y']]))
                    
                    self.players_health[data['player_num']] = data['health']
                    is_player_alive[data['player_num']] = True

                    for sound in data['sounds']:
                        self.sounds_to_play.append(\
                            player_features.sounds[sound])
                case 'Mob':
                    self.sprites_to_show.append(tuple(\
                        [self.mob_features.direction_dict[data['direction']], 
                         data['x'], data['y']]))
                    for sound in data['sounds']:
                        self.sounds_to_play.append(\
                            self.mob_features.sounds[sound])
                case 'Mob_bullet':
                    self.sprites_to_show.append(tuple(\
                        [self.mob_features.bullet, data['x'], data['y']]))
                case 'Effect':
                    self.sprites_to_show.append(tuple(\
                    [pg.image.load(su.explosion_animation[data['anim_num']]), 
                     data['x'], data['y']]))
                case 'Player_bullet':
                    self.sprites_to_show.append(tuple(\
                        [pg.transform.rotate(self.players_features[0].bullet, 
                                             data['direction']), 
                         data['x'], data['y']]))
                case 'Game_stats':
                    self.score = data['score']
                    self.wave_num = data['wave_num']
                    self.max_players = data['max_players']
                    self.players_health \
                        = self.players_health[:self.max_players]
                case _:
                    self.sprites_to_show.append(tuple(\
                        [pg.image.load(\
                          su.bonus_textures[data['name']][data['anim_num']]), 
                          data['x'], data['y']]))
        for num, player in enumerate(is_player_alive):
            if not player:
                self.players_health[num] = 0

    def draw(self, screen, volume=100):
        for sprites in self.sprites_to_show:
            screen.blit(sprites[0], (sprites[1:]))
        for sound in self.sounds_to_play:
            su.play_sound(sound, volume)