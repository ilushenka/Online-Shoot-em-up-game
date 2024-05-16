from random import randint, choice, uniform
from math import cos, sin, radians
import pygame as pg
import sprite_utilities as su
import constants as const


#создание группы спрайтов
all_sprites = pg.sprite.Group() 
#cоздание  группы мобов и их пуль
mobs = pg.sprite.Group()
mob_bullets = pg.sprite.Group()
#создание группы игроков и их пуль
players = pg.sprite.Group()
#Создание группы бонусов
bonuses = pg.sprite.Group()
effects = pg.sprite.Group()


class Player(pg.sprite.Sprite):
    def __init__(self, player_features, screen_width=const.WIDTH, 
                 screen_height=const.HEIGHT, sound_volume=100,
                 is_online=False):
        super().__init__() 

        self.features = su.Sprite_features(player_features, screen_width, 
                                             screen_height, True)
        self.direction = 'back'
        self.image = self.features.direction_dict[self.direction]
        self.rect = self.image.get_rect()

        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.last_time_shoot = -500
        self.shoot_delay = const.DEFAULT_SHOOT_DELAY
        self.shoot_mode = su.ShootModes.DEFAULT
        self.bonus_time = {'shoot_delay': 0,
                           'shoot_mode': 0}

        self.is_invincible = False
        self.invincible_animation = 0
        self.invincible_time = 0

        self.is_online = is_online
        if is_online:
            self.pressed_keys = {'forward':False, 
                                 'back':False, 
                                 'left':False, 
                                 'right':False, 
                                 'shoot':False}
            self.sounds = []

        self.sound_volume = sound_volume

        all_sprites.add(self)
        players.add(self)
        self.bullets = pg.sprite.Group()

    def update(self):

        self.direction = 'back'
        if self.is_online:    
            if(self.pressed_keys['forward'] and self.rect.top > 0):
                self.rect.y -= self.features.mov_speed
                self.direction = 'forward'
            if(self.pressed_keys['back'] \
            and self.rect.bottom <= self.screen_height):
                self.rect.y += self.features.mov_speed
                self.direction = 'back'
            if(self.pressed_keys['right'] \
            and self.rect.right <= self.screen_width):
                self.rect.x += self.features.mov_speed
                self.direction = 'right'
            if(self.pressed_keys['left'] and self.rect.left > 0):
                self.rect.x -= self.features.mov_speed
                self.direction = 'left'
            if(self.pressed_keys['shoot'] and 
            pg.time.get_ticks() - self.last_time_shoot >= self.shoot_delay):
                self.last_time_shoot = pg.time.get_ticks()
                self.shoot()

            self.pressed_keys = {'forward':False, 
                                 'back':False, 
                                 'left':False, 
                                 'right':False, 
                                 'shoot':False}
        else: 
            pressed_key = pg.key.get_pressed()       
            if(pressed_key[self.features.forward_button] and self.rect.top > 0):
                self.rect.y -= self.features.mov_speed
                self.direction = 'forward'
            if(pressed_key[self.features.back_button] \
            and self.rect.bottom <= self.screen_height):
                self.rect.y += self.features.mov_speed
                self.direction = 'back'
            if(pressed_key[self.features.right_button] \
            and self.rect.right <= self.screen_width):
                self.rect.x += self.features.mov_speed
                self.direction = 'right'
            if(pressed_key[self.features.left_button] and self.rect.left > 0):
                self.rect.x -= self.features.mov_speed
                self.direction = 'left'
            if(pressed_key[self.features.shoot_button] and 
            pg.time.get_ticks() - self.last_time_shoot >= self.shoot_delay):
                self.last_time_shoot = pg.time.get_ticks()
                self.shoot()

            self.image = self.features.direction_dict[self.direction]

        self.check_invincibility()
        self.check_bonuses()
    
    def shoot(self):
        for i in range(1, self.shoot_mode):
            left_bullet = Bullet(self.features.bullet_speed, 
                                 self.features.bullet, 
                                 self.rect.centerx, self.rect.top, 
                                 self.screen_width, self.screen_height, 
                                 self.sound_volume, 
                                 su.bullet_angles[f'left_{i}'])
            right_bullet = Bullet(self.features.bullet_speed, 
                                  self.features.bullet, 
                                  self.rect.centerx, self.rect.top, 
                                  self.screen_width, self.screen_height, 
                                  self.sound_volume, 
                                  su.bullet_angles[f'right_{i}'])
            all_sprites.add(left_bullet)
            all_sprites.add(right_bullet)
            self.bullets.add(left_bullet)
            self.bullets.add(right_bullet)
        bullet = Bullet(self.features.bullet_speed, self.features.bullet, 
                        self.rect.centerx, self.rect.top, self.screen_width, 
                        self.screen_height, self.sound_volume)
        all_sprites.add(bullet)
        self.bullets.add(bullet)
        if self.is_online:
            self.sounds.append('shoot_sound')
        else:
            su.play_sound(self.features.sounds['shoot_sound'], 
                                    self.sound_volume)

    def check_health(self):
        if self.features.health == 0:
            self.kill()
            if self.is_online:
                self.sounds.append('dead_sound')
            else:    
                su.play_sound(self.features.sounds['dead_sound'], 
                              self.sound_volume)
            return
        if not self.is_invincible:
            self.get_invincibility(pg.time.get_ticks())
    
    def check_bonuses(self):
        if(self.shoot_mode != su.ShootModes.DEFAULT \
           and pg.time.get_ticks() - self.bonus_time['shoot_mode'] \
            >= const.BONUS_DURATION):
            self.shoot_mode = su.ShootModes.DEFAULT
        if(self.shoot_delay != const.DEFAULT_SHOOT_DELAY \
           and pg.time.get_ticks() - self.bonus_time['shoot_delay'] \
            >= const.BONUS_DURATION):
            self.shoot_delay = const.DEFAULT_SHOOT_DELAY

    def check_invincibility(self):
        if self.is_invincible:
            if(pg.time.get_ticks() - self.invincible_time 
                > const.DEFAULT_DAMAGED_TIME):
                self.is_invincible = False
            else:
                animation = [self.image, self.features.disappear]
                self.invincible_animation += 0.25
                self.image = animation[int(self.invincible_animation)%2]

    def get_invincibility(self, time):
        self.is_invincible = True
        self.invincible_animation = 0
        self.invincible_time = time


