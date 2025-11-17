# config.py
import pygame
import math

# --- CONFIGURACOES GERAIS ---
WIDTH = 1200
HEIGHT = 600
TITLE = "SONIC ESTAVEL FINALISSIMO COM MENU"
FPS = 30
GAME_SPEED = 8
GROUND_Y_POS = 480
PLATFORM_COLOR = (180, 80, 0)
MIN_PLATFORM_SPACING = 350
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 60
BUTTON_Y_START = HEIGHT // 2 - 100

# --- CONSTANTES DO PLAYER E SPRITES ---
PLAYER_SPRITE_HEIGHT = 80
PLAYER_SPRITE_WIDTH = 80
GROUND_HEIGHT = 30
EXPLOSION_FRAME_RATE = 5

# --- CAMINHOS DE ASSETS ---
ASSET_PATHS = {
    'MUSIC_FILE': 'sounds/sonic_bgm.mp3',
    'COIN_SFX': 'sounds/coin_sfx.mp3',
    'EXPLOSION_SFX': 'sounds/explosion_sfx.mp3',
    'PLATFORM_A_IMG': 'images/plataformaexplo.png',
    'PLATFORM_B_IMG': 'images/plataformabem.png',
    'COIN_IMG': 'images/moeda3.png',
    'NAVE_IMG': 'images/naveinimiga.png',
    'CORREDOR_IMG': 'images/corredorinimigo.png',
    'GAME_OVER_IMG': 'images/imagemderrota.png',
    'EXPLOSION_1': 'images/explo1.png',
    'EXPLOSION_2': 'images/explo2.png',
    'EXPLOSION_3': 'images/explo3.png',
    # Sprites do jogador (nomes relativos dentro da pasta images/)
    'IDLE_RIGHT': 'paradodir.png',
    'RUN_RIGHT': 'correndodir.png',
    'FLY_RIGHT': 'semipulodir.png',
    'FALL_RIGHT': 'pulodir.png',
    'LAND_RIGHT': 'pousodir.png',
    'RUN_LEFT': 'correndoesq.png',
    'FLY_LEFT': 'semipuloesq.png',
    'FALL_LEFT': 'puloesq.png',
    'LAND_LEFT': 'pousoesq.png',
    'IDLE_LEFT_FALLBACK': 'paradoesq.png',
    # Background (opcional)
    'FUNDOSONICS_IMG': 'images/fundosonics.jpg'
}
