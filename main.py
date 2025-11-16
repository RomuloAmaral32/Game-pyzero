# -*- coding: utf-8 -*-
import pygame 
import pgzrun 
import random 
import math 

# --- CONFIGURACOES PGZERO ---
WIDTH = 1200
HEIGHT = 600
TITLE = "SONIC ESTAVEL FINALISSIMO COM COLISAO CORRIGIDA"
FPS = 30 
GAME_SPEED = 8  

# --- VARIAVEIS DE POSICAO E DIMENSAO FIXAS ---
ALTURA_SPRITE_PLAYER = 80  
LARGURA_SPRITE_PLAYER = 80 
ALTURA_CHAO = 30 
GROUND_Y_POS = 480 
PLATFORM_COLOR = (180, 80, 0) 
MIN_PLATFORM_SPACING = 350 

# --- VARIAVEIS GLOBAIS DE CONTROLE E IMAGENS ---
scroll_speed = 0
score = 0
game_state = 'RUNNING'
PLATFORM_IMG_A = None 
PLATFORM_IMG_B = None
COIN_IMAGE = None 
EXPLOSION_IMAGES = []
explosion_frame_rate = 5 
player = None
player_group = None
ground_group = None
background_group = None
platform_group = None
coin_group = None
enemy_ground_group = None
enemy_air_group = None    
NAVE_INIMIGA_IMAGE = None
CORREDOR_INIMIGO_IMAGE = None
COIN_SOUND = None
EXPLOSION_SOUND = None

# --- CLASSE PLATFORM ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, width, height, image_surface, is_explosive=False):
        super().__init__()
        
        self.image = pygame.transform.scale(image_surface, (width, height))
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)
        self.is_explosive = is_explosive

    def update(self):
        global scroll_speed
        if self.rect.right < 0: self.kill() 
        self.rect.x -= scroll_speed 

# --- CLASSE COIN ---
class Coin(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        
        self.image = pygame.transform.scale(COIN_IMAGE, (30, 30))
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)

    def update(self):
        global scroll_speed
        if self.rect.right < 0: self.kill() 
        self.rect.x -= scroll_speed

# --- CLASSES DE INIMIGOS ---
class CorredorInimigo(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__()
        self.image = pygame.transform.scale(CORREDOR_INIMIGO_IMAGE, (120, 120)) 
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
        self.image = pygame.transform.scale(NAVE_INIMIGA_IMAGE, (150, 100)) 
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)
        self.speed = random.randint(4, 8) 
        self.amplitude = random.randint(20, 50)
        self.freq = random.uniform(0.02, 0.05)
        self.initial_y = y_pos
        self.is_explosive = True

    def update(self):
        global scroll_speed
        self.rect.x -= (scroll_speed + self.speed) 
        # CORRIGIDO: Usando math.sin do módulo 'math'
        self.rect.y = self.initial_y + self.amplitude * math.sin(pygame.time.get_ticks() * self.freq)
        if self.rect.right < 0:
            self.kill() 
# --- FIM CLASSES DE INIMIGOS ---


# --- FUNCOES DE SPAWN ---
def spawn_platform():
    if 'platform_group' not in globals() or platform_group is None: return
    last_platform_right_edge = 0
    if platform_group.sprites(): last_platform_right_edge = max(p.rect.right for p in platform_group.sprites())
    min_x_start = max(WIDTH, last_platform_right_edge + MIN_PLATFORM_SPACING)
    platform_width = random.randint(150, 300) 
    platform_y = random.randint(GROUND_Y_POS - 250, GROUND_Y_POS - 100)
    new_platform_x = random.randint(min_x_start, min_x_start + 200)

    is_explosive_platform = random.random() < 0.3
    
    if is_explosive_platform and PLATFORM_IMG_A: image_to_use = PLATFORM_IMG_A
    elif PLATFORM_IMG_B: image_to_use = PLATFORM_IMG_B
    else:
        solid_surface = pygame.Surface((platform_width, 20), pygame.SRCALPHA); solid_surface.fill(PLATFORM_COLOR); image_to_use = solid_surface

    new_platform = Platform(x_pos=new_platform_x, y_pos=platform_y, width=platform_width, height=20, image_surface=image_to_use, is_explosive=is_explosive_platform)
                            
    platform_group.add(new_platform)

    if COIN_IMAGE and random.random() < 0.7: 
        num_coins = random.randint(2, 5); gap_between_coins = platform_width // num_coins if num_coins > 0 else 0; start_x = new_platform_x + 20 
        for i in range(num_coins):
            coin_x = start_x + (i * 45); coin_y = platform_y - 40 
            if coin_x < new_platform_x + platform_width - 30: coin_group.add(Coin(x_pos=coin_x, y_pos=coin_y))

