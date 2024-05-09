import pygame as pg
import random as rng
import numpy as np
import cv2
import time
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import os
import win32api

# блок с определением игровых элементов
player_lives = 3
score = 0
fruits = ['melon', 'orange', 'bebra', 'guava', 'durian(bad)']

FPS = 120

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

pg.init()
clock = pg.time.Clock()

window = pg.display.set_mode((1280, 720))
back = pg.transform.scale(pg.image.load('images/background.jpg'), (1280, 720))

font = pg.font.Font(os.path.join(os.getcwd(), './comic.ttf'), 60)
score_text = font.render('Score : ' + str(score), True, (255, 255, 255))

lives_icon_orig = pg.image.load('images/hp_ico.png')
lives_icon = pg.transform.scale(lives_icon_orig,(70,70))

red_lives_orig = pg.image.load('images/hp_ico.png')
red_lives = pg.transform.scale(red_lives_orig, (70,70))

bag_image_orig = pg.image.load('images/bag.png')
bag_image = pg.transform.scale(bag_image_orig, (70,70))

drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

video = cv2.VideoCapture(0)

# создание фрукта
def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
    orig_image = pg.image.load(fruit_path)
    scale_image = pg.transform.scale(orig_image, (85, 85))
    data[fruit] = {
        'img': scale_image,
        'x': rng.randint(300,900),
        'y': 0,
        'speed_x': rng.randint(-1,1),
        'speed_y': score / 10 + 1,
        'throw': False,                               
        'hit': False,
    }

    if rng.random() >= 0.0001:
        data[fruit]['throw'] = True
    else:
        data[fruit]['throw'] = False

data = {}
for fruit in fruits:
    generate_random_fruits(fruit)

# функция для удаления пойманного фрукта с экрана
def hide_fruits():
    value['x'] = -2000
    value['y'] = -2000

# функция для удаления жизни
def hide_cross_lives(x, y):
    window.blit(red_lives, (x, y))

# функция для отрисовки стилизованного текста
def draw_text(text, x, y):
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    window.blit(text_surface, text_rect)

# функция для отрисовки жизней
def draw_lives(display, x, y, lives, image) :
    for i in range(lives) :
        img = image
        img_rect = img.get_rect()       
        img_rect.x = int(x + 80 * i)
        img_rect.y = y
        display.blit(img, img_rect)

# функция для показа титульного экрана
def show_gameover_screen():
    window.blit(back, (0,0))
    draw_text("FRUIT CATCHER!", 640, 150)
    if not game_over :
        draw_text("Score : " + str(score), 640, 300)

    draw_text("PRESS ANY KEY!", 640, 450)
    pg.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYUP:
                waiting = False

first_round = True
game_over = True
game_running = True

# цикл, в котором происходит игра

while video.isOpened():
    # __,frame = video.read()
    # image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # image = cv2.flip(image, 1)
    #
    # image_height,image_width,_ = image.shape
    #
    # hands_render_result = hands.process(image)
    #
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # захват и отрисовка рук
    # if hands_render_result.multi_hand_landmarks:
    #      for num,hand in enumerate(hands_render_result.multi_hand_landmarks):
    #        drawing.draw_landmarks(image,hand,mp_hands.HAND_CONNECTIONS,
    #          drawing.DrawingSpec(color = (250, 44, 250), thickness = 2, circle_radius = 2))
    #
    # if hands_render_result.multi_hand_landmarks != None:
    #     for handsLandmarks in hands_render_result.multi_hand_landmarks:
    #         for points in mp_hands.HandLandmark:
    #             normalizedLandmark = handsLandmarks.landmark[points]
    #             pixelCoordinatesLandmark = drawing._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, image_width, image_height)
    #             if points == mp_hands.HandLandmark.INDEX_FINGER_TIP:
    #                 try:
    #                     cv2.circle(image, (pixelCoordinatesLandmark[0], pixelCoordinatesLandmark[1]),25,(0,200,0),5)
    #                     indexfingertip_x = pixelCoordinatesLandmark[0]
    #                     indexfingertip_y = pixelCoordinatesLandmark[1]
    #                     win32api.SetCursorPos((indexfingertip_x*4, indexfingertip_y*5))
    #                 except:
    #                     pass

        # отрисовка окна с камерой и захватом рук
        # cv2.imshow('game', image)

        # ВСЕ ВЫРЕЗАННЫЕ КУСКИ КОДА ОТВЕЧАЮТ ЗА AR ЧАСТЬ ИГРЫ, КОТОРАЯ РАБОТАЕТ НЕ НА ВСЕХ ВЕРСИЯХ PYTHON (РАБОТАЕТ ТОЛЬКО НА 3.9)

        if game_over :
            if first_round :
                show_gameover_screen()
                first_round = False
            game_over = False
            player_lives = 3
            draw_lives(window, 690, 5, player_lives, red_lives)
            score = 0
        
        # отрисовка игры
        window.blit(back, (0, 0))
        window.blit(score_text, (0, 0))
        draw_lives(window, 1000, 5, player_lives, red_lives)

        for event in pg.event.get():
        # проверка на закрытие окна
            if event.type == pg.QUIT:
                video.release()

        for key, value in data.items():
            if value['throw']:
                value['x'] += value['speed_x']
                value['y'] += value['speed_y']

                if value['y'] <= 800:
                    window.blit(value['img'], (value['x'], value['y']))
                else:
                    generate_random_fruits(key)

                current_position = pg.mouse.get_pos()
                window.blit(bag_image, (current_position[0] - 25, current_position[1] -25))

                # проверка касания курсора и фрукта
                if not value['hit'] and current_position[0] > value['x'] and current_position[0] < value['x']+60 \
                        and current_position[1] > value['y'] and current_position[1] < value['y']+60:
                    if key == 'durian(bad)':
                        player_lives -= 1
                        score -= 5
                        if player_lives == 0:
                            hide_cross_lives(690, 15)
                        elif player_lives == 1 :
                            hide_cross_lives(725, 15)
                        elif player_lives == 2 :
                            hide_cross_lives(760, 15)
                        if player_lives <= 0 :
                            show_gameover_screen()
                            game_over = True

                    # блок описания фруктов

                    if key != 'durian(bad)':
                        score += 1
                    score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
                    value['hit'] = True
                    hide_fruits()
                    if key == 'bebra':
                        score += 5
                        if player_lives < 3:
                            player_lives += 1
                    if key == 'guava':
                        score += 2
                        
            else:
                generate_random_fruits(key)

        pg.display.update()
        clock.tick(FPS)

# выгруз всех окон
pg.quit()