class Mob(pg.sprite.Sprite):
    def __init__(self, mob_features, screen_width=const.WIDTH, 
                 screen_height=const.HEIGHT, 
                 sound_volume=100, is_online=False):
        super().__init__()
        
        self.features = su.Sprite_features(mob_features, screen_width, 
                                             screen_height)
    
        self.direction = 'forward'
        self.image = self.features.direction_dict[self.direction]

        self.sound_volume = sound_volume
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.rect = self.image.get_rect()
        self.set_trajectory()

        self.is_online = is_online

        if self.is_online:
            self.sounds = []

    @staticmethod
    def spawnMobs(mobs_num, mob_features, screen_width=const.WIDTH, 
                  screen_height=const.HEIGHT, 
                  sound_volume=100, is_online=False):
        for _ in range(mobs_num):
            mob = Mob(mob_features, screen_width, screen_height, 
                      sound_volume, is_online)
            all_sprites.add(mob)
            mobs.add(mob)

    def update(self):
        self.trajectory()     
        if(self.speedx > 0):
            self.direction = 'left'
        elif(self.speedx < 0):
            self.direction = 'right'
        else:
            self.direction = 'forward'

        self.image = self.features.direction_dict[self.direction]

        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if(self.rect.top > self.screen_height \
           or self.rect.bottom < -self.screen_height/4 \
           or self.rect.right < -4*self.rect.width \
           or self.rect.left > self.screen_width + 4*self.rect.width):
            self.set_trajectory()
            self.features.health = const.DEFAULT_MOB_HEALTH
        if(uniform(0,100) <= const.DEFAULT_MOB_SHOOT_CHANCE):
            self.shoot()  
        self.check_collision()

    def check_collision(self):
        hits = pg.sprite.spritecollide(self, players, False)
        for hit in hits:
            if not hit.is_invincible:
                self.kill()
                hit.features.health -= 1
                if hit.is_online:
                    hit.sounds.append('hurt_sound')
                else:
                    su.play_sound(hit.features.sounds['hurt_sound'], hit.sound_volume)
            hit.check_health()

    def check_health(self):
        if self.features.health == 0:
            if self.is_online:
                self.sounds.append('dead_sound')
            else:
                su.play_sound(self.features.sounds['dead_sound'])
            self.kill()
            if uniform(0, 100) <= const.DEFAULT_BONUS_DROP_CHANCE:
                Bonus.spawn_bonus(self.rect.x, self.rect.y, 
                                  self.screen_width, self.screen_height)

    def shoot(self):
        bullet = Bullet(self.features.bullet_speed, self.features.bullet, 
                        self.rect.centerx, self.rect.bottom + 100, 
                        self.screen_width, self.screen_height, 
                        self.sound_volume)
        all_sprites.add(bullet)
        mob_bullets.add(bullet)

    def set_trajectory(self):
        stop_cord = randint(self.rect.height, self.screen_height/3)
        trajectory_list = [self.sin_trajectory,
                           lambda:self.arc_trajectory(1), 
                           lambda:self.arc_trajectory(-1), 
                           lambda:self.default_trajectory(stop_cord)]
        self.trajectory_is_set = False
        self.trajectory = trajectory_list[randint(0, len(trajectory_list)-1)]
        self.trajectory()

    def sin_trajectory(self):
        if not self.trajectory_is_set:
            self.trajectory_is_set = True
            self.trajectory_coef = randint(30,100)

            self.rect.x = choice(
                [randint(-2*self.rect.width, - self.rect.width), 
                randint(self.screen_width + self.rect.width, 
                        self.screen_width + 2*self.rect.width)])
            self.rect.y = randint(0, self.screen_height/2)
            self.speedx =  randint(int(self.features.mov_speed/2), 
                                   int(self.features.mov_speed))
        self.speedy = 2*cos(self.rect.x / self.trajectory_coef)
        if(self.rect.centerx < -4*self.rect.width \
           or self.rect.centerx > self.screen_width + 4*self.rect.width):
            self.speedx = -self.speedx

    def arc_trajectory(self, direction):
        if not self.trajectory_is_set:
            self.trajectory_is_set = True
            self.trajectory_coef = randint(50, 100)
            self.rect.x = randint(self.screen_width/4, 3*self.screen_width/4)
            self.rect.y = - self.rect.height*2
            self.speedy = randint(int(self.features.mov_speed/2), 
                                  int(self.features.mov_speed))
        self.speedx = 0 if self.rect.y < 0 \
                        else direction*2*self.rect.y/self.trajectory_coef

    def default_trajectory(self, stop_cord):
        if not self.trajectory_is_set:
            self.trajectory_is_set = True
            self.rect.x = randint(self.rect.width, 
                                  self.screen_width - self.rect.width)
            self.rect.y = - self.rect.height*2
            self.speedy = randint(int(self.features.mov_speed/2), 
                                  int(self.features.mov_speed))
        if self.rect.y < stop_cord:
            self.speedx = 0
        else:
            if self.speedy != 0:
                self.speedx = choice([self.speedy, -self.speedy])
            else:
                self.speedx = self.speedx
            self.speedy = 0
            if self.rect.centerx < 0 or self.rect.centerx > self.screen_width:
                self.speedx = -self.speedx


