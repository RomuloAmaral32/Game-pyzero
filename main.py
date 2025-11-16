# -*- coding: utf-8 -*-
import pygame 
import pgzrun 
import random 

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
PLATFORM_IMG_A = None 
PLATFORM_IMG_B = None
COIN_IMAGE = None 

# --- CLASSE PLATFORM ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, width, height, image_surface):
        super().__init__()
        
        self.image = pygame.transform.scale(image_surface, (width, height))
        self.rect = self.image.get_rect(x=x_pos, y=y_pos)

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

# --- FUNCOES DE SPAWN ---
def spawn_platform():
    if 'platform_group' not in globals() or platform_group is None: return
    last_platform_right_edge = 0
    if platform_group.sprites(): last_platform_right_edge = max(p.rect.right for p in platform_group.sprites())
    min_x_start = max(WIDTH, last_platform_right_edge + MIN_PLATFORM_SPACING)
    platform_width = random.randint(150, 300) 
    platform_y = random.randint(GROUND_Y_POS - 250, GROUND_Y_POS - 100)
    new_platform_x = random.randint(min_x_start, min_x_start + 200)

    if PLATFORM_IMG_A and PLATFORM_IMG_B: image_to_use = random.choice([PLATFORM_IMG_A, PLATFORM_IMG_B])
    else:
        solid_surface = pygame.Surface((platform_width, 20), pygame.SRCALPHA); solid_surface.fill(PLATFORM_COLOR); image_to_use = solid_surface

    new_platform = Platform(x_pos=new_platform_x, y_pos=platform_y, width=platform_width, height=20, image_surface=image_to_use)
    platform_group.add(new_platform)

    # Logica de moedas na plataforma
    if COIN_IMAGE and random.random() < 0.7: 
        num_coins = random.randint(2, 5); gap_between_coins = platform_width // num_coins if num_coins > 0 else 0; start_x = new_platform_x + 20 
        for i in range(num_coins):
            coin_x = start_x + (gap_between_coins * i); coin_y = platform_y - 40 
            if coin_x < new_platform_x + platform_width - 30: coin_group.add(Coin(x_pos=coin_x, y_pos=coin_y))

def spawn_coins_on_ground():
    if not COIN_IMAGE or 'coin_group' not in globals() or coin_group is None: return

    if random.random() < 0.5: 
        num_coins = random.randint(3, 6); coin_y = GROUND_Y_POS - 40; start_x = WIDTH + random.randint(50, 200) 
        for i in range(num_coins):
            coin_x = start_x + (i * 45) 
            coin_group.add(Coin(x_pos=coin_x, y_pos=coin_y))


# --- CLASSE PLAYER ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        def _load_and_scale(filename):
            try:
                img = pygame.image.load(f"images/{filename}").convert_alpha()
                return pygame.transform.scale(img, (LARGURA_SPRITE_PLAYER, ALTURA_SPRITE_PLAYER))
            except pygame.error as e:
                print(f"ERROR: Could not load {filename}. Details: {e}")
                fail_surface = pygame.Surface((LARGURA_SPRITE_PLAYER, ALTURA_SPRITE_PLAYER)); fail_surface.fill((255, 0, 0)); return fail_surface

        self.idle_right = _load_and_scale("paradodir.png"); self.run_right = _load_and_scale("correndodir.png"); self.fly_right = _load_and_scale("semipulodir.png"); self.fall_right = _load_and_scale("pulodir.png"); self.land_right = _load_and_scale("pousodir.png"); self.run_left = _load_and_scale("correndoesq.png"); self.fly_left = _load_and_scale("semipuloesq.png"); self.fall_left = _load_and_scale("puloesq.png"); self.land_left = _load_and_scale("pousoesq.png")
        try: self.idle_left = _load_and_scale("paradoesq.png")
        except: self.idle_left = pygame.transform.flip(self.idle_right, True, False)

        self.current_image = self.idle_right; self.image = self.current_image; self.rect = self.image.get_rect(x=100, y=GROUND_Y_POS - ALTURA_SPRITE_PLAYER) 
        self.speed_y = 0; self.gravity = 1; self.on_ground = True; self.facing_right = True; self.is_jumping = False; self.is_falling = False

    def move_horizontal(self, all_terrain_sprites):
        global scroll_speed; old_x = self.rect.x; moving_horizontally = False
        if keyboard.right:
            self.rect.x += GAME_SPEED; self.facing_right = True; moving_horizontally = True; scroll_speed = GAME_SPEED
        elif keyboard.left:
            self.rect.x -= GAME_SPEED; self.facing_right = False; moving_horizontally = True; scroll_speed = 0 
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
        self.rect.y += self.speed_y; self.speed_y += self.gravity

    def jump_or_fly(self):
        if keyboard.space and self.on_ground: self.speed_y = -18; self.on_ground = False; self.is_jumping = True; self.is_falling = False
        
    def check_ground_sensor(self, all_terrain_sprites):
        sensor_rect = self.rect.copy(); sensor_rect.y = self.rect.bottom; sensor_rect.height = 1 
        for sprite in all_terrain_sprites:
            if sensor_rect.colliderect(sprite.rect): return True
        return False

    def check_vertical_collision(self, all_terrain_sprites):
        on_ground_this_frame = self.check_ground_sensor(all_terrain_sprites)
        
        if on_ground_this_frame and self.speed_y >= 0:
            collisions = pygame.sprite.spritecollide(self, all_terrain_sprites, False)
            if collisions:
                platform_to_land_on = min(collisions, key=lambda x: x.rect.top)
                if self.rect.bottom > platform_to_land_on.rect.top:
                    self.rect.bottom = platform_to_land_on.rect.top
            
            self.speed_y = 0; self.on_ground = True; return
        
        if self.speed_y < 0: 
            collisions = pygame.sprite.spritecollide(self, all_terrain_sprites, False)
            if collisions:
                self.speed_y = 0; self.on_ground = False; return 

        if not on_ground_this_frame and self.rect.bottom < GROUND_Y_POS:
            self.on_ground = False
        elif self.rect.bottom >= GROUND_Y_POS:
            self.rect.bottom = GROUND_Y_POS; self.speed_y = 0; self.on_ground = True


    def update(self, all_terrain_sprites): 
        self.jump_or_fly(); self.apply_gravity(); self.check_vertical_collision(all_terrain_sprites)
        moving_horizontally = self.move_horizontal(all_terrain_sprites); self.check_boundaries()
        
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
        super().__init__(); ground_w = WIDTH * 2; self.image = pygame.Surface((ground_w, ALTURA_CHAO), pygame.SRCALPHA); self.image.fill((0, 100, 160, 0)); self.rect = self.image.get_rect(x=x_pos, y=GROUND_Y_POS)
    def update(self):
        global scroll_speed; self.rect.x -= scroll_speed
        