def spawn_coins_on_ground():
    if not COIN_IMAGE or 'coin_group' not in globals() or coin_group is None: return

    if random.random() < 0.5: 
        num_coins = random.randint(3, 6); coin_y = GROUND_Y_POS - 40; start_x = WIDTH + random.randint(50, 200) 
        for i in range(num_coins):
            coin_x = start_x + (i * 45); coin_y = GROUND_Y_POS - 40 
            coin_group.add(Coin(x_pos=coin_x, y_pos=coin_y))

def spawn_ground_enemy():
    if not CORREDOR_INIMIGO_IMAGE or 'enemy_ground_group' not in globals() or enemy_ground_group is None: return
    if random.random() < 0.4: 
        new_enemy = CorredorInimigo(x_pos=WIDTH + random.randint(50, 300))
        enemy_ground_group.add(new_enemy)

def spawn_air_enemy():
    # CHECAGEM CRITICA: Se a imagem nao carregou, nao tente criar o inimigo.
    if not NAVE_INIMIGA_IMAGE or 'enemy_air_group' not in globals() or enemy_air_group is None: return
    
    # Aumentado para 70% de chance de spawn
    if random.random() < 0.7: 
        y_pos = random.randint(HEIGHT // 4, HEIGHT // 2) 
        new_enemy = NaveInimiga(x_pos=WIDTH + random.randint(50, 500), y_pos=y_pos)
        enemy_air_group.add(new_enemy)
# --- FIM FUNCOES DE SPAWN ---


# --- CLASSE PLAYER ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        def _load_and_scale(filename):
            try:
                img = pygame.image.load(f"images/{filename}").convert_alpha()
                return pygame.transform.scale(img, (LARGURA_SPRITE_PLAYER, ALTURA_SPRITE_PLAYER))
            except pygame.error as e:
                print(f"ERROR: Nao foi possivel carregar {filename}. Detalhes: {e}")
                fail_surface = pygame.Surface((LARGURA_SPRITE_PLAYER, ALTURA_SPRITE_PLAYER)); fail_surface.fill((255, 0, 0)); return fail_surface

        self.idle_right = _load_and_scale("paradodir.png"); self.run_right = _load_and_scale("correndodir.png"); self.fly_right = _load_and_scale("semipulodir.png"); self.fall_right = _load_and_scale("pulodir.png"); self.land_right = _load_and_scale("pousodir.png"); self.run_left = _load_and_scale("correndoesq.png"); self.fly_left = _load_and_scale("semipuloesq.png"); self.fall_left = _load_and_scale("puloesq.png"); self.land_left = _load_and_scale("pousoesq.png")
        try: self.idle_left = _load_and_scale("paradoesq.png")
        except: self.idle_left = pygame.transform.flip(self.idle_right, True, False)

        self.explosion_frames = [pygame.transform.scale(img, (LARGURA_SPRITE_PLAYER, ALTURA_SPRITE_PLAYER)) for img in EXPLOSION_IMAGES]

        self.current_image = self.idle_right; self.image = self.current_image; self.rect = self.image.get_rect(x=100, y=GROUND_Y_POS - ALTURA_SPRITE_PLAYER) 
        self.speed_y = 0; self.gravity = 1; self.on_ground = True; self.facing_right = True; self.is_jumping = False; self.is_falling = False
        self.is_exploding = False; self.explosion_frame = 0; self.time_since_explosion_frame_change = 0

    def move_horizontal(self, all_terrain_sprites):
        global scroll_speed
        if self.is_exploding: return False 
        old_x = self.rect.x; moving_horizontally = False
        if keyboard.right:
            self.rect.x += GAME_SPEED; self.facing_right = True; moving_horizontally = True; scroll_speed = GAME_SPEED
        elif keyboard.left:
            if self.rect.x > 100: self.rect.x -= GAME_SPEED
            self.facing_right = False; moving_horizontally = True; scroll_speed = 0 
        else:
            scroll_speed = 0 
        for sprite in all_terrain_sprites:
            if self.rect.colliderect(sprite.rect): self.rect.x = old_x; break 
        return moving_horizontally
    
    def check_boundaries(self):
        global scroll_speed
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH; scroll_speed = 0 

    def apply_gravity(self):
        if not self.is_exploding: self.rect.y += self.speed_y; self.speed_y += self.gravity

    def jump_or_fly(self):
        if self.is_exploding: return
        if keyboard.space and self.on_ground: 
            self.speed_y = -18; self.on_ground = False; self.is_jumping = True; self.is_falling = False
        
    def check_ground_sensor(self, all_terrain_sprites):
        sensor_rect = self.rect.copy(); sensor_rect.y = self.rect.bottom; sensor_rect.height = 1 
        for sprite in all_terrain_sprites:
            if sensor_rect.colliderect(sprite.rect): return True
        return False

    def check_vertical_collision(self, all_terrain_sprites):
        if self.is_exploding: return
        on_ground_this_frame = self.check_ground_sensor(all_terrain_sprites)
        
        if on_ground_this_frame and self.speed_y >= 0:
            collisions = pygame.sprite.spritecollide(self, all_terrain_sprites, False)
            if collisions:
                platform_to_land_on = min(collisions, key=lambda x: x.rect.top)
                
                if platform_to_land_on.is_explosive:
                    self.start_explosion()
                    return

                if self.rect.bottom > platform_to_land_on.rect.top:
                    self.rect.bottom = platform_to_land_on.rect.top
            
            self.speed_y = 0; self.on_ground = True; return
        
        if self.speed_y < 0: 
            collisions = pygame.sprite.spritecollide(self, all_terrain_sprites, False)
            if collisions:
                if collisions[0].is_explosive:
                    self.start_explosion()
                    return
                self.speed_y = 0; self.on_ground = False; return 

        if not on_ground_this_frame and self.rect.bottom < GROUND_Y_POS:
            self.on_ground = False
        elif self.rect.bottom >= GROUND_Y_POS:
            self.rect.bottom = GROUND_Y_POS; self.speed_y = 0; self.on_ground = True

    def start_explosion(self):
        global game_state
        if not self.is_exploding and self.explosion_frames:
            if EXPLOSION_SOUND: EXPLOSION_SOUND.play() 
            self.is_exploding = True; self.explosion_frame = 0; self.image = self.explosion_frames[0] 
            self.speed_y = 0; self.on_ground = False; self.time_since_explosion_frame_change = 0

    def update_explosion_animation(self):
        global explosion_frame_rate, game_state
        if self.is_exploding:
            self.time_since_explosion_frame_change += 1
            if self.time_since_explosion_frame_change >= explosion_frame_rate:
                self.time_since_explosion_frame_change = 0; self.explosion_frame += 1
                if self.explosion_frame < len(self.explosion_frames):
                    self.image = self.explosion_frames[self.explosion_frame]
                else:
                    self.kill()
                    game_state = 'GAME_OVER'

    def update(self, all_terrain_sprites, all_enemy_sprites): 
        if self.is_exploding:
            self.update_explosion_animation()
            return

        # Checa colisão com inimigos (morte)
        if pygame.sprite.spritecollide(self, all_enemy_sprites, False):
            self.start_explosion()
            return

        self.jump_or_fly(); self.apply_gravity(); self.check_vertical_collision(all_terrain_sprites); moving_horizontally = self.move_horizontal(all_terrain_sprites); self.check_boundaries()
        
        if self.on_ground:
            self.is_jumping = False; self.is_falling = False
            if moving_horizontally:
                self.current_image = self.run_right if self.facing_right else self.run_left
            else:
                self.current_image = self.idle_right if self.facing_right else self.idle_left
        else:
            if self.speed_y < 0: self.is_jumping = True; self.is_falling = False; self.current_image = self.fly_right if self.facing_right else self.fly_left
            else: self.is_falling = True; self.is_jumping = False; self.current_image = self.fall_right if self.facing_right else self.fall_left

        self.image = self.current_image

# --- CLASSES AUXILIARES E SETUP ---
class Ground(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__(); ground_w = WIDTH * 2; self.image = pygame.Surface((ground_w, ALTURA_CHAO), pygame.SRCALPHA); self.image.fill((0, 100, 160, 0)); self.rect = self.image.get_rect(x=x_pos, y=GROUND_Y_POS); self.is_explosive = False
    def update(self):
        global scroll_speed; self.rect.x -= scroll_speed
        
class Background(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__(); 
        try: self.image = pygame.image.load("images/fundosonics.jpg").convert(); self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        except pygame.error as e: self.image = pygame.Surface((WIDTH, HEIGHT)); self.image.fill((135, 206, 235)); self.is_explosive = False
        self.rect = self.image.get_rect(x=x_pos, y=0); self.is_explosive = False
    def update(self):
        global scroll_speed; self.rect.x -= scroll_speed 

class CorredorInimigo(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__()
        self.image = pygame.transform.scale(CORREDOR_INIMIGO_IMAGE, (120, 120)) 
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
        self.image = pygame.transform.scale(NAVE_INIMIGA_IMAGE, (150, 100)) 
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
        
# --- FUNCOES DE CONTROLE DO JOGO ---
def load_assets():
    global PLATFORM_IMG_A, PLATFORM_IMG_B, COIN_IMAGE, EXPLOSION_IMAGES, COIN_SOUND, EXPLOSION_SOUND, NAVE_INIMIGA_IMAGE, CORREDOR_INIMIGO_IMAGE
    try:
        PLATFORM_IMG_A = pygame.image.load("images/plataformaexplo.png").convert_alpha()
        PLATFORM_IMG_B = pygame.image.load("images/plataformabem.png").convert_alpha()
        COIN_IMAGE = pygame.image.load("images/moeda3.png").convert_alpha()
        for i in range(1, 4): EXPLOSION_IMAGES.append(pygame.image.load(f"images/explo{i}.png").convert_alpha())
        
        # --- Carregamento de Inimigos ---
        NAVE_INIMIGA_IMAGE = pygame.image.load("images/naveinimiga.png").convert_alpha()
        CORREDOR_INIMIGO_IMAGE = pygame.image.load("images/corredorinimigo.png").convert_alpha()
        
        # Audio
        pygame.mixer.init()
        COIN_SOUND = pygame.mixer.Sound('sounds/coin_sfx.mp3')
        EXPLOSION_SOUND = pygame.mixer.Sound('sounds/explosion_sfx.mp3') 
    except pygame.error as e:
        print(f"ERRO: FALHA AO CARREGAR ASSETS. Detalhes: {e}")
        PLATFORM_IMG_A = None; PLATFORM_IMG_B = None; COIN_IMAGE = None; EXPLOSION_IMAGES = []; NAVE_INIMIGA_IMAGE = None; CORREDOR_INIMIGO_IMAGE = None

def start_game():
    global player, player_group, ground_group, background_group, platform_group, coin_group, score, game_state, scroll_speed, enemy_ground_group, enemy_air_group

    # Reset do estado
    score = 0
    game_state = 'RUNNING'
    scroll_speed = 0
    
    # Inicializacao dos Grupos e Objetos
    player_group = pygame.sprite.Group(); ground_group = pygame.sprite.Group(); background_group = pygame.sprite.Group(); platform_group = pygame.sprite.Group(); coin_group = pygame.sprite.Group(); enemy_ground_group = pygame.sprite.Group(); enemy_air_group = pygame.sprite.Group()
    player = Player(); player_group.add(player)
    ground1 = Ground(0); ground2 = Ground(ground1.rect.width); ground_group.add(ground1, ground2)
    bg1 = Background(0); bg2 = Background(WIDTH); background_group.add(bg1, bg2)

    # Agenda funcoes
    clock.unschedule(spawn_platform); clock.unschedule(spawn_coins_on_ground)
    clock.unschedule(spawn_ground_enemy); clock.unschedule(spawn_air_enemy) 
    
    clock.schedule_interval(spawn_platform, 2.0); clock.schedule_interval(spawn_coins_on_ground, 1.2)
    clock.schedule_interval(spawn_ground_enemy, 2.5); clock.schedule_interval(spawn_air_enemy, 4.0) 
    
    # Plataforma inicial
    image_for_first_platform = PLATFORM_IMG_A
    if not PLATFORM_IMG_A: 
        image_for_first_platform = pygame.Surface((200, 20), pygame.SRCALPHA); image_for_first_platform.fill(PLATFORM_COLOR)
        
    platform_group.add(Platform(x_pos=WIDTH, y_pos=GROUND_Y_POS - 150, width=200, height=20, image_surface=image_for_first_platform))

    # Inicia a musica de fundo (Sintaxe correta para PGZero)
    try: 
        music.play('sounds/sonic_bgm.mp3', -1)
        music.set_volume(0.5)
    except Exception as e: 
        print(f"AVISO: Falha ao carregar musica de fundo. Detalhes: {e}")

def on_key_down(key):
    global game_state
    if game_state == 'GAME_OVER' and key == pygame.K_RETURN:
        start_game()
        
# --- INICIALIZACAO ---
load_assets()
try:
    start_game()
except Exception as e:
    print(f"ERRO CRITICO AO INICIAR GRUPOS/SPRITES: {e}")

# --- FUNCAO AUXILIAR ---
def off_screen(sprite):
    return sprite.rect.right < 0

# ----------------------------------------

def update():
    global scroll_speed, score, game_state
    
    if game_state == 'GAME_OVER':
        scroll_speed = 0
        return
        
    if not player_group: return
        
    all_terrain = ground_group.sprites() + platform_group.sprites()
    all_enemies = enemy_ground_group.sprites() + enemy_air_group.sprites()
    
    player_group.update(all_terrain, all_enemies)
    
    coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
    if coins_collected and COIN_SOUND: COIN_SOUND.play()
    score += len(coins_collected)
    
    ground_group.update(); background_group.update(); platform_group.update(); coin_group.update()
    enemy_ground_group.update(); enemy_air_group.update() # Atualiza inimigos
    
    if scroll_speed > 0:
        if off_screen(background_group.sprites()[0]):
            background_group.remove(background_group.sprites()[0]); last_bg = background_group.sprites()[-1]
            background_group.add(Background(last_bg.rect.right))
    
        if off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0]); last_ground = ground_group.sprites()[-1]
            ground_group.add(Ground(last_ground.rect.right))

def draw():
    
    background_group.draw(screen.surface) 
    platform_group.draw(screen.surface) 
    coin_group.draw(screen.surface)
    enemy_ground_group.draw(screen.surface)
    enemy_air_group.draw(screen.surface)
    ground_group.draw(screen.surface) 
    
    if player_group.sprites():
        player_group.draw(screen.surface)
    
    screen.draw.text(f"SCORE: {score}", (20, 20), color='white', fontsize=40)
    
    if game_state == 'GAME_OVER':
        screen.draw.filled_rect(pygame.Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0, 180)) 
        
        screen.draw.text("VOCE PERDEU!", (WIDTH // 2, HEIGHT // 2 - 50), 
                         color='red', fontsize=100, anchor=('center', 'center'))
        
        screen.draw.text("APERTE ENTER PARA JOGAR NOVAMENTE", (WIDTH // 2, HEIGHT // 2 + 50), 
                         color='white', fontsize=50, anchor=('center', 'center'))

# ----------------------------------------

pgzrun.go()