class Bullet(pg.sprite.Sprite):
    def __init__(self, mov_speed, bullet_texture, start_x, 
                 start_y, screen_width=const.WIDTH, 
                 screen_height=const.HEIGHT, 
                 sound_volume=100, angle=0):
        super().__init__()
        self.image = pg.transform.rotate(bullet_texture, angle)
        self.angle = angle
        self.mov_speed = mov_speed
        self.mov_speedx = self.mov_speed * sin(radians(angle))
        self.mov_speedy = self.mov_speed * cos(radians(angle))
        self.rect = self.image.get_rect()
        self.rect.bottom = start_y
        self.rect.centerx = start_x

        self.sound_volume = sound_volume
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self):
        self.rect.y += self.mov_speedy
        self.rect.x += self.mov_speedx
        if(self.rect.bottom < -self.screen_height/4 or self.rect.top > self.screen_height 
           or self.rect.right < 0 or self.rect.left > self.screen_width):
            self.kill()
        for player in players:
            self.checkHit(mobs, player.bullets)
        self.checkHit(players, mob_bullets)

    def checkHit(self, group, bullets_group):
        hits = pg.sprite.groupcollide(group, bullets_group, False, False)
        for hit, bullets in hits.items():
            for bullet in bullets:
                Effects(max(hit.rect.left, bullet.rect.left), 
                        max(hit.rect.top, bullet.rect.top), 
                        su.explosion_animation, 
                        const.EXPLOSION_ANIMATION_TIME)
                bullet.kill()
            hit.features.health -= 0 if type(hit) is Player \
                                         and hit.is_invincible else 1
            if hit.is_online:
                hit.sounds.append('hurt_sound')
            else:
                su.play_sound(hit.features.sounds['hurt_sound'], self.sound_volume)

            hit.check_health()