class Background(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__(); 
        try: self.image = pygame.image.load("images/fundosonics.jpg").convert(); self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        except pygame.error as e: self.image = pygame.Surface((WIDTH, HEIGHT)); self.image.fill((135, 206, 235)) 
        self.rect = self.image.get_rect(x=x_pos, y=0)
    def update(self):
        global scroll_speed; self.rect.x -= scroll_speed 
        
# --- INICIALIZACAO DE ASSETS ---
try:
    PLATFORM_IMG_A = pygame.image.load("images/plataformaexplo.png").convert_alpha()
    PLATFORM_IMG_B = pygame.image.load("images/plataformabem.png").convert_alpha()
    COIN_IMAGE = pygame.image.load("images/moeda3.png").convert_alpha()
except pygame.error as e:
    PLATFORM_IMG_A = None; PLATFORM_IMG_B = None; COIN_IMAGE = None

try:
    player_group = pygame.sprite.Group(); ground_group = pygame.sprite.Group(); background_group = pygame.sprite.Group(); platform_group = pygame.sprite.Group(); coin_group = pygame.sprite.Group() 
    player = Player(); player_group.add(player)
    ground1 = Ground(0); ground2 = Ground(ground1.rect.width); ground_group.add(ground1, ground2)
    bg1 = Background(0); bg2 = Background(WIDTH); background_group.add(bg1, bg2)

    clock.schedule_interval(spawn_platform, 2.0)
    clock.schedule_interval(spawn_coins_on_ground, 1.2)
    
    # Plataforma inicial
    image_for_first_platform = PLATFORM_IMG_A
    if not PLATFORM_IMG_A: 
        image_for_first_platform = pygame.Surface((200, 20), pygame.SRCALPHA); image_for_first_platform.fill(PLATFORM_COLOR)
        
    platform_group.add(Platform(x_pos=WIDTH, y_pos=GROUND_Y_POS - 150, width=200, height=20, image_surface=image_for_first_platform))
    
except Exception as e:
    print(f"ERRO CRITICO AO INICIAR GRUPOS/SPRITES: {e}")
    player_group = None; ground_group = None; background_group = None; platform_group = None; coin_group = None

# --- FUNCAO AUXILIAR ---
def off_screen(sprite):
    return sprite.rect.right < 0

# ----------------------------------------

def update():
    global scroll_speed, score
    if not player_group: return
        
    all_terrain = ground_group.sprites() + platform_group.sprites()
    
    player_group.update(all_terrain)
    
    coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
    score += len(coins_collected)
    
    ground_group.update(); background_group.update(); platform_group.update(); coin_group.update()
    
    if scroll_speed > 0:
        if off_screen(background_group.sprites()[0]):
            background_group.remove(background_group.sprites()[0]); last_bg = background_group.sprites()[-1]
            background_group.add(Background(last_bg.rect.right))
    
        if off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0]); last_ground = ground_group.sprites()[-1]
            ground_group.add(Ground(last_ground.rect.right))

def draw():
    if not player_group: return
    
    background_group.draw(screen.surface) 
    platform_group.draw(screen.surface) 
    coin_group.draw(screen.surface)
    ground_group.draw(screen.surface) 
    player_group.draw(screen.surface)
    
    screen.draw.text(f"SCORE: {score}", (20, 20), color='white', fontsize=40)

# ----------------------------------------

pgzrun.go()