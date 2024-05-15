import socket
import json
from dataclasses import asdict
import sys
import pygame as pg
from sprites import Player, Mob, players, \
      mob_bullets, mobs, bonuses, effects, all_sprites
from sprite_utilities import player_one_features, mob_features
import constants as const
import sprite_data
PORT =  8080 # Адрес сервера
MAX_PLAYERS = 2 # Максимальное кол-во подключений

pg.init() 

class Server:
    def __init__(self, addr, max_conn, width=const.WIDTH, 
                 height=const.HEIGHT, screen=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(addr)
  
        if screen:
            self.screen = screen
        else:
            self.screen = pg.display.set_mode((800, 600), flags=pg.HIDDEN)

        self.max_players = max_conn
        self.players = []
        self.is_closed = False

        self.states = ['Game'] * max_conn
        self.data = [0] * max_conn
        self.width = width
        self.height = height
        self.new_game = True
        self.is_new_wave = True
        self.wave_num = 0
        self.score = 0
        self.conn_num = 0
        
    def host_server(self):
        self.sock.listen()
        self.listen()    
    
    def listen(self):
        clients = []
        for _ in range(self.max_players):
            try:
                client, address = self.sock.accept()
                print("New connection", address)
                self.conn_num += 1
                clients.append(client)
            except:
                print('Server was closed')
                return
        self.handle_client(clients)

    def handle_client(self, clients):
        self.players = []
        self.clients_num = len(clients)
        for player_num in range(len(clients)):
            self.players.append(Player(player_one_features, self.width, 
                                    self.height, is_online=True))
            players.add(self.players[player_num])

        while True:
            try:
                self.game_update()
                self.update_resp_data()
                if self.is_closed:
                    break

                for client_num, client in enumerate(clients):
                    if self.states[client_num] != 'Disconnected': 
                        try:
                            client.sendall(bytes(self.data[client_num], 
                                                 'UTF-8'))
                        except:
                            self.player_disconnect(client_num)
                
                for client_num, client in enumerate(clients):
                    if self.states[client_num] != 'Disconnected':
                        try:
                            self.data[client_num] \
                                = client.recv(1024*10).decode('UTF-8')
                        except:
                            self.player_disconnect(client_num)

                for client_num, data in enumerate(self.data):
                    if self.states[client_num] == 'Disconnected':
                        pass
                    elif not data:
                        self.player_disconnect(client_num)

                if len(players) == 0:
                    break

                for client_num, client in enumerate(clients):
                    if self.states[client_num] != 'Disconnected':
                        self.insert_recv_data(client_num)
            except Exception as e:
                print(e)
                pg.quit()
                sys.exit()
                break

    def player_disconnect(self, client_num):
        print(f"{client_num + 1} player disconnected")
        self.players[client_num].kill()
        self.states[client_num] = 'Disconnected' 

    def insert_recv_data(self, client_num):
        self.data[client_num] = json.loads(self.data[client_num])

        if not (self.data[client_num][0]['name'] == 'state' \
                and self.data[client_num][0]['state'] == 'Pause menu'):
            self.states[client_num] \
            = self.insert_player_recv_data(self.players[client_num],
                                           self.data[client_num])
        else:
            self.states[client_num] = self.data[client_num][0]['state']

    def insert_player_recv_data(self, player, data):
        for item in data:
            match item['name']:
                case 'keys':
                    player.pressed_keys = item['keys']
                case 'state':
                    state = item['state']
        return state

    def update_resp_data(self):
        for client_num in range(self.clients_num):
            if self.states[client_num] == 'Disconnected':
                pass
            else:
                self.data[client_num] = self.set_server_data(client_num)
                self.data[client_num] = json.dumps(self.data[client_num])
        for player in players:
            player.sounds =[]
        for mob in mobs:
            mob.sounds = []      

    def set_server_data(self, client_num):
        res = []
        if self.states[client_num] == 'Pause menu':
            res = {'Other_players_state':\
                   [state for state in self.states \
                    if not self.states[client_num] is state]}
        else:
            sprites = sprite_data.set_sprites_data(self.players, players, 
                                                   mobs, mob_bullets, bonuses, 
                                                   effects, self.states)
            res += sprites
            res = list(map(asdict, res)) + [{'name':'Game_stats', 
                                             'wave_num':self.wave_num, 
                                             'score':self.score, 
                                             'max_players':self.clients_num}]
        
        return res
    
    def game_update(self):
        if self.states.count('Game') != 0:
            if self.new_game:
                self.new_game = False
                for sprite in all_sprites:
                    if not sprite in players:
                        sprite.kill()
                    else:
                        sprite.rect.x = self.width/2
                        sprite.rect.y = 3*self.height/4
                self.score = 0
                self.wave_num = 0
            self.new_wave()
            mobs_num = len(mobs)
            all_sprites.update()
            if mobs_num > len(mobs):
                self.score \
                    += (mobs_num - len(mobs)) * const.DEFAULT_KILL_POINTS

    def new_wave(self):
        if self.is_new_wave:
            self.is_new_wave = False
            self.wave_num += 1
            self.remain_mobs = self.wave_num*2

        mobs_num = self.remain_mobs \
            if self.remain_mobs < const.DEFAULT_MAX_MOB_NUM \
                else const.DEFAULT_MAX_MOB_NUM
        
        Mob.spawnMobs(mobs_num, mob_features, self.width, 
                      self.height, is_online=True)
        
        self.remain_mobs -= mobs_num
        self.is_new_wave = True \
            if self.remain_mobs == 0 and len(mobs) == 0 else self.is_new_wave