class Bonus(pg.sprite.Sprite):
    def __init__(self, bonus_texture, bonus_name, spawn_x, spawn_y, 
                 screen_width=const.WIDTH, screen_height=const.HEIGHT):
        super().__init__()
        self.spawn_time = pg.time.get_ticks()
        self.bonus_name = bonus_name
        self.animation = [pg.transform.scale( \
            pg.image.load(bonus_texture[i]).convert_alpha(), 
            (screen_width/const.WIDTH*const.BONUS_SIZE,
             screen_height/const.HEIGHT*const.BONUS_SIZE)) \
            for i in range(len(bonus_texture))]
        self.image = self.animation[0]
        self.rect = self.image.get_rect()
        self.rect.x = spawn_x
        self.rect.y = spawn_y
        self.speed = const.DEFAULT_BONUS_SPEED
        self.animation_time = 0
        self.current_animation = 0


        self.screen_width = screen_width
        self.screen_height = screen_height

    @staticmethod
    def spawn_bonus(spawn_x, spawn_y, screen_width=const.WIDTH, 
                    screen_height=const.HEIGHT):
        bonus_name = choice([items for items in su.bonus_textures.keys()])
        bonus = Bonus(su.bonus_textures[bonus_name], bonus_name, 
                      spawn_x, spawn_y, screen_width, screen_height)
        bonuses.add(bonus)
        all_sprites.add(bonus)

    def update(self):
        if(pg.time.get_ticks() - self.spawn_time >= const.BONUS_LIFETIME \
           or self.rect.top > self.screen_height):
            self.kill()
        self.rect.y += self.speed
        self.check_animation()
        Bonus.check_collisions()
    
    @staticmethod
    def check_collisions():
        collisions = pg.sprite.groupcollide(players, bonuses, False, False)
        for person, bonus in collisions.items():
            for item in bonus:
                if person.is_online:
                    person.sounds.append('bonus_sound')
                else:
                    su.play_sound(person.features.sounds['bonus_sound'], person.sound_volume)

                if item.bonus_name == 'heal_bonus':
                    Bonus.add_health(person)
                elif item.bonus_name == 'bullet_bonus':
                    Bonus.change_shoot_mode(person)
                else:
                    Bonus.change_shoot_delay(person)
                item.kill()

    @staticmethod
    def add_health(person):
        person.features.health += const.DEFAULT_BONUS_HEAL
        if person.features.health > const.DEFAULT_PLAYER_HEALTH:
            person.features.health = const.DEFAULT_PLAYER_HEALTH

    @staticmethod
    def change_shoot_mode(person):
        if person.shoot_mode == su.ShootModes.SEVEN_SHOT:
            pass
        else:
            person.shoot_mode += 1
        person.bonus_time['shoot_mode'] = pg.time.get_ticks()

    @staticmethod
    def change_shoot_delay(person):
        if person.shoot_delay > const.MIN_SHOOT_DELAY:
            person.shoot_delay /= const.SHOOT_DELAY_COEF
            if person.shoot_delay < const.MIN_SHOOT_DELAY:
                person.shoot_delay = const.MIN_SHOOT_DELAY
        person.bonus_time['shoot_delay'] = pg.time.get_ticks()

    def check_animation(self):
        self.animation_time += const.BONUS_ANIMATION
        self.current_animation = int(self.animation_time)%len(self.animation)
        self.image \
            = self.animation[self.current_animation]       


