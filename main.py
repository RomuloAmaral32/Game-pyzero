# -*- coding: utf-8 -*-
import pygame
import pgzrun
import random
import math

# --- CONFIGURACOES PGZERO ---
WIDTH = 1200
HEIGHT = 600
TITLE = "SONIC JUMPER FINAL"
FPS = 30
GAME_SPEED = 8

# --- VARIAVEIS DE POSICAO E DIMENSAO FIXAS ---
ALTURA_SPRITE_PLAYER = 80
LARGURA_SPRITE_PLAYER = 80
ALTURA_CHAO = 30
GROUND_Y_POS = 480
PLATFORM_COLOR = (180, 80, 0)
MIN_PLATFORM_SPACING = 350

# --- VARIAVEIS GLOBAIS DE ESTADO E CONTROLE ---
scroll_speed = 0
score = 0
game_state = 'MENU'  # ESTADO INICIAL: MENU
is_audio_on = True  # Controle de audio

# Velocidade da animação de explosão (frames por troca)
explosion_frame_rate = 5

# Grupos de Sprites
player = None
player_group = None
ground_group = None
background_group = None
platform_group = None
coin_group = None
enemy_ground_group = None
enemy_air_group = None
ASSETS = {}  # Dicionário para armazenar imagens e sons carregados

# --- VARIAVEIS DE MENU E UI ---
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 60
BUTTON_Y_START = HEIGHT // 2 - 100
EXPLOSION_IMAGES = []  # Lista global para frames de explosão

# --- CLASSE PLATFORM ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, width, height, image_surface, is_explosive=False):
        super().__init__()
        self.image = pygame.transform.scale(image_surface, (width, height))
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)
        self.is_explosive = is_explosive

    def update(self):
        global scroll_speed
        if self.rect.right < 0:
            self.kill()
        self.rect.x -= scroll_speed


# --- CLASSE COIN ---
class Coin(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        if ASSETS.get('COIN_IMAGE'):
            try:
                self.image = pygame.transform.scale(ASSETS['COIN_IMAGE'], (30, 30))
            except Exception:
                surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                surf.fill((255, 215, 0))
                self.image = surf
        else:
            surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            surf.fill((255, 215, 0))
            self.image = surf
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)

    def update(self):
        global scroll_speed
        if self.rect.right < 0:
            self.kill()
        self.rect.x -= scroll_speed


