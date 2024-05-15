import constants as const
import pygame as pg
from sprites import Button, Controls_button


def check_music(pause=False, start_game=False, main_menu=False, stop=False):
    if start_game:
        pg.mixer.music.load(menu_features['game_music'])
        pg.mixer.music.play(-1)
    elif main_menu:
        pg.mixer.music.load(menu_features['menu_music'])
        pg.mixer.music.play(-1)
    elif stop:
        pg.mixer.music.stop()
    elif pause:
        pg.mixer.music.pause()
    else:
        pg.mixer.music.unpause()
    
def print_text(screen, string, font, color, x=0, y=0):
    text_surface = font.render(string, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def set_background_image(screen, image, width=const.WIDTH, 
                         height=const.HEIGHT):
    background_image = pg.image.load(image).convert()
    screen.blit(pg.transform.scale(background_image, 
                                   (width, height)), (0, 0))    

def check_default_events(event, cursor, volume=100, buttons=None):
    if event.type == pg.QUIT:
        pg.quit()
        sys.exit()
    Button.list_handle_event(event, buttons, volume)
    cursor.check_hover(event, volume)

def get_high_scores_data(file_name):
    high_scores = open(file_name, 'r')
    scores = []
    for i in range(10):
        line = high_scores.readline()
        scores.append(line)
        if not line:
            break
        i += 1
    high_scores.close()
    return scores

def set_high_scores_data(file_name, score, scores, record_pos, nickname):
    file = open(file_name, 'w')
    nickname = nickname if nickname else 'Ilya'
    scores.insert(record_pos, f'{nickname} {score}\n')
    file.writelines(scores)
    file.close()    


class TextBox:
    def __init__(self, x, y, width, height, inactive_color, 
                 active_color, text_font, text=''):
        self.rect = pg.Rect(x, y, width, height)
        self.rect.center = (x, y)
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.current_color = inactive_color
        self.text = text
        self.text_font = text_font
        self.txt_surface = text_font.render(text, True, self.current_color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.current_color = self.active_color if self.active \
                 else self.inactive_color
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    return self.text
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.text_font.render(self.text, True, 
                                                         self.current_color)

    def update(self):
        width = max(self.rect.width, self.txt_surface.get_width()+10)
        self.rect.width = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pg.draw.rect(screen, self.current_color, self.rect, 2)

        
class DropDown():
    def __init__(self, color_menu, color_option, x, y, width, height, 
                 font, main_str, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.font = font
        self.main_str = main_str
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.rect = pg.Rect((x,y), (width,height))
        self.rect.center = (x,y)

    def draw(self, screen):
        pg.draw.rect(screen, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main_str, 1, const.CREAM)
        screen.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in zip(range(10), self.options):
                rect = self.rect.copy()
                rect.y += (i+1)*self.rect.height
                pg.draw.rect(screen, 
                             self.color_option\
                             [1 if text == self.active_option else 0], 
                             rect, 0)
                msg = self.font.render(text, 1, const.CREAM)
                screen.blit(msg, msg.get_rect(center = rect.center))

    def update(self, event_list):
        mpos = pg.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        for i, text in  zip(range(10),self.options):
            rect = self.rect.copy()
            rect.y += (i+1)*self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = text
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option != -1:
                    self.draw_menu = False
                    return self.active_option
        return -1
    

class Slider:
    def __init__(self, pos: tuple, size: tuple, 
                 initial_val: float, min_val: int,
                 mav_val: int, text_font) -> None:
        self.pos = pos
        self.size = size
        self.hovered = False
        self.grabbed = False

        self.slider_left_pos = self.pos[0] - (size[0]//2)
        self.slider_right_pos = self.pos[0] + (size[0]//2)
        self.slider_top_pos = self.pos[1] - (size[1]//2)

        self.min_val = min_val
        self.mav_val = mav_val
        self.initial_val = (self.slider_right_pos
                            - self.slider_left_pos)*initial_val

        self.container_rect = pg.Rect(self.slider_left_pos, 
                                      self.slider_top_pos, 
                                      self.size[0], self.size[1])
        self.button_rect = pg.Rect(self.slider_left_pos 
                                   + self.initial_val - 5, 
                                   self.slider_top_pos, 10, self.size[1])

        # label
        self.font = text_font
        self.text = self.font.render('volume: ' + str(int(self.get_value())), 
                                     True, const.CREAM, None)
        self.label_rect = self.text.get_rect(center = 
                                             (self.pos[0],
                                              self.slider_top_pos - 15))
        
    def move_slider(self, mouse_pos):
        pos = mouse_pos[0]
        if pos < self.slider_left_pos:
            pos = self.slider_left_pos
        if pos > self.slider_right_pos:
            pos = self.slider_right_pos
        self.button_rect.centerx = pos

    def hover(self):
        self.hovered = True

    def render(self, screen):
        pg.draw.rect(screen, const.RED, self.container_rect)
        pg.draw.rect(screen, const.CREAM, self.button_rect)

    def get_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos - 1
        button_val = self.button_rect.centerx - self.slider_left_pos

        return (button_val/val_range)*(self.mav_val-self.min_val) \
                + self.min_val
    
    def display_value(self, screen):
        self.text = self.font.render('volume: ' + str(int(self.get_value())), 
                                     True, const.CREAM, None)
        screen.blit(self.text, self.label_rect)

    def check(self, screen):
        mouse_pos = pg.mouse.get_pos()
        mouse = pg.mouse.get_pressed()
        if self.container_rect.collidepoint(mouse_pos):
            if mouse[0]:
                self.grabbed = True
        if not mouse[0]:
            self.grabbed = False
        if self.button_rect.collidepoint(mouse_pos):  
            self.hover()
        if self.grabbed:
            self.move_slider(mouse_pos)
            self.hover()
        else:
            self.hovered = False
        self.render(screen)
        self.display_value(screen)
        return self.get_value()


class Buttons_placement():
    def __init__(self, font, width=const.WIDTH, height=const.HEIGHT):
        self.settings_button_width \
            = width/const.WIDTH * const.SETTINGS_BUTTON_WIDTH
        self.settings_button_height \
            = height/const.HEIGHT * const.SETTINGS_BUTTON_HEIGHT 
        self.button_width=width/const.WIDTH * const.BUTTON_WIDTH
        self.button_height=height/const.HEIGHT * const.BUTTON_HEIGHT

        button_space = self.button_height
        center_x = (width/2 - self.button_width/2)
        center_y = (height/2 - self.button_height/2)
        settings_button_x = 3*width/5
        settings_button_y = height/3 

        self.font = font
        self.dict = {
            'start':Button(center_x, center_y, self.button_width, 
                           self.button_height, 'Play',
                           menu_features['button_inactive'],
                           self.font, 
                           menu_features['button_active'], 
                           menu_features['button_click_sound']),
            'settings':Button(center_x, center_y + button_space, 
                              self.button_width, self.button_height, 
                              'Settings', menu_features['button_inactive'], 
                              self.font,
                              menu_features['button_active'], 
                              menu_features['button_click_sound']),
            'scores':Button(center_x, center_y + button_space*2, 
                            self.button_width, self.button_height, 
                            'Scores', menu_features['button_inactive'],
                            self.font,  
                            menu_features['button_active'], 
                            menu_features['button_click_sound']),
            'quit':Button(center_x, center_y + button_space*3, 
                          self.button_width, self.button_height, 'Quit', 
                          menu_features['button_inactive'],
                          self.font, 
                          menu_features['button_active'], 
                          menu_features['button_click_sound']),
            'back':Button(self.button_width,  height - self.button_height*2, 
                          self.button_width, self.button_height, 'Back',
                          menu_features['button_inactive'], 
                          self.font, menu_features['button_active'], 
                          menu_features['button_click_sound']),
            'resume':Button(center_x , center_y, self.button_width, 
                            self.button_height, 'Resume',
                            menu_features['button_inactive'], 
                            self.font, menu_features['button_active'], 
                            menu_features['button_click_sound']),
            'main_menu':Button(center_x, center_y + button_space, 
                               self.button_width, self.button_height, 
                               'Main Menu', menu_features['button_inactive'], 
                               self.font, menu_features['button_active'], 
                               menu_features['button_click_sound']),
            'retry':Button(center_x, center_y + button_space, 
                           self.button_width, self.button_height, 'Retry',
                           menu_features['button_inactive'],
                           self.font, menu_features['button_active'], 
                           menu_features['button_click_sound']),
            'quit_from_game_over':Button(center_x, 
                                         center_y + button_space*2, 
                                         self.button_width, self.button_height, 
                                         'Main Menu', 
                                         menu_features['button_inactive'], 
                                         self.font, 
                                         menu_features['button_active'], 
                                         menu_features['button_click_sound']),
            '1 player':Button(center_x - self.button_width, center_y, 
                              self.button_width, self.button_height, 
                              '1 player', menu_features['button_inactive'], 
                              self.font, menu_features['button_active'], 
                              menu_features['button_click_sound']),
            '2 players':Button(center_x + self.button_width, center_y, 
                               self.button_width, self.button_height, 
                               '2 players', menu_features['button_inactive'], 
                               self.font, menu_features['button_active'], 
                               menu_features['button_click_sound']),
            'host':Button(center_x - self.button_width, center_y, 
                              self.button_width, self.button_height, 
                              'Host', menu_features['button_inactive'], 
                              self.font, menu_features['button_active'], 
                              menu_features['button_click_sound']),
            'connect':Button(center_x + self.button_width, center_y, 
                               self.button_width, self.button_height, 
                               'Connect', menu_features['button_inactive'], 
                               self.font, menu_features['button_active'], 
                               menu_features['button_click_sound']),
            'online':Button(center_x,  center_y + self.button_height, 
                          self.button_width, self.button_height, 'Online game',
                          menu_features['button_inactive'], 
                          self.font, menu_features['button_active'], 
                          menu_features['button_click_sound']),
            'Yes':Button(center_x - self.button_width, center_y, self.button_width, 
                         self.button_height, 'Yes', 
                         menu_features['button_inactive'], self.font, 
                         menu_features['button_active'], 
                         menu_features['button_click_sound']),
            'No':Button(center_x + self.button_width, center_y, self.button_width, 
                        self.button_height, 'No', menu_features['button_inactive'], 
                        self.font, menu_features['button_active'], 
                        menu_features['button_click_sound']),
            'shoot_p1':Controls_button((settings_button_x
                                        - self.settings_button_width), 
                                       settings_button_y, 
                                       self.settings_button_width, 
                                       self.settings_button_height, 'space', 
                                       const.DEFAULT_PLAYER_ONE_SHOOT_BUTTON, 
                                       'shoot_p1', 
                                       menu_features['button_inactive'], 
                                       self.font, 
                                       menu_features['button_active'], 
                                       menu_features['button_click_sound']),
            'up_p1':Controls_button((settings_button_x
                                    - self.settings_button_width), 
                                    (settings_button_y
                                    + self.settings_button_height), 
                                    self.settings_button_width, 
                                    self.settings_button_height, 
                                    'w', const.DEFAULT_PLAYER_ONE_FORWARD_BUTTON, 
                                    'up_p1', 
                                    menu_features['button_inactive'], 
                                    self.font,
                                    menu_features['button_active'], 
                                    menu_features['button_click_sound']),
            'down_p1':Controls_button((settings_button_x
                                      - self.settings_button_width), 
                                      (settings_button_y 
                                      + 2*self.settings_button_height), 
                                      self.settings_button_width, 
                                      self.settings_button_height, 
                                      's', 
                                      const.DEFAULT_PLAYER_ONE_BACK_BUTTON, 
                                      'down_p1', 
                                      menu_features['button_inactive'],
                                      self.font, 
                                      menu_features['button_active'], 
                                      menu_features['button_click_sound']),
            'right_p1':Controls_button((settings_button_x 
                                       - self.settings_button_width), 
                                       (settings_button_y
                                       + 3*self.settings_button_height), 
                                       self.settings_button_width, 
                                       self.settings_button_height, 
                                       'd', 
                                       const.DEFAULT_PLAYER_ONE_RIGHT_BUTTON, 
                                       'right_p1', 
                                       menu_features['button_inactive'], 
                                       self.font,
                                       menu_features['button_active'], 
                                       menu_features['button_click_sound']),
            'left_p1':Controls_button((settings_button_x
                                      - self.settings_button_width), 
                                      (settings_button_y
                                      + 4*self.settings_button_height), 
                                      self.settings_button_width, 
                                      self.settings_button_height, 
                                      'a', 
                                      const.DEFAULT_PLAYER_ONE_LEFT_BUTTON, 
                                      'left_p1', 
                                      menu_features['button_inactive'], 
                                      self.font, 
                                      menu_features['button_active'], 
                                      menu_features['button_click_sound']),
            'shoot_p2':Controls_button((settings_button_x
                                       + self.settings_button_width), 
                                       settings_button_y, 
                                       self.settings_button_width, 
                                       self.settings_button_height, 'rctrl', 
                                       const.DEFAULT_PLAYER_TWO_SHOOT_BUTTON, 
                                       'shoot_p2', 
                                       menu_features['button_inactive'],
                                       self.font, 
                                       menu_features['button_active'], 
                                       menu_features['button_click_sound']),
            'up_p2':Controls_button((settings_button_x 
                                    + self.settings_button_width), 
                                    (settings_button_y 
                                    + self.settings_button_height), 
                                    self.settings_button_width, 
                                    self.settings_button_height, 
                                    'up', const.DEFAULT_PLAYER_TWO_FORWARD_BUTTON, 
                                    'up_p2', menu_features['button_inactive'], 
                                    self.font, 
                                    menu_features['button_active'], 
                                    menu_features['button_click_sound']),
            'down_p2':Controls_button((settings_button_x
                                      + self.settings_button_width), 
                                      (settings_button_y
                                      + 2*self.settings_button_height), 
                                      self.settings_button_width, 
                                      self.settings_button_height, 
                                      'down', 
                                      const.DEFAULT_PLAYER_TWO_BACK_BUTTON, 
                                      'down_p2', 
                                      menu_features['button_inactive'],
                                      self.font, 
                                      menu_features['button_active'], 
                                      menu_features['button_click_sound']),
            'right_p2':Controls_button((settings_button_x
                                       + self.settings_button_width), 
                                       (settings_button_y
                                       + 3*self.settings_button_height), 
                                       self.settings_button_width, 
                                       self.settings_button_height, 
                                       'right', 
                                       const.DEFAULT_PLAYER_TWO_RIGHT_BUTTON, 
                                       'right_p2', 
                                       menu_features['button_inactive'], 
                                       self.font, 
                                       menu_features['button_active'], 
                                       menu_features['button_click_sound']),
            'left_p2':Controls_button((settings_button_x
                                      + self.settings_button_width), 
                                      (settings_button_y 
                                      + 4*self.settings_button_height), 
                                      self.settings_button_width, 
                                      self.settings_button_height, 
                                      'left', 
                                      const.DEFAULT_PLAYER_TWO_LEFT_BUTTON, 
                                      'left_p2',
                                      menu_features['button_inactive'], 
                                      self.font, 
                                      menu_features['button_active'], 
                                      menu_features['button_click_sound']),
        }

default_font = './fonts/QuinqueFive.ttf'

screen_resolution = {
    '400 x 300': (400, 300),
    '800 x 600': (800, 600),
    '1280 x 720': (1280, 720) 
}

menu_features = {
    'button_inactive':'./images/button_inactive.png', 
    'button_active':'./images/button_active.png', 
    'menu_background':'./images/main_menu_background.jpg',
    'pause_background':'./images/game_background.png',
    'game_over_background':'./images/game_over_background.jpg',
    'settings_background':'./images/settings_background.jpg',
    'button_click_sound':'./sounds/button_click.ogg',
    'menu_music':'./sounds/menu_music.mp3',
    'game_music':'./sounds/game_music.wav'
}

health_bar = {
    0:'./images/health_bar/death_anim_1.png',
    1:'./images/health_bar/1.png',
    2:'./images/health_bar/2.png',
    3:'./images/health_bar/3.png',
    4:'./images/health_bar/4.png',
    5:'./images/health_bar/5.png',
    6:'./images/health_bar/6.png',
    7:'./images/health_bar/7.png',
    8:'./images/health_bar/8.png',
    9:'./images/health_bar/9.png',
    10:'./images/health_bar/10.png',
}