class Effects(pg.sprite.Sprite):
    def __init__(self, x, y, animation_list, animation_time):
        super().__init__()
        self.animation_list = [pg.image.load(item).convert_alpha() \
                               for item in animation_list]
        self.image = self.animation_list[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.animation_time = 0
        self.current_animation = 0
        self.tick = len(animation_list)/(const.FPS*animation_time)
        all_sprites.add(self)
        effects.add(self)
    def update(self):  
        self.animation_time += self.tick
        self.current_animation \
            = int(self.animation_time)%(len(self.animation_list))
        if self.animation_time > len(self.animation_list):
            self.kill()
        else:    
            self.image \
                = self.animation_list[self.current_animation]


class Button():
    def __init__(self, x, y, width, height, text, texture_path, 
                 font, hover_texture_path=None, sound_path=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.is_hovered = False            

        self.image = pg.image.load(texture_path)
        self.image = pg.transform.scale(self.image, (width, height))
        self.hover_image = self.image
        
        if hover_texture_path:
            self.hover_image = pg.image.load(hover_texture_path)
            self.hover_image = pg.transform.scale(self.hover_image, 
                                                  (width, height))

        self.rect = self.image.get_rect(topleft = (x,y))

        self.sound = None
        if sound_path:
            self.sound = pg.mixer.Sound(sound_path)

    def update(self, screen):
        if self.is_hovered:
            image = self.hover_image
        else:
            image = self.image
        text_surface = self.font.render(self.text, True, const.RED)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        screen.blit(image, self.rect.topleft)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event, volume=100):
        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 
            and self.is_hovered):
            if self.sound:
                su.play_sound(self.sound, volume)
            pg.event.post(pg.event.Event(pg.USEREVENT, button=self))

    @staticmethod
    def list_handle_event(event, buttons=None, volume=100):
        if buttons:
            for button in buttons:
                button.handle_event(event, volume)

    @staticmethod
    def list_check_hover(buttons, screen):
        for button in buttons:
            button.check_hover(pg.mouse.get_pos())
            button.update(screen)


class Controls_button(Button):
    def __init__(self, x, y, width, height, text, control_button, 
                 key, texture_path, font, hover_texture_path=None, 
                 sound_path=None):
        super().__init__(x, y, width, height, text, texture_path, 
                         font, hover_texture_path, 
                         sound_path)
        self.control_button = control_button
        self.key = key

    def change_controls(self, new_key, new_str):
        match self.key:
            case 'shoot_p1':
                su.player_one_features['shoot_button'] = new_key
            case 'up_p1':
                su.player_one_features['forward_button'] = new_key
            case 'down_p1':
                su.player_one_features['back_button'] = new_key
            case 'right_p1':
                su.player_one_features['right_button'] = new_key
            case 'left_p1':
                su.player_one_features['left_button'] = new_key
            case 'shoot_p2':
                su.player_two_features['shoot_button'] = new_key
            case 'up_p2':
                su.player_two_features['forward_button'] = new_key
            case 'down_p2':
                su.player_two_features['back_button'] = new_key
            case 'right_p2':
                su.player_two_features['right_button'] = new_key
            case 'left_p2':
                su.player_one_features['left_button'] = new_key
        self.text = new_str
        self.control_button = new_key


class Cursor():
    def __init__(self, inactive_texture, active_texture, sound_path=None):
        self.inactive_texture \
             = pg.image.load(inactive_texture).convert_alpha()
        self.active_texture = pg.image.load(active_texture).convert_alpha()
        self.cursor = self.inactive_texture
        if sound_path:
            self.sound = pg.mixer.Sound(sound_path)
        pg.mouse.set_visible(False)

    def update(self, screen, is_game_on=False):
        if not is_game_on:
            screen.blit(self.cursor, pg.mouse.get_pos())

    def check_hover(self, event, volume=100):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.cursor = self.active_texture
            su.play_sound(self.sound, volume)       
        else:
            self.cursor = self.inactive_texture
