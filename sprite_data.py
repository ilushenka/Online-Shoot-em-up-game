from dataclasses import dataclass

@dataclass
class Sprites_data:
    name: str = None
    x: int = None
    y: int = None

@dataclass
class Mobs_data(Sprites_data):
    direction: str = 'forward'
    sounds: list = None

@dataclass
class Effects_data(Sprites_data):
    anim_num: int = None

@dataclass
class Player_data(Mobs_data):
    health: int = None
    is_invincible: bool = False
    anim_num: int = None
    player_num: int = None

def set_sprites_data(players, players_group, mobs, 
                     mob_bullets, bonuses, effects, states):
    res = []
    for mob in mobs:
        res.append(Mobs_data('Mob', mob.rect.x, mob.rect.y, 
                             mob.direction, mob.sounds))
    for bullet in mob_bullets:
        res.append(Sprites_data('Mob_bullet', bullet.rect.x, bullet.rect.y))
    for bonus in bonuses:
        res.append(Effects_data(bonus.bonus_name, bonus.rect.x, bonus.rect.y,
                                bonus.current_animation))
    for effect in effects:
        res.append(Effects_data('Effect', effect.rect.x, effect.rect.y, 
                                effect.current_animation))
    for player in players_group:
        for bullet in player.bullets:
            res.append(Mobs_data('Player_bullet', bullet.rect.x, 
                                 bullet.rect.y, bullet.angle))
    for num, player in enumerate(players):
        if player.features.health > 0 and states[num] != 'Disconnected':        
            res.append(Player_data('Player', player.rect.x, player.rect.y, 
                                    player.direction, player.sounds, 
                                    player.features.health, 
                                    player.is_invincible, 
                                    player.invincible_animation, num))

    return res

