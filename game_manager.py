# game_manager.py
import pygame
import random
import os
from config import *
from entities import Player, Ground, Background, Platform, Coin, CorredorInimigo, NaveInimiga

import entities

# GameManager: centraliza estado do jogo (sem usar globais espalhados)
class GameManager:
    def __init__(self):
        # estado
        self.scroll_speed = 0
        self.score = 0
        self.game_state = 'MENU'
        self.is_audio_on = True

        # grupos de sprites
        self.player_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.background_group = pygame.sprite.Group()
        self.platform_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.enemy_ground_group = pygame.sprite.Group()
        self.enemy_air_group = pygame.sprite.Group()

        # referência ao player
        self.player = None

        # assets (será preenchido por load_assets)
        self.assets = {
            'EXPLOSION_IMAGES': [],
            'COIN_SOUND': None,
            'EXPLOSION_SOUND': None,
            'MUSIC_FILE': config.ASSET_PATHS.get('MUSIC_FILE')
        }

    # -------- ASSETS ----------
    def _load_image(self, path):
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            return None

    def _load_sound(self, path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None

    def load_assets(self):
        """Carrega imagens e sons (preenche self.assets e entities.ASSETS)."""
        p = config.ASSET_PATHS
        a = self.assets

        # imagens
        a['PLATFORM_IMG_A'] = self._load_image(p.get('PLATFORM_A_IMG', 'images/plataformaexplo.png'))
        a['PLATFORM_IMG_B'] = self._load_image(p.get('PLATFORM_B_IMG', 'images/plataformabem.png'))
        a['COIN_IMAGE'] = self._load_image(p.get('COIN_IMG', 'images/moeda3.png'))
        a['NAVE_INIMIGA_IMAGE'] = self._load_image(p.get('NAVE_IMG', 'images/naveinimiga.png'))
        a['CORREDOR_INIMIGO_IMAGE'] = self._load_image(p.get('CORREDOR_IMG', 'images/corredorinimigo.png'))
        a['GAME_OVER_IMAGE'] = self._load_image(p.get('GAME_OVER_IMG', 'images/imagemderrota.png'))
        a['BACKGROUND_IMAGE'] = self._load_image(p.get('FUNDOSONICS_IMG', 'images/fundosonics.jpg'))

        # explosion frames (1..3)
        explo = []
        for k in ('EXPLOSION_1', 'EXPLOSION_2', 'EXPLOSION_3'):
            path = p.get(k)
            if path:
                img = self._load_image(path)
                if img:
                    explo.append(img)
        a['EXPLOSION_IMAGES'] = explo

        # sons (inicia mixer silenciosamente caso não inicie)
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        a['COIN_SOUND'] = self._load_sound(p.get('COIN_SFX', 'sounds/coin_sfx.mp3'))
        a['EXPLOSION_SOUND'] = self._load_sound(p.get('EXPLOSION_SFX', 'sounds/explosion_sfx.mp3'))
        a['MUSIC_FILE'] = p.get('MUSIC_FILE')

        # Propaga para entities
        entities.ASSETS = a

    # -------- GAME FLOW ----------
    def start_game(self):
        """Inicia / reinicia o jogo e agenda spawns."""
        self.score = 0
        self.game_state = 'RUNNING'
        self.scroll_speed = 0

        # limpa grupos
        self.player_group.empty(); self.ground_group.empty(); self.background_group.empty()
        self.platform_group.empty(); self.coin_group.empty(); self.enemy_ground_group.empty(); self.enemy_air_group.empty()

        # cria entidades
        self.player = entities.Player()
        self.player_group.add(self.player)

        ground1 = entities.Ground(0)
        ground2 = entities.Ground(ground1.rect.width)
        self.ground_group.add(ground1, ground2)

        bg1 = entities.Background(0)
        bg2 = entities.Background(config.WIDTH)
        self.background_group.add(bg1, bg2)

        # cancela timers antigos (se existirem)
        try:
            clock.unschedule(self._spawn_platform)
            clock.unschedule(self._spawn_coins_on_ground)
            clock.unschedule(self._spawn_ground_enemy)
            clock.unschedule(self._spawn_air_enemy)
        except Exception:
            pass

        # agenda novos spawns
        clock.schedule_interval(self._spawn_platform, 2.0)
        clock.schedule_interval(self._spawn_coins_on_ground, 1.2)
        clock.schedule_interval(self._spawn_ground_enemy, 2.5)
        clock.schedule_interval(self._spawn_air_enemy, 4.0)

        # plataforma inicial
        first_img = self.assets.get('PLATFORM_IMG_A') or self.assets.get('PLATFORM_IMG_B')
        if not first_img:
            surf = pygame.Surface((200, 20), pygame.SRCALPHA); surf.fill(config.PLATFORM_COLOR)
            first_img = surf
        self.platform_group.add(entities.Platform(config.WIDTH, config.GROUND_Y_POS - 150, 200, 20, first_img))

        # inicia música se necessário
        self._start_music_if_enabled()

    def _start_music_if_enabled(self):
        if not self.is_audio_on:
            try: pygame.mixer.music.stop()
            except: pass
            return
        music_file = self.assets.get('MUSIC_FILE')
        if not music_file:
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)
        except Exception:
            pass

    def toggle_audio(self):
        self.is_audio_on = not self.is_audio_on
        if self.is_audio_on:
            self._start_music_if_enabled()
            try:
                if self.assets.get('COIN_SOUND'):
                    self.assets['COIN_SOUND'].set_volume(1.0)
                if self.assets.get('EXPLOSION_SOUND'):
                    self.assets['EXPLOSION_SOUND'].set_volume(1.0)
            except Exception:
                pass
        else:
            try: pygame.mixer.music.stop()
            except: pass
            try:
                if self.assets.get('COIN_SOUND'):
                    self.assets['COIN_SOUND'].set_volume(0.0)
                if self.assets.get('EXPLOSION_SOUND'):
                    self.assets['EXPLOSION_SOUND'].set_volume(0.0)
            except Exception:
                pass

    # -------- SPAWNS (métodos privados) ----------
    def _spawn_platform(self):
        last_right = 0
        if self.platform_group.sprites():
            last_right = max(p.rect.right for p in self.platform_group.sprites())
        min_x_start = max(config.WIDTH, last_right + config.MIN_PLATFORM_SPACING)
        platform_width = random.randint(150, 300)
        platform_y = random.randint(config.GROUND_Y_POS - 250, config.GROUND_Y_POS - 100)
        new_platform_x = random.randint(min_x_start, min_x_start + 200)
        is_explosive_platform = random.random() < 0.3

        image_to_use = None
        if is_explosive_platform and self.assets.get('PLATFORM_IMG_A'):
            image_to_use = self.assets['PLATFORM_IMG_A']
        elif self.assets.get('PLATFORM_IMG_B'):
            image_to_use = self.assets['PLATFORM_IMG_B']
        else:
            solid_surface = pygame.Surface((platform_width, 20), pygame.SRCALPHA); solid_surface.fill(config.PLATFORM_COLOR)
            image_to_use = solid_surface

        new_platform = entities.Platform(new_platform_x, platform_y, platform_width, 20, image_to_use, is_explosive_platform)
        self.platform_group.add(new_platform)

        # moedas sobre a plataforma
        if self.assets.get('COIN_IMAGE') and random.random() < 0.7:
            num_coins = random.randint(2, 5)
            start_x = new_platform_x + 20
            for i in range(num_coins):
                coin_x = start_x + (i * 45)
                coin_y = platform_y - 40
                if coin_x < new_platform_x + platform_width - 30:
                    self.coin_group.add(entities.Coin(coin_x, coin_y))

    def _spawn_coins_on_ground(self):
        if not self.assets.get('COIN_IMAGE'):
            return
        if random.random() < 0.5:
            num_coins = random.randint(3, 6)
            start_x = config.WIDTH + random.randint(50, 200)
            for i in range(num_coins):
                coin_x = start_x + (i * 45)
                coin_y = config.GROUND_Y_POS - 40
                self.coin_group.add(entities.Coin(coin_x, coin_y))

    def _spawn_ground_enemy(self):
        if not self.assets.get('CORREDOR_INIMIGO_IMAGE'):
            return
        if random.random() < 0.4:
            new_enemy = entities.CorredorInimigo(config.WIDTH + random.randint(50, 300))
            self.enemy_ground_group.add(new_enemy)

    def _spawn_air_enemy(self):
        if not self.assets.get('NAVE_INIMIGA_IMAGE'):
            return
        if random.random() < 0.7:
            y_pos = random.randint(config.HEIGHT // 4, config.HEIGHT // 2)
            new_enemy = entities.NaveInimiga(config.WIDTH + random.randint(50, 500), y_pos)
            self.enemy_air_group.add(new_enemy)

    # -------- UPDATE e DRAW helpers ----------
    def update(self, keyboard):
        """keyboard: objeto fornecido por pgzero (pgzero.keyboard.keyboard)"""
        # sincroniza scrolling
        # early out (menu / gameover)
        if self.game_state == 'MENU':
            return
        if self.game_state == 'GAME_OVER':
            self.scroll_speed = 0
            return

        if not self.player_group.sprites():
            return

        all_terrain = list(self.ground_group.sprites()) + list(self.platform_group.sprites())
        all_enemies = list(self.enemy_ground_group.sprites()) + list(self.enemy_air_group.sprites())

        # player update: player.update recebe keyboard, terreno, inimigos, manager (self)
        self.player_group.update(keyboard, all_terrain, all_enemies, self)

        # coleta moedas
        coins_collected = pygame.sprite.spritecollide(self.player, self.coin_group, True)
        if coins_collected and self.assets.get('COIN_SOUND') and self.is_audio_on:
            try: self.assets['COIN_SOUND'].play()
            except: pass
        self.score += len(coins_collected)

        # atualiza demais grupos (passando scroll_speed)
        self.ground_group.update(self.scroll_speed)
        self.background_group.update(self.scroll_speed)
        self.platform_group.update(self.scroll_speed)
        self.coin_group.update(self.scroll_speed)
        self.enemy_ground_group.update(self.scroll_speed)
        self.enemy_air_group.update(self.scroll_speed)

        # reciclagem (looping)
        if self.scroll_speed > 0:
            if self.background_group.sprites() and self.background_group.sprites()[0].rect.right < 0:
                first = self.background_group.sprites()[0]
                self.background_group.remove(first)
                last_bg = self.background_group.sprites()[-1]
                self.background_group.add(entities.Background(last_bg.rect.right))
            if self.ground_group.sprites() and self.ground_group.sprites()[0].rect.right < 0:
                firstg = self.ground_group.sprites()[0]
                self.ground_group.remove(firstg)
                lastg = self.ground_group.sprites()[-1]
                self.ground_group.add(entities.Ground(lastg.rect.right))

    def draw(self, screen):
        if self.game_state == 'MENU':
            screen.fill((0, 0, 50))
            screen.draw.text("SONIC JUMPER", (config.WIDTH // 2, config.BUTTON_Y_START - 100),
                             color='yellow', fontsize=100, anchor=(0.5, 0.5))
            buttons = [
                "COMEÇAR O JOGO",
                "MÚSICA E SONS: " + ("LIGADO" if self.is_audio_on else "DESLIGADO"),
                "SAÍDA"
            ]
            for i, text in enumerate(buttons):
                y_pos = config.BUTTON_Y_START + (i * 80)
                rect = pygame.Rect(config.WIDTH // 2 - config.BUTTON_WIDTH // 2, y_pos, config.BUTTON_WIDTH, config.BUTTON_HEIGHT)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                button_color = (60, 60, 60) if rect.collidepoint(mouse_x, mouse_y) else (30, 30, 30)
                screen.draw.filled_rect(rect, button_color)
                screen.draw.rect(rect, (200, 200, 200))
                screen.draw.text(text, rect.center, color='white', fontsize=30, anchor=(0.5, 0.5))
            return

        # Desenha o jogo
        self.background_group.draw(screen.surface)
        self.platform_group.draw(screen.surface)
        self.coin_group.draw(screen.surface)
        self.enemy_ground_group.draw(screen.surface)
        self.enemy_air_group.draw(screen.surface)
        self.ground_group.draw(screen.surface)
        if self.player_group.sprites():
            self.player_group.draw(screen.surface)
        screen.draw.text(f"SCORE: {self.score}", (20, 20), color='white', fontsize=40)

        if self.game_state == 'GAME_OVER':
            go_img = self.assets.get('GAME_OVER_IMAGE')
            if go_img:
                try:
                    go_scaled = pygame.transform.scale(go_img, (config.WIDTH, config.HEIGHT))
                    screen.surface.blit(go_scaled, (0, 0))
                except Exception:
                    screen.draw.filled_rect(pygame.Rect(0, 0, config.WIDTH, config.HEIGHT), (0, 0, 0))
            else:
                screen.draw.filled_rect(pygame.Rect(0, 0, config.WIDTH, config.HEIGHT), (0, 0, 0))
            screen.draw.text("VOCE PERDEU!", (config.WIDTH // 2, config.HEIGHT // 2 - 50), color='red', fontsize=100, anchor=(0.5, 0.5))
            screen.draw.text("APERTE ENTER PARA JOGAR NOVAMENTE", (config.WIDTH // 2, config.HEIGHT // 2 + 50), color='white', fontsize=50, anchor=(0.5, 0.5))