# --- CLASSES DE INIMIGOS ---
class CorredorInimigo(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__()
        if ASSETS.get('CORREDOR_INIMIGO_IMAGE'):
            try:
                self.image = pygame.transform.scale(ASSETS['CORREDOR_INIMIGO_IMAGE'], (120, 120))
            except Exception:
                s = pygame.Surface((120, 120), pygame.SRCALPHA)
                s.fill((200, 0, 0))
                self.image = s
        else:
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            s.fill((200, 0, 0))
            self.image = s
        self.rect = self.image.get_rect(x=x_pos, y=GROUND_Y_POS - 120)
        self.speed = random.randint(3, 6)
        self.is_explosive = True

    def update(self):
        global scroll_speed
        self.rect.x -= (scroll_speed + self.speed)
        if self.rect.right < 0:
            self.kill()


class NaveInimiga(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        if ASSETS.get('NAVE_INIMIGA_IMAGE'):
            try:
                self.image = pygame.transform.scale(ASSETS['NAVE_INIMIGA_IMAGE'], (150, 100))
            except Exception:
                s = pygame.Surface((150, 100), pygame.SRCALPHA)
                s.fill((0, 0, 200))
                self.image = s
        else:
            s = pygame.Surface((150, 100), pygame.SRCALPHA)
            s.fill((0, 0, 200))
            self.image = s
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)
        self.speed = random.randint(4, 8)
        self.amplitude = random.randint(20, 50)
        self.freq = random.uniform(0.02, 0.05)
        self.initial_y = y_pos
        self.is_explosive = True

    def update(self):
        global scroll_speed
        self.rect.x -= (scroll_speed + self.speed)
        self.rect.y = self.initial_y + self.amplitude * math.sin(pygame.time.get_ticks() * self.freq)
        if self.rect.right < 0:
            self.kill()


# --- FUNCOES DE SPAWN ---
def spawn_platform():
    if 'platform_group' not in globals() or platform_group is None:
        return
    last_platform_right_edge = 0
    if platform_group.sprites():
        last_platform_right_edge = max(p.rect.right for p in platform_group.sprites())
    min_x_start = max(WIDTH, last_platform_right_edge + MIN_PLATFORM_SPACING)
    platform_width = random.randint(150, 300)
    platform_y = random.randint(GROUND_Y_POS - 250, GROUND_Y_POS - 100)
    new_platform_x = random.randint(min_x_start, min_x_start + 200)
    is_explosive_platform = random.random() < 0.3

    image_to_use = None
    if is_explosive_platform and ASSETS.get('PLATFORM_IMG_A'):
        image_to_use = ASSETS['PLATFORM_IMG_A']
    elif ASSETS.get('PLATFORM_IMG_B'):
        image_to_use = ASSETS['PLATFORM_IMG_B']
    else:
        solid_surface = pygame.Surface((platform_width, 20), pygame.SRCALPHA)
        solid_surface.fill(PLATFORM_COLOR)
        image_to_use = solid_surface

    if image_to_use:
        new_platform = Platform(x_pos=new_platform_x, y_pos=platform_y, width=platform_width, height=20,
                                image_surface=image_to_use, is_explosive=is_explosive_platform)
        platform_group.add(new_platform)

    if ASSETS.get('COIN_IMAGE') and random.random() < 0.7:
        num_coins = random.randint(2, 5)
        start_x = new_platform_x + 20
        for i in range(num_coins):
            coin_x = start_x + (i * 45)
            coin_y = platform_y - 40
            if coin_x < new_platform_x + platform_width - 30:
                coin_group.add(Coin(x_pos=coin_x, y_pos=coin_y))


def spawn_coins_on_ground():
    if not ASSETS.get('COIN_IMAGE') or 'coin_group' not in globals() or coin_group is None:
        return
    if random.random() < 0.5:
        num_coins = random.randint(3, 6)
        start_x = WIDTH + random.randint(50, 200)
        for i in range(num_coins):
            coin_x = start_x + (i * 45)
            coin_y = GROUND_Y_POS - 40
            coin_group.add(Coin(x_pos=coin_x, y_pos=coin_y))


def spawn_ground_enemy():
    if not ASSETS.get('CORREDOR_INIMIGO_IMAGE') or 'enemy_ground_group' not in globals() or enemy_ground_group is None:
        return
    if random.random() < 0.4:
        new_enemy = CorredorInimigo(x_pos=WIDTH + random.randint(50, 300))
        enemy_ground_group.add(new_enemy)


def spawn_air_enemy():
    if not ASSETS.get('NAVE_INIMIGA_IMAGE') or 'enemy_air_group' not in globals() or enemy_air_group is None:
        return
    if random.random() < 0.7:
        y_pos = random.randint(HEIGHT // 4, HEIGHT // 2)
        new_enemy = NaveInimiga(x_pos=WIDTH + random.randint(50, 500), y_pos=y_pos)
        enemy_air_group.add(new_enemy)


# --- CLASSE PLAYER ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        def _load_and_scale(filename):
            try:
                img = pygame.image.load(f"images/{filename}").convert_alpha()
                return pygame.transform.scale(img, (LARGURA_SPRITE_PLAYER, ALTURA_SPRITE_PLAYER))
            except Exception as e:
                s = pygame.Surface((LARGURA_SPRITE_PLAYER, ALTURA_SPRITE_PLAYER), pygame.SRCALPHA)
                s.fill((0, 0, 0, 0))
                return s

        self.idle = _load_and_scale("paradodir.png")
        self.run_right = _load_and_scale("correndodir.png")
        self.fly_right = _load_and_scale("semipulodir.png")
        self.fall_right = _load_and_scale("pulodir.png")
        self.land_right = _load_and_scale("pousodir.png")
        self.run_left = _load_and_scale("correndoesq.png")
        self.fly_left = _load_and_scale("semipuloesq.png")
        self.fall_left = _load_and_scale("puloesq.png")
        self.land_left = _load_and_scale("pousoesq.png")

        self.idle_right = self.idle
        self.idle_left = self.idle

        self.explosion_frames = [pygame.transform.scale(img, (LARGURA_SPRITE_PLAYER, ALTURA_SPRITE_PLAYER))
                                 for img in EXPLOSION_IMAGES]

        self.current_image = self.idle_right
        self.image = self.current_image
        self.rect = self.image.get_rect(x=100, y=GROUND_Y_POS - ALTURA_SPRITE_PLAYER)
        self.speed_y = 0
        self.gravity = 1
        self.on_ground = True
        self.facing_right = True
        self.is_jumping = False
        self.is_falling = False
        self.is_exploding = False
        self.explosion_frame = 0
        self.time_since_explosion_frame_change = 0

    def move_horizontal(self, all_terrain_sprites):
        global scroll_speed
        if self.is_exploding:
            return False
        old_x = self.rect.x
        moving_horizontally = False
        if keyboard.right:
            self.rect.x += GAME_SPEED
            self.facing_right = True
            moving_horizontally = True
            scroll_speed = GAME_SPEED
        elif keyboard.left:
            if self.rect.x > 100:
                self.rect.x -= GAME_SPEED
            self.facing_right = False
            moving_horizontally = True
            scroll_speed = 0
        else:
            scroll_speed = 0
        for sprite in all_terrain_sprites:
            if self.rect.colliderect(sprite.rect):
                self.rect.x = old_x
                break
        return moving_horizontally

    def check_boundaries(self):
        global scroll_speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            scroll_speed = 0

    def apply_gravity(self):
        if not self.is_exploding:
            self.rect.y += self.speed_y
            self.speed_y += self.gravity

    def jump_or_fly(self):
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
        global game_state
        if not self.is_exploding and self.explosion_frames:
            if ASSETS.get('EXPLOSION_SOUND') and is_audio_on:
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

    def update_explosion_animation(self):
        global explosion_frame_rate, game_state
        if self.is_exploding:
            self.time_since_explosion_frame_change += 1
            if self.time_since_explosion_frame_change >= explosion_frame_rate:
                self.time_since_explosion_frame_change = 0
                self.explosion_frame += 1
                if self.explosion_frame < len(self.explosion_frames):
                    self.image = self.explosion_frames[self.explosion_frame]
                else:
                    try:
                        self.kill()
                    except Exception:
                        pass
                    game_state = 'GAME_OVER'

    def update(self, all_terrain_sprites, all_enemy_sprites):
        if self.is_exploding:
            self.update_explosion_animation()
            return

        if pygame.sprite.spritecollide(self, all_enemy_sprites, False):
            self.start_explosion()
            return

        self.jump_or_fly()
        self.apply_gravity()
        self.check_vertical_collision(all_terrain_sprites)
        moving_horizontally = self.move_horizontal(all_terrain_sprites)
        self.check_boundaries()

        if self.on_ground:
            self.is_jumping = False
            self.is_falling = False
            if moving_horizontally:
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


# --- CLASSES AUXILIARES E SETUP ---
class Ground(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__()
        ground_w = WIDTH * 2
        self.image = pygame.Surface((ground_w, ALTURA_CHAO), pygame.SRCALPHA)
        self.image.fill((0, 100, 160, 0))
        self.rect = self.image.get_rect(x=x_pos, y=GROUND_Y_POS)
        self.is_explosive = False

    def update(self):
        global scroll_speed
        self.rect.x -= scroll_speed


class Background(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__()
        try:
            self.image = pygame.image.load("images/fundosonics.jpg").convert()
            self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        except Exception:
            self.image = pygame.Surface((WIDTH, HEIGHT))
            self.image.fill((135, 206, 235))
        self.rect = self.image.get_rect(x=x_pos, y=0)
        self.is_explosive = False

    def update(self):
        global scroll_speed
        self.rect.x -= scroll_speed


# --- FUNCOES DE CONTROLE DO JOGO ---
def load_assets():
    global EXPLOSION_IMAGES
    try:
        ASSETS['PLATFORM_IMG_A'] = pygame.image.load("images/plataformaexplo.png").convert_alpha()
        ASSETS['PLATFORM_IMG_B'] = pygame.image.load("images/plataformabem.png").convert_alpha()
        ASSETS['COIN_IMAGE'] = pygame.image.load("images/moeda3.png").convert_alpha()
        for i in range(1, 4):
            EXPLOSION_IMAGES.append(pygame.image.load(f"images/explo{i}.png").convert_alpha())
        ASSETS['NAVE_INIMIGA_IMAGE'] = pygame.image.load("images/naveinimiga.png").convert_alpha()
        ASSETS['CORREDOR_INIMIGO_IMAGE'] = pygame.image.load("images/corredorinimigo.png").convert_alpha()
        ASSETS['GAME_OVER_IMAGE'] = pygame.image.load("images/imagemderrota.png").convert_alpha()

        ASSETS['MUSIC_FILE'] = 'sounds/sonic_bgm.mp3'

        try:
            pygame.mixer.init()
            try:
                ASSETS['COIN_SOUND'] = pygame.mixer.Sound('sounds/coin_sfx.mp3')
            except Exception:
                ASSETS['COIN_SOUND'] = None
            try:
                ASSETS['EXPLOSION_SOUND'] = pygame.mixer.Sound('sounds/explosion_sfx.mp3')
            except Exception:
                ASSETS['EXPLOSION_SOUND'] = None
        except Exception:
            ASSETS['COIN_SOUND'] = None
            ASSETS['EXPLOSION_SOUND'] = None
    except Exception as e:
        print("erro ao carregar assets", e)
        ASSETS.setdefault('PLATFORM_IMG_A', None)
        ASSETS.setdefault('PLATFORM_IMG_B', None)
        ASSETS.setdefault('COIN_IMAGE', None)
        ASSETS.setdefault('NAVE_INIMIGA_IMAGE', None)
        ASSETS.setdefault('CORREDOR_INIMIGO_IMAGE', None)
        ASSETS.setdefault('GAME_OVER_IMAGE', None)
        ASSETS.setdefault('COIN_SOUND', None)
        ASSETS.setdefault('EXPLOSION_SOUND', None)
        ASSETS.setdefault('MUSIC_FILE', None)


def _start_music_if_enabled():
    if not is_audio_on:
        try: pygame.mixer.music.stop()
        except: pass
        return
    music_file = ASSETS.get('MUSIC_FILE')
    if not music_file:
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
    except:
        pass


def start_game():
    global player, player_group, ground_group, background_group, platform_group, coin_group, score, game_state, scroll_speed, enemy_ground_group, enemy_air_group

    score = 0
    game_state = 'RUNNING'
    scroll_speed = 0

    player_group = pygame.sprite.Group()
    ground_group = pygame.sprite.Group()
    background_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()
    enemy_ground_group = pygame.sprite.Group()
    enemy_air_group = pygame.sprite.Group()

    player = Player()
    player_group.add(player)

    ground1 = Ground(0)
    ground2 = Ground(ground1.rect.width)
    ground_group.add(ground1, ground2)

    bg1 = Background(0)
    bg2 = Background(WIDTH)
    background_group.add(bg1, bg2)

    try:
        clock.unschedule(spawn_platform)
        clock.unschedule(spawn_coins_on_ground)
        clock.unschedule(spawn_ground_enemy)
        clock.unschedule(spawn_air_enemy)
    except:
        pass

    clock.schedule_interval(spawn_platform, 2.0)
    clock.schedule_interval(spawn_coins_on_ground, 1.2)
    clock.schedule_interval(spawn_ground_enemy, 2.5)
    clock.schedule_interval(spawn_air_enemy, 4.0)

    image_for_first_platform = ASSETS.get('PLATFORM_IMG_A')
    if not image_for_first_platform:
        image_for_first_platform = pygame.Surface((200, 20), pygame.SRCALPHA)
        image_for_first_platform.fill(PLATFORM_COLOR)

    platform_group.add(
        Platform(WIDTH, GROUND_Y_POS - 150, 200, 20, image_for_first_platform)
    )

    _start_music_if_enabled()


def on_key_down(key):
    global game_state
    if game_state == 'GAME_OVER' and key == pygame.K_RETURN:
        start_game()


load_assets()

def off_screen(sprite):
    return sprite.rect.right < 0


# MENU CLICK
def on_mouse_down(pos):
    global game_state, is_audio_on

    if game_state != 'MENU':
        return

    x, y = pos

    # começar
    if 400 < x < 800 and BUTTON_Y_START < y < BUTTON_Y_START + BUTTON_HEIGHT:
        start_game()
        return

    # musica
    if 400 < x < 800 and BUTTON_Y_START + 80 < y < BUTTON_Y_START + 140:
        is_audio_on = not is_audio_on
        if is_audio_on:
            _start_music_if_enabled()
            if ASSETS.get('COIN_SOUND'):
                ASSETS['COIN_SOUND'].set_volume(1.0)
            if ASSETS.get('EXPLOSION_SOUND'):
                ASSETS['EXPLOSION_SOUND'].set_volume(1.0)
        else:
            try: pygame.mixer.music.stop()
            except: pass
            if ASSETS.get('COIN_SOUND'):
                ASSETS['COIN_SOUND'].set_volume(0.0)
            if ASSETS.get('EXPLOSION_SOUND'):
                ASSETS['EXPLOSION_SOUND'].set_volume(0.0)
        return

    # sair
    if 400 < x < 800 and BUTTON_Y_START + 160 < y < BUTTON_Y_START + 220:
        try: pygame.mixer.music.stop()
        except: pass
        pygame.quit()
        exit()


def update():
    global scroll_speed, score, game_state

    if game_state == 'MENU':
        return

    if game_state == 'GAME_OVER':
        scroll_speed = 0
        return

    if not player_group:
        return

    all_terrain = ground_group.sprites() + platform_group.sprites()
    all_enemies = enemy_ground_group.sprites() + enemy_air_group.sprites()

    player_group.update(all_terrain, all_enemies)

    coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
    if coins_collected and ASSETS.get('COIN_SOUND') and is_audio_on:
        ASSETS['COIN_SOUND'].play()
    score += len(coins_collected)

    ground_group.update()
    background_group.update()
    platform_group.update()
    coin_group.update()
    enemy_ground_group.update()
    enemy_air_group.update()

    if scroll_speed > 0:
        if background_group.sprites() and off_screen(background_group.sprites()[0]):
            background_group.remove(background_group.sprites()[0])
            last_bg = background_group.sprites()[-1]
            background_group.add(Background(last_bg.rect.right))

        if ground_group.sprites() and off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])
            last_ground = ground_group.sprites()[-1]
            ground_group.add(Ground(last_ground.rect.right))


def draw():

    if game_state == 'MENU':
        screen.fill((0, 0, 50))
        screen.draw.text("SONIC JUMPER", (WIDTH // 2, BUTTON_Y_START - 100),
                         color='yellow', fontsize=100, anchor=(0.5, 0.5))

        buttons = [
            "COMEÇAR O JOGO",
            "MÚSICA E SONS: " + ("LIGADO" if is_audio_on else "DESLIGADO"),
            "SAÍDA"
        ]

        for i, text in enumerate(buttons):
            y_pos = BUTTON_Y_START + (i * 80)
            rect = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, y_pos,
                               BUTTON_WIDTH, BUTTON_HEIGHT)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            button_color = (60, 60, 60) if rect.collidepoint(mouse_x, mouse_y) else (30, 30, 30)

            screen.draw.filled_rect(rect, button_color)
            screen.draw.rect(rect, (200, 200, 200))
            screen.draw.text(text, rect.center,
                             color='white', fontsize=30, anchor=(0.5, 0.5))
        return

    if background_group:
        background_group.draw(screen.surface)
    if platform_group:
        platform_group.draw(screen.surface)
    if coin_group:
        coin_group.draw(screen.surface)
    if enemy_ground_group:
        enemy_ground_group.draw(screen.surface)
    if enemy_air_group:
        enemy_air_group.draw(screen.surface)
    if ground_group:
        ground_group.draw(screen.surface)

    if player_group:
        player_group.draw(screen.surface)

    screen.draw.text(f"SCORE: {score}", (20, 20), color='white', fontsize=40)

    if game_state == 'GAME_OVER':
        if ASSETS.get('GAME_OVER_IMAGE'):
            try:
                screen.surface.blit(ASSETS['GAME_OVER_IMAGE'], (0, 0))
            except:
                screen.draw.filled_rect(pygame.Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0))
        else:
            screen.draw.filled_rect(pygame.Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0, 180))

        screen.draw.text("VOCE PERDEU!", (WIDTH // 2, HEIGHT // 2 - 50),
                         color='red', fontsize=100, anchor=(0.5, 0.5))
        screen.draw.text("APERTE ENTER PARA JOGAR NOVAMENTE",
                         (WIDTH // 2, HEIGHT // 2 + 50),
                         color='white', fontsize=50, anchor=(0.5, 0.5))


pgzrun.go()
