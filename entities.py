# entities.py
import pygame
import random
import math
import os
from config import *

# Este dicionário será preenchido por game_manager.load_assets()
ASSETS = {}

# --- FUNÇÕES AUXILIARES ---
def safe_scale(surface, size, fallback_color=(255, 0, 255, 128)):
    """Tenta escalar um Surface; se None, cria fallback Surface."""
    if surface and isinstance(surface, pygame.Surface):
        try:
            return pygame.transform.scale(surface, size)
        except Exception:
            pass
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf

def try_load_image_from_images_folder(filename):
    """Tenta carregar images/<filename> e retorna Surface ou None."""
    try:
        path = os.path.join("images", filename)
        surf = pygame.image.load(path).convert_alpha()
        return surf
    except Exception:
        return None

# --- ENTIDADES ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, width, height, image_surface=None, is_explosive=False):
        super().__init__()
        self.image = safe_scale(image_surface, (width, height), fallback_color=(180, 80, 0, 255))
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)
        self.is_explosive = is_explosive

    def update(self, scroll_speed=0):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        coin_img = ASSETS.get('COIN_IMAGE') or try_load_image_from_images_folder(ASSET_PATHS.get('COIN_IMG', 'moeda3.png'))
        self.image = safe_scale(coin_img, (30, 30), fallback_color=(255, 215, 0, 255))
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)

    def update(self, scroll_speed=0):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class CorredorInimigo(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__()
        img = ASSETS.get('CORREDOR_INIMIGO_IMAGE') or try_load_image_from_images_folder(ASSET_PATHS.get('CORREDOR_IMG', 'corredorinimigo.png'))
        self.image = safe_scale(img, (120, 120), fallback_color=(200, 0, 0, 255))
        self.rect = self.image.get_rect(x=x_pos, y=GROUND_Y_POS - 120)
        self.speed = random.randint(3, 6)
        self.is_explosive = True

    def update(self, scroll_speed=0):
        self.rect.x -= (scroll_speed + self.speed)
        if self.rect.right < 0:
            self.kill()

class NaveInimiga(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        img = ASSETS.get('NAVE_INIMIGA_IMAGE') or try_load_image_from_images_folder(ASSET_PATHS.get('NAVE_IMG', 'naveinimiga.png'))
        self.image = safe_scale(img, (150, 100), fallback_color=(0, 0, 200, 255))
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)
        self.speed = random.randint(4, 8)
        self.amplitude = random.randint(20, 50)
        self.freq = random.uniform(0.02, 0.05)
        self.initial_y = y_pos
        self.is_explosive = True

    def update(self, scroll_speed=0):
        self.rect.x -= (scroll_speed + self.speed)
        # movimento senoidal (convertendo pra int)
        self.rect.y = int(self.initial_y + self.amplitude * math.sin(pygame.time.get_ticks() * self.freq))
        if self.rect.right < 0:
            self.kill()

class Ground(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__()
        ground_w = WIDTH * 2
        self.image = pygame.Surface((ground_w, GROUND_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(x=x_pos, y=GROUND_Y_POS)
        self.is_explosive = False

    def update(self, scroll_speed=0):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Background(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__()
        bg_img = ASSETS.get('BACKGROUND_IMAGE') or try_load_image_from_images_folder(os.path.basename(ASSET_PATHS.get('FUNDOSONICS_IMG', 'fundosonics.jpg')))
        if bg_img:
            self.image = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        else:
            self.image = pygame.Surface((WIDTH, HEIGHT))
            self.image.fill((135, 206, 235))
        self.rect = self.image.get_rect(x=x_pos, y=0)
        self.is_explosive = False

    def update(self, scroll_speed=0):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        def _load_or_asset(key, fallback_filename):
            # tenta ASSETS (Surface) -> tenta arquivo images/<fallback_filename> -> cria Surface vazia
            surf = ASSETS.get(key)
            if isinstance(surf, pygame.Surface):
                return safe_scale(surf, (PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), fallback_color=(0,0,0,0))
            loaded = try_load_image_from_images_folder(fallback_filename)
            if loaded:
                return pygame.transform.scale(loaded, (PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT))
            s = pygame.Surface((PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), pygame.SRCALPHA)
            return s

        self.idle_right = _load_or_asset('IDLE_RIGHT', ASSET_PATHS.get('IDLE_RIGHT', 'paradodir.png'))
        self.run_right = _load_or_asset('RUN_RIGHT', ASSET_PATHS.get('RUN_RIGHT', 'correndodir.png'))
        self.fly_right = _load_or_asset('FLY_RIGHT', ASSET_PATHS.get('FLY_RIGHT', 'semipulodir.png'))
        self.fall_right = _load_or_asset('FALL_RIGHT', ASSET_PATHS.get('FALL_RIGHT', 'pulodir.png'))
        self.land_right = _load_or_asset('LAND_RIGHT', ASSET_PATHS.get('LAND_RIGHT', 'pousodir.png'))
        self.run_left = _load_or_asset('RUN_LEFT', ASSET_PATHS.get('RUN_LEFT', 'correndoesq.png'))
        self.fly_left = _load_or_asset('FLY_LEFT', ASSET_PATHS.get('FLY_LEFT', 'semipuloesq.png'))
        self.fall_left = _load_or_asset('FALL_LEFT', ASSET_PATHS.get('FALL_LEFT', 'puloesq.png'))
        self.land_left = _load_or_asset('LAND_LEFT', ASSET_PATHS.get('LAND_LEFT', 'pousoesq.png'))

        # idle left fallback
        try:
            self.idle_left = _load_or_asset('IDLE_LEFT_FALLBACK', ASSET_PATHS.get('IDLE_LEFT_FALLBACK', 'paradoesq.png'))
        except Exception:
            self.idle_left = pygame.transform.flip(self.idle_right, True, False)

        # explosão: ASSETS['EXPLOSION_IMAGES'] deve ser lista de Surfaces carregadas
        raw_explo = ASSETS.get('EXPLOSION_IMAGES') or []
        self.explosion_frames = [safe_scale(img, (PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)) for img in raw_explo]

        # estado inicial
        self.current_image = self.idle_right
        self.image = self.current_image
        self.rect = self.image.get_rect(x=100, y=GROUND_Y_POS - PLAYER_SPRITE_HEIGHT)

        # física
        self.speed_y = 0
        self.gravity = 1
        self.on_ground = True
        self.facing_right = True
        self.is_jumping = False
        self.is_falling = False

        # explosão
        self.is_exploding = False
        self.explosion_frame = 0
        self.time_since_explosion_frame_change = 0

    def move_horizontal(self, keyboard, all_terrain_sprites, manager):
        """Retorna True se moveu horizontalmente. Ajusta manager.scroll_speed quando mover para a direita."""
        if self.is_exploding:
            return False
        old_x = self.rect.x
        moving_horizontally = False

        if keyboard.right:
            self.rect.x += GAME_SPEED
            self.facing_right = True
            moving_horizontally = True
            manager.scroll_speed = GAME_SPEED
        elif keyboard.left:
            if self.rect.x > 100:
                self.rect.x -= GAME_SPEED
            self.facing_right = False
            moving_horizontally = True
            manager.scroll_speed = 0
        else:
            manager.scroll_speed = 0

        for sprite in all_terrain_sprites:
            if self.rect.colliderect(sprite.rect):
                self.rect.x = old_x
                break
        return moving_horizontally

    def check_boundaries(self, manager):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            manager.scroll_speed = 0

    def apply_gravity(self):
        if not self.is_exploding:
            self.rect.y += self.speed_y
            self.speed_y += self.gravity

    def jump_or_fly(self, keyboard):
        if self.is_exploding:
            return
        if keyboard.space and self.on_ground:
            self.speed_y = -18
            self.on_ground = False
            self.is_jumping = True
            self.is_falling = False

    def check_ground_sensor(self, all_terrain_sprites):
        sensor_rect = self.rect.copy()
        sensor_rect.y = self.rect.bottom
        sensor_rect.height = 1
        for sprite in all_terrain_sprites:
            if sensor_rect.colliderect(sprite.rect):
                return True
        return False

    def check_vertical_collision(self, all_terrain_sprites):
        if self.is_exploding:
            return
        on_ground_this_frame = self.check_ground_sensor(all_terrain_sprites)

        if on_ground_this_frame and self.speed_y >= 0:
            collisions = pygame.sprite.spritecollide(self, all_terrain_sprites, False)
            if collisions:
                platform_to_land_on = min(collisions, key=lambda x: x.rect.top)
                if getattr(platform_to_land_on, 'is_explosive', False):
                    self.start_explosion()
                    return
                if self.rect.bottom > platform_to_land_on.rect.top:
                    self.rect.bottom = platform_to_land_on.rect.top
            self.speed_y = 0
            self.on_ground = True
            return

        if self.speed_y < 0:
            collisions = pygame.sprite.spritecollide(self, all_terrain_sprites, False)
            if collisions:
                if getattr(collisions[0], 'is_explosive', False):
                    self.start_explosion()
                    return
                self.speed_y = 0
                self.on_ground = False
                return

        if not on_ground_this_frame and self.rect.bottom < GROUND_Y_POS:
            self.on_ground = False
        elif self.rect.bottom >= GROUND_Y_POS:
            self.rect.bottom = GROUND_Y_POS
            self.speed_y = 0
            self.on_ground = True

    def start_explosion(self):
        if not self.is_exploding and self.explosion_frames:
            if ASSETS.get('EXPLOSION_SOUND'):
                try:
                    ASSETS['EXPLOSION_SOUND'].play()
                except Exception:
                    pass
            self.is_exploding = True
            self.explosion_frame = 0
            self.image = self.explosion_frames[0]
            self.speed_y = 0
            self.on_ground = False
            self.time_since_explosion_frame_change = 0

    def update_explosion_animation(self, manager):
        if self.is_exploding:
            self.time_since_explosion_frame_change += 1
            if self.time_since_explosion_frame_change >= EXPLOSION_FRAME_RATE:
                self.time_since_explosion_frame_change = 0
                self.explosion_frame += 1
                if self.explosion_frame < len(self.explosion_frames):
                    self.image = self.explosion_frames[self.explosion_frame]
                else:
                    try:
                        self.kill()
                    except Exception:
                        pass
                    manager.game_state = 'GAME_OVER'

    def update(self, keyboard, all_terrain_sprites, all_enemy_sprites, manager):
        # explosão
        if self.is_exploding:
            self.update_explosion_animation(manager)
            return

        # colisão com inimigos
        if pygame.sprite.spritecollide(self, all_enemy_sprites, False):
            self.start_explosion()
            return

        # movimento
        self.jump_or_fly(keyboard)
        self.apply_gravity()
        self.check_vertical_collision(all_terrain_sprites)
        moving_h = self.move_horizontal(keyboard, all_terrain_sprites, manager)
        self.check_boundaries(manager)

        # animação atual
        if self.on_ground:
            self.is_jumping = False
            self.is_falling = False
            if moving_h:
                self.current_image = self.run_right if self.facing_right else self.run_left
            else:
                self.current_image = self.idle_right if self.facing_right else self.idle_left
        else:
            if self.speed_y < 0:
                self.is_jumping = True
                self.is_falling = False
                self.current_image = self.fly_right if self.facing_right else self.fly_left
            else:
                self.is_falling = True
                self.is_jumping = False
                self.current_image = self.fall_right if self.facing_right else self.fall_left

        self.image = self.current_image
