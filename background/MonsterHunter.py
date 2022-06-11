import pygame
from pygame import mixer
import os
import random
import csv
import button

pygame.init()
mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Monster Hunter')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75
SCROLL_THRESH = 350
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 22
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 3

start_game = False
instruction = False
pause = False
finished = False
start_intro = False
enter_level = False
ingame = False
death = False
score = 0
time = 120
mute = False

#define player action variables
moving_left = False
moving_right = False
shoot = False

#load audio
pygame.mixer.music.load('audio/DizzySpells.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
damaged_fx = pygame.mixer.Sound('audio/damaged.wav')
damaged_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
gameover_fx = pygame.mixer.Sound('audio/gameover.wav')
gameover_fx.set_volume(1)
gamefinished_fx = pygame.mixer.Sound('audio/finished.wav')
gamefinished_fx.set_volume(1)
pickup_fx = pygame.mixer.Sound('audio/pickup.wav')
pickup_fx.set_volume(1)
                             
#bg images
cave_img = pygame.image.load('Background/cave.png').convert_alpha()
cave2_img = pygame.image.load('Background/cave2.png').convert_alpha()

mh_img = pygame.image.load('Background/MH.png').convert_alpha()
gameover_img = pygame.image.load('Background/GameOverr.png').convert_alpha()
gamepause_img = pygame.image.load('Background/Paused.png').convert_alpha()
gamefinish_img = pygame.image.load('Background/GFS.png').convert_alpha()
#button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
play_img = pygame.image.load('img/play_btn.png').convert_alpha()
level1_img = pygame.image.load('img/level1_btn.png').convert_alpha()
level2_img = pygame.image.load('img/level2_btn.png').convert_alpha()
level3_img = pygame.image.load('img/level3_btn.png').convert_alpha()
level4_img = pygame.image.load('img/level4_btn.png').convert_alpha()
level5_img = pygame.image.load('img/level5_btn.png').convert_alpha()

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
        img = pygame.image.load(f'img/Tile/{x}.png')
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)

#bullet
bullet_img = pygame.image.load('icons/bullet.png').convert_alpha()
arrow_img = pygame.image.load('icons/leftArrows.png').convert_alpha()
rightarrow_img = pygame.image.load('icons/rightArrows.png').convert_alpha()
leftfireball_img = pygame.image.load('icons/leftfireball.png').convert_alpha()
rightfireball_img = pygame.image.load('icons/rightfireball.png').convert_alpha()
earrow_img = pygame.image.load('icons/enemyleftArrows.png').convert_alpha()
rightearrow_img = pygame.image.load('icons/enemyrightArrows.png').convert_alpha()

#pick up boxes
health_box_img = pygame.image.load('icons/health_box.png').convert_alpha()
coin_img = pygame.image.load('icons/12.png').convert_alpha()
ammo_box_img = pygame.image.load('icons/ammo_box.png').convert_alpha()
item_boxes = {
        'Health'        : health_box_img,
        'Ammo'          : ammo_box_img,
        'Coin'          : coin_img
}

#define colours
RED = (135, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
DARKRED = (70, 20, 0)
ORANGE = (156, 85, 9)

#define font
font = pygame.font.Font('PublicPixel.ttf', 30)

#method for drawing text
def draw_text(text, font, text_col, x, y, scale):
        img = font.render(text, True, text_col)
        img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        screen.blit(img, (x, y))

#method for drawing bg
def draw_bgmain():
        screen.fill(BLACK)
        width = cave2_img.get_width()
        for x in range(5):
            screen.blit(cave2_img, ((x * width) - bg_scroll,0))

def draw_bg():
        screen.fill(BLACK)
        width = cave_img.get_width()
        for x in range(5):
            screen.blit(cave_img, ((x * width) - bg_scroll,0))

#function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    ebullet_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    platform_group.empty()
    lava_group.empty()
    exit_group.empty()
    spike_group.empty()
    
    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data

#entity class
class Soldier(pygame.sprite.Sprite):
        def __init__(self, char_type, x, y, scale, speed, ammo):
                pygame.sprite.Sprite.__init__(self)
                self.player_spike = 0
                self.levelanimation = 600
                self.score = score
                self.time_tick = 0
                self.time = time
                self.loading = 1200
                self.alive = True
                self.char_type = char_type
                self.speed = speed
                self.ammo = ammo
                self.shoots = False
                self.shooting = False
                self.view = False
                self.start_ammo = ammo
                self.shoot_cooldown = 0
                self.health = 100
                self.max_health = self.health
                self.direction = 1
                self.vel_y = 0
                self.jump = False
                self.in_air = True
                self.flip = False
                self.animation_list = []
                self.frame_index = 0
                self.action = 0
                self.update_time = pygame.time.get_ticks()
                #ai specific variables
                self.move_counter = 0
                self.vision = pygame.Rect(0, 0, 250, 20)
                self.idling = False
                self.idling_counter = 0
                
                #load all images for the players
                animation_types = ['Idle', 'Run', 'Jump', 'Death', 'Attack']
                for animation in animation_types:
                        #reset temporary list of images
                        temp_list = []
                        #count number of files in the folder
                        num_of_frames = len(os.listdir(f'{self.char_type}/{animation}'))
                        for i in range(num_of_frames):
                                img = pygame.image.load(f'{self.char_type}/{animation}/{i}.png').convert_alpha()
                                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                                temp_list.append(img)
                        self.animation_list.append(temp_list)

                self.image = self.animation_list[self.action][self.frame_index]
                self.rect = self.image.get_rect()
                self.rect.center = (x, y)
                self.width =  self.image.get_width()
                self.height = self.image.get_height()

        #constant self update
        def update(self):
                self.update_animation()
                self.check_alive()
                #update cooldown
                if self.shoot_cooldown > 0:
                        if self.char_type == 'player':
                                self.shoot_cooldown -= 1
                        elif self.char_type == 'enemy' or self.char_type == 'enemy2' and self.shoots == True:
                                self.shoot_cooldown -= 1
                                if self.shoot_cooldown == 0:
                                        self.ai_shoot()
                                        
                if pause == False and player.alive and ingame == True:
                        if player.time_tick < 500:
                                if level == 1:
                                        player.time_tick += 1
                                elif level == 2:
                                        player.time_tick += 1
                                elif level == 3:
                                        player.time_tick += .5
                        elif player.time_tick >= 500:
                                player.time_tick = 0
                                player.time -= 1
                if player.player_spike > 0:
                        player.player_spike -= 1
        #method for moving the player
        def move(self, moving_left, moving_right):
                #reset movement variables
                dx = 0
                dy = 0
                col_thresh = 20
                screen_scroll = 0
                #assign movement variables if moving left or right
                if moving_left and self.char_type == 'player':
                        dx = -self.speed
                        self.flip = True
                        self.direction = -1
                if moving_right and self.char_type == 'player':
                        dx = self.speed
                        self.flip = False
                        self.direction = 1
                if moving_left and self.char_type == 'enemy' and self.action != 4 and self.alive:
                        dx = -self.speed
                        self.flip = True
                        self.direction = -1
                if moving_right and self.char_type == 'enemy' and self.action != 4 and self.alive:
                        dx = self.speed
                        self.flip = False
                        self.direction = 1
                        
                if moving_left and self.char_type == 'enemy2' and self.action != 4 and self.alive:
                        dx = -self.speed
                        self.flip = True
                        self.direction = -1
                if moving_right and self.char_type == 'enemy2' and self.action != 4 and self.alive:
                        dx = self.speed
                        self.flip = False
                        self.direction = 1
                #jump
                if self.jump == True and self.in_air == False:
                        self.vel_y = -11
                        self.jump = False
                        self.in_air = True

                #apply gravity
                self.vel_y += GRAVITY
                if self.vel_y > 10 and self.action == 5:
                        self.vel_y
                dy += self.vel_y
                #check for collision
                for tile in world.obstacle_list:
                        #check collision in the x direction
                        if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                                dx = 0
                                #if ai hit wall turn around
                                if self.char_type == 'enemy':
                                    self.direction *= -1
                                    self.move_counter = 0
                        #check for collision in the y direction
                        if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                                #check if below the ground, i.e. jumping
                                if self.vel_y < 0:
                                        self.vel_y = 0
                                        dy = tile[1].bottom - self.rect.top
                                #check if above the ground, i.e. falling
                                elif self.vel_y >= 0:
                                        self.vel_y = 0
                                        self.in_air = False
                                        dy = tile[1].top - self.rect.bottom
                        elif self.alive == False and self.char_type == 'enemy2':
                                dy = tile[1].bottom - 120 - self.rect.top


                #check for collision with platforms
                for platform in platform_group:
                        #collision in x direction
                        if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                                dx = 0
                        #collision in y direction
                        if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                                #check if below platform
                                if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh and self.vel_y < 0:
                                        self.vel_y = 0
                                        dy = platform.rect.bottom - self.rect.top
                                #check if above platform
                                elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                                        self.vel_y = 0
                                        self.in_air = False
                                        self.rect.bottom = platform.rect.top - 1
                                        dy = 0
                                #move with platform
                                if platform.move_x != 0:
                                        if platform.move_direction > 0:
                                                self.rect.x += platform.move_direction + 2
                                        elif platform.move_direction < 0:
                                                self.rect.x += platform.move_direction - 2
                                        
                #check collision with water
                if pygame.sprite.spritecollide(player, lava_group, False):
                    player.health = 0
                    
                #check collision with exit
                level_complete = False
                if pygame.sprite.spritecollide(player, exit_group, False):
                        if player.loading > 0:
                                if player.loading == 1200:
                                        gamefinished_fx.play()
                                if level == 1:
                                        player.loading -=1                                        
                                if level == 2:
                                        player.loading -= .8
                                if level == 3:
                                        player.loading -= .6
                        if player.loading <= 0:
                                if level != 3:
                                        player.health = 0
                                level_complete = True
                #check collision with spikes
                if pygame.sprite.spritecollide(player, spike_group, False):
                        if player.player_spike == 0:
                                player.health -= 10
                                damaged_fx.play()
                                player.player_spike = 100
                                player.update_action(3)
                        player.vel_y = -11
                        player.vel_x = -11
                        
                #check if fallen off the map
                if player.rect.bottom > SCREEN_HEIGHT:
                    player.health = 0
                    
                #check if off edge screen
                if self.char_type == 'player':
                    if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                        dx = 0
                        
                #update rectangle position
                self.rect.x += dx
                self.rect.y += dy

                #update scroll based on player pos
                if self.char_type == 'player':
                    if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                        or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                        self.rect.x -= dx
                        screen_scroll = -dx
                        
                return screen_scroll, level_complete

        #method for player shooting
        def shoot(self):
                if self.shoot_cooldown == 0 and self.ammo > 0 and player.alive:
                        self.shoot_cooldown = 30
                        bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                        bullet_group.add(bullet)
                        #reduce ammo
                        self.ammo -= 1
                        player.update_action(0)
                        shot_fx.play()

        #method for ai shooting
        def ai_shoot(self):
                if self.shoot_cooldown == 0 and self.char_type == 'enemy' and self.alive:
                        if self.direction == 1:
                                ebullet = EnemyBullet(self.rect.centerx - 45 + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                                ebullet_group.add(ebullet)
                                #reduce ammo
                                self.shoots = False
                        elif self.direction == -1:
                                ebullet = EnemyBullet(self.rect.centerx + 45 + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                                ebullet_group.add(ebullet)
                                #reduce ammo
                                self.shoots = False                        
                elif self.shoot_cooldown == 0 and self.char_type == 'enemy2' and self.alive:
                        ebullet2 = Enemy2Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery - 10, self.direction)
                        ebullet_group.add(ebullet2)
                        #reduce ammo
                        self.shoots = False
                        shot_fx.play()

        #method for ai logic and movement
        def ai(self):
                if self.alive:
                        if self.idling == False and random.randint(1, 200) == 1:
                                self.update_action(0)#4: attack
                                self.idling = True
                                self.idling_counter = 50
                        #check if the ai in near the player
                        if self.vision.colliderect(player.rect) and player.alive == True:
                                #stop running and face the player
                                self.view = True
                                self.update_action(4)#4: attack
                                #shoot
                                if self.shoots == False and self.view == True:
                                        if self.shooting == False:
                                                self.shoot_cooldown = 30
                                                self.shooting = True
                                        elif self.shooting == True:
                                            if self.char_type == 'enemy':
                                                self.shoot_cooldown = 35
                                            elif self.char_type == 'enemy2':
                                                self.shoot_cooldown = 60
                                        self.shoots = True
                                self.move(moving_left, moving_right)
                        else:
                                self.view = False
                                self.shoots = False
                                self.shoot_cooldown = 0
                                if self.idling == False:
                                        if self.direction == 1:
                                                ai_moving_right = True
                                        else:
                                                ai_moving_right = False
                                        ai_moving_left = not ai_moving_right
                                        self.move(ai_moving_left, ai_moving_right)
                                        self.update_action(1)#1: run
                                        self.move_counter += 1
                                        #update ai vision as the enemy moves
                                        #pygame.draw.rect(screen, RED, self.vision)
                                        self.vision.center = (self.rect.centerx + 155 * self.direction, self.rect.centery)
                                        if self.move_counter > TILE_SIZE:
                                                self.direction *= -1
                                                self.move_counter *= -1
                                else:
                                        self.idling_counter -= 1
                                        if self.idling_counter <= 0:
                                                self.idling = False
                else:

                        enemy.move(moving_left, moving_right)
                        self.shoots = False
                #scroll
                self.rect.x += screen_scroll
                        
        #method for player and ai animation updates
        def update_animation(self):
                #update animation
                ANIMATION_COOLDOWN = 100
                #update image depending on current frame
                self.image = self.animation_list[self.action][self.frame_index]
                #check if enough time has passed since the last update
                if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                        self.update_time = pygame.time.get_ticks()
                        self.frame_index += 1
                #if the animation has run out the reset back to the start
                if self.frame_index >= len(self.animation_list[self.action]):
                        if self.action == 3:
                                self.frame_index = len(self.animation_list[self.action]) - 1
                        else:
                                self.frame_index = 0

        #method for changing action type
        def update_action(self, new_action):
                #check if the new action is different to the previous one
                if new_action != self.action:
                        self.action = new_action
                        #update the animation settings
                        self.frame_index = 0
                        self.update_time = pygame.time.get_ticks()


        #method for checking if the player or ai is alive
        def check_alive(self):
                if self.health <= 0 or self.time == 0:
                        self.health = 0
                        self.speed = 0
                        self.alive = False
                        self.update_action(3)


        #method for drawing the player or ai in the window
        def draw(self):
                screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            
#method for generation of the world data
class World():
        def __init__(self):
                self.obstacle_list = []

        def process_data(self, data):
            self.level_length = len(data[0])
                #iterate through each value in level data file
            for y, row in enumerate(data):
                    for x, tile in enumerate(row):
                            if tile >= 0:
                                    img = img_list[tile]
                                    img_rect = img.get_rect()
                                    img_rect.x = x * TILE_SIZE
                                    img_rect.y = y * TILE_SIZE
                                    tile_data = (img, img_rect)
                                    if tile >= 0 and tile <= 8:
                                            self.obstacle_list.append(tile_data)
                                    elif tile == 9:
                                            platform = Platform(img, x * TILE_SIZE, y * TILE_SIZE, 0 ,1)
                                            platform_group.add(platform)
                                    elif tile >= 10 and tile <= 11:
                                            lava = Lava(img, x * TILE_SIZE, y * TILE_SIZE)
                                            lava_group.add(lava)
                                    elif tile == 12:
                                            item_box = ItemBox('Coin', x * TILE_SIZE, y * TILE_SIZE)
                                            item_box_group.add(item_box)
                                    elif tile == 13 :
                                            decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                                            decoration_group.add(decoration)
                                    elif tile == 14 :
                                            spike = Spike(img, x * TILE_SIZE, y * TILE_SIZE)
                                            spike_group.add(spike)
                                    elif tile == 15:#create player
                                            player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.4, 4, 20)
                                            health_bar = HealthBar(10, 10, player.health, player.health)
                                    elif tile == 16:#create enemies
                                            enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20)
                                            enemy_group.add(enemy)
                                    elif tile == 18:#create enemies
                                            enemy2 = Soldier('enemy2', x * TILE_SIZE, y * TILE_SIZE, 1.35, 2, 20)
                                            enemy_group.add(enemy2)
                                    elif tile == 17:#create ammo box
                                            item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                                            item_box_group.add(item_box)
                                    elif tile == 19:#create health box
                                            item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                                            item_box_group.add(item_box)
                                    elif tile == 20:#create exit 
                                            exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                                            exit_group.add(exit)
                                    elif tile == 21:
                                            platform = Platform(img, x * TILE_SIZE, y * TILE_SIZE, 1,0)
                                            platform_group.add(platform)
                                        

            return player, health_bar

        #method for creating rectangles for collision and  world images displays
        def draw(self):
                for tile in self.obstacle_list:
                    tile[1][0] += screen_scroll
                    screen.blit(tile[0], tile[1])
                  
#class for decorations
class Decoration(pygame.sprite.Sprite):
        def __init__(self, img, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.image = img
                self.rect = self.image.get_rect()
                self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        def update(self):
            self.rect.x += screen_scroll

#class for platform
class Platform(pygame.sprite.Sprite):
        def __init__(self, img, x, y, move_x, move_y):
                pygame.sprite.Sprite.__init__(self)
                self.image = img
                self.rect = self.image.get_rect()
                self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
                self.rect.x = x
                self.rect.y = y
                self.move_direction = 1
                self.move_counter = 0
                self.move_x = move_x
                self.move_y = move_y
                
        def update(self):
            self.rect.x += screen_scroll
            self.rect.y += self.move_direction * self.move_y
            self.rect.x += self.move_direction * self.move_x
            self.move_counter += 1
            if abs(self.move_counter) > 50:
                    self.move_direction *= -1
                    self.move_counter *= -1

#class for lava
class Lava(pygame.sprite.Sprite):
        def __init__(self, img, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.image = img
                self.rect = self.image.get_rect()
                self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

        def update(self):
            self.rect.x += screen_scroll
            
#class for spike
class Spike(pygame.sprite.Sprite):
        def __init__(self, img, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.image = img
                self.rect = self.image.get_rect()
                self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

        def update(self):
            self.rect.x += screen_scroll
            
#class for coin
class Coin(pygame.sprite.Sprite):
        def __init__(self, img, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.image = img
                self.rect = self.image.get_rect()
                self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

        def update(self):
            self.rect.x += screen_scroll

#class for exit
class Exit(pygame.sprite.Sprite):
        def __init__(self, img, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.image = img
                self.rect = self.image.get_rect()
                self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

        def update(self):
            self.rect.x += screen_scroll

#class for itembox
class ItemBox(pygame.sprite.Sprite):
        def __init__(self, item_type, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.item_type = item_type
                self.image = item_boxes[self.item_type]
                self.rect = self.image.get_rect()
                self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

        def update(self):
            #scroll
            self.rect.x += screen_scroll
                #check if the player has picked up the box
            if pygame.sprite.collide_rect(self, player):
                    #check what kind of box it was
                    if self.item_type == 'Health':
                            player.health += 25
                            pickup_fx.play()
                            if player.health > player.max_health:
                                    player.health = player.max_health
                    elif self.item_type == 'Ammo':
                            player.ammo += 10
                            if player.ammo >= 20:
                                    player.ammo = 20
                            pickup_fx.play()
                    elif self.item_type == 'Coin':
                            player.score += 10
                            pickup_fx.play()
                    #delete the item box
                    self.kill()
#class for healthbar
class HealthBar():
        def __init__(self, x, y, health, max_health):
                self.x = x
                self.y = y
                self.health = health
                self.max_health = max_health

        def draw(self, health):
                #update with new health
                self.health = health
                #calculate health ratio
                ratio = self.health / self.max_health
                pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
                pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
                pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

#class for bullet
class Bullet(pygame.sprite.Sprite):
        def __init__(self, x, y, direction):
                pygame.sprite.Sprite.__init__(self)
                self.speed = 7
                if direction == -1:   
                        self.image = arrow_img
                elif direction == 1:
                        self.image = rightarrow_img
                self.rect = self.image.get_rect()
                self.rect.center = (x, y)
                self.direction = direction

        def update(self):
                #move bullet
                self.rect.x += (self.direction * self.speed) + screen_scroll
                #check if bullet has gone off screen
                if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                        self.kill()
                #check for collision with level
                for tile in world.obstacle_list:
                        if tile[1].colliderect(self.rect):
                                self.kill()
                #check collision with characters
                for enemy in enemy_group:
                        if pygame.sprite.spritecollide(enemy, bullet_group, False):
                                if enemy.alive:
                                        enemy.health -= 25
                                        if enemy.health == 0:
                                            player.score += 10
                                            score = player.score
                                        self.kill()
                  #class for enemybullet
class EnemyBullet(pygame.sprite.Sprite):
        def __init__(self, x, y, direction):
                pygame.sprite.Sprite.__init__(self)
                self.speed = 7
                if direction == -1:   
                        self.image = leftfireball_img
                elif direction == 1:
                        self.image = rightfireball_img
                self.rect = self.image.get_rect()
                self.rect.center = (x, y)
                self.direction = direction

        def update(self):
                #move bullet
                self.rect.x += (self.direction * self.speed) + screen_scroll
                #check if bullet has gone off screen
                if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                        self.kill()
                #check for collision with level
                for tile in world.obstacle_list:
                        if tile[1].colliderect(self.rect):
                                self.kill()

                #check collision with characters
                if pygame.sprite.spritecollide(player, ebullet_group, False):
                        if player.alive:
                                player.health -= 10
                                self.kill()


#class for enemy2bullet
class Enemy2Bullet(pygame.sprite.Sprite):
        def __init__(self, x, y, direction):
                pygame.sprite.Sprite.__init__(self)
                self.speed = 7
                if direction == -1:   
                        self.image = earrow_img
                elif direction == 1:
                        self.image = rightearrow_img
                self.rect = self.image.get_rect()
                self.rect.center = (x, y)
                self.direction = direction

        def update(self):
                #move bullet
                self.rect.x += (self.direction * self.speed) + screen_scroll
                #check if bullet has gone off screen
                if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                        self.kill()
                #check for collision with level
                for tile in world.obstacle_list:
                        if tile[1].colliderect(self.rect):
                                self.kill()

                #check collision with characters
                if pygame.sprite.spritecollide(player, ebullet_group, False):
                        if player.alive:
                                player.health -= 15
                                self.kill()
                          
#class for screentransitions
class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1: #whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH //  2 , SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0,0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0,SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
            
        if self.direction == 2: #vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0,0, SCREEN_WIDTH, 0 + self.fade_counter))

            
        if (self.fade_counter >= 2000 and self.direction == 3) or (self.fade_counter >= 400 and self.direction == 1) or (self.fade_counter >= 800 and self.direction == 2):
            fade_complete = True
            
        if self.direction == 3: #vertical screen side slide
            pygame.draw.rect(screen, self.colour, (-1100 + self.fade_counter, 0, SCREEN_WIDTH + 300, SCREEN_HEIGHT))
         
        return fade_complete
        

#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, DARKRED, 4)
enter_fade = ScreenFade(3, BLACK, 6)

#create button
start_button = button.Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 , start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 85, SCREEN_HEIGHT // 2 + 190, exit_img, 1)
exit1_button = button.Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 100, exit_img, 1)
exit2_button = button.Button(SCREEN_WIDTH // 2 - 85, SCREEN_HEIGHT // 2 + 170, exit_img, 1)
play_button = button.Button(SCREEN_WIDTH // 2 - 85, SCREEN_HEIGHT // 2 + 210, play_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 102, SCREEN_HEIGHT // 2 + 70, restart_img, 1)
restart_button2 = button.Button(SCREEN_WIDTH // 2 - 105, SCREEN_HEIGHT // 2 + 180, restart_img, 1)

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
ebullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create empty tile list
world_data = []
for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)

#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
        print(level)
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)
                                

run = True
#gameloop
while run:
        clock.tick(FPS)
        if start_game == False and level < 3 and instruction == False:
            #main menu
            draw_bgmain()
            screen.blit(mh_img, (70, -20))
            #buttons
            if start_button.draw(screen):
                    instruction = True
            if exit1_button.draw(screen):
                run = False
            for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                run = False
                        #keyboard presses
                        if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_m:
                                        if mute == False:
                                                mute = True
                                                pygame.mixer.music.set_volume(0)
                                                jump_fx.set_volume(0)
                                                shot_fx.set_volume(0)
                                                gameover_fx.set_volume(0)
                                                gamefinished_fx.set_volume(0)
                                                pickup_fx.set_volume(0)
                                        elif mute == True:
                                                mute = False
                                                pygame.mixer.music.set_volume(0.3)
                                                jump_fx.set_volume(0.5)
                                                shot_fx.set_volume(0.5)
                                                gameover_fx.set_volume(1)
                                                gamefinished_fx.set_volume(1)
                                                pickup_fx.set_volume(1)
        #instructions
        elif start_game == False and instruction == True:
                draw_bgmain()
                draw_text(f'Instructions:', font, ORANGE, 260, 30, .8)
                draw_text(f'Press "W" to Jump', font, ORANGE, 180, 90, .7)
                draw_text(f'Press "A" to Move left', font, ORANGE, 180, 140, .7)
                draw_text(f'Press "D" to Move right', font, ORANGE, 180, 190, .7)
                draw_text(f'Press "Space" to Shoot', font, ORANGE, 180, 240, .7)
                draw_text(f'Press "M" to Mute all sound', font, ORANGE, 180, 290, .7)
                draw_text(f'Press "ESC" to pause', font, ORANGE, 180, 340, .7)
                draw_text(f'Objective:', font, ORANGE, 295, 400, .8)
                draw_text(f'Finish all 3 levels', font, ORANGE, 180, 460, .7)
                if play_button.draw(screen):
                        pause = False
                        start_intro = True
                        screen_scroll = 0
                        bg_scroll = 0
                        world_data = reset_level()
                        #load in level data and create world
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                                reader = csv.reader(csvfile, delimiter=',')
                                for x, row in enumerate(reader):
                                        for y, tile in enumerate(row):
                                                world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
                        instruction = False
                        pygame.mixer.music.load('audio/Underclocked.mp3')
                        if mute == False:
                                pygame.mixer.music.set_volume(0.3)
                        elif mute == True:
                                pygame.mixer.music.set_volume(0)
                        pygame.mixer.music.play(-1, 0.0)
                        start_game = True
                        start_intro = True
                for event in pygame.event.get():
                        # keyboard presses
                        if event.type == pygame.QUIT:
                                run = False
                        if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_m:
                                        if mute == False:
                                                mute = True
                                                pygame.mixer.music.set_volume(0)
                                                jump_fx.set_volume(0)
                                                shot_fx.set_volume(0)
                                                gameover_fx.set_volume(0)
                                                gamefinished_fx.set_volume(0)
                                                pickup_fx.set_volume(0)
                                        elif mute == True:
                                                mute = False
                                                pygame.mixer.music.set_volume(0.3)
                                                jump_fx.set_volume(0.5)
                                                shot_fx.set_volume(0.5)
                                                gameover_fx.set_volume(1)
                                                gamefinished_fx.set_volume(1)
                                                pickup_fx.set_volume(1)
        #gamefinished
        elif start_game == False and level >= 3:
                draw_bg()
                pygame.mixer.music.set_volume(0)
                screen.blit(gamefinish_img, (110,120))
                pygame.draw.rect(screen, ORANGE, (175, 365, 455, 90))
                pygame.draw.rect(screen, BLACK, (180, 370, 445, 80))
                draw_text(f'Your Score:{player.score}', font, ORANGE, 220, 395, 1)
                if exit_button.draw(screen):
                        level = 1
                        pygame.mixer.music.load('audio/DizzySpells.mp3')
                        pygame.mixer.music.set_volume(0.1)
                        pygame.mixer.music.play(-1, 0.0)
                        
#
        #start gameplay
        elif start_game == True:
            #update background
            if pause == False and player.alive:
                draw_bg()
                #draw world map
                world.draw()
                #show player health
                health_bar.draw(player.health)
                #show ammo                
                draw_text('Arrow:    ', font, WHITE, 10, 45, .75)
                for x in range(player.ammo):
                        screen.blit(bullet_img, (130 + (x * 15), 43))
                draw_text(f'Score: {player.score}', font, WHITE, 600, 20, .6)
                draw_text(f'Timer: {player.time}', font, WHITE, 599, 50, .6)
                draw_text(f'Level: {level}', font, WHITE, 603, 80, .6)

                player.update()
                player.draw()

                for enemy in enemy_group:
                        enemy.ai()
                        enemy.update()
                        enemy.draw()

            #update and draw groups
                bullet_group.update()
                ebullet_group.update()
                item_box_group.update()
                decoration_group.update()
                platform_group.update()
                lava_group.update()
                spike_group.update()
                exit_group.update()
                bullet_group.draw(screen)
                ebullet_group.draw(screen)
                item_box_group.draw(screen)
                decoration_group.draw(screen)
                platform_group.draw(screen)
                lava_group.draw(screen)
                spike_group.draw(screen)
                exit_group.draw(screen)

                if level == 1:
                        screen.blit(level1_img, (250, 300))
                        
                        level1_img.set_alpha(player.levelanimation)
                if level == 2:
                        screen.blit(level2_img, (250, 300))
                        level2_img.set_alpha(player.levelanimation)
                if level == 3:
                        screen.blit(level3_img, (250, 300))
                        level3_img.set_alpha(player.levelanimation)
                if level == 4:
                        screen.blit(level4_img, (250, 300))
                        level4_img.set_alpha(player.levelanimation)
                if level == 5:
                        screen.blit(level5_img, (250, 300))
                        level5_img.set_alpha(player.levelanimation)
                if player.levelanimation > 0:
                        player.levelanimation -= 4
            #show intro
            if start_intro == True:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0
                    ingame = True
            #show enter level
            if enter_level == True:
                if enter_fade.fade():
                    enter_level = False
                    enter_fade.fade_counter = 0
                    ingame = True
                    
            #update player actions
            if player.alive:
                    #shoot bullets
                    if player.shoot_cooldown == 0 and shoot == True:
                            player.shoot()
                            shoot = False
                    if player.in_air:
                            player.update_action(2)#2: jump
                    elif moving_left or moving_right:
                            player.update_action(1)#1: run
                    elif shoot == True:
                            player.update_action(4)#1: attack
                    else:
                            player.update_action(0)#0: idle
                            
                    screen_scroll, level_complete = player.move(moving_left, moving_right)
                    bg_scroll -= screen_scroll
                    
                    if player.loading < 1150:
                           enter_level = True
                           
                    #check if level is complete
                    if level_complete:
                        if level < 3:
                                score = player.score + player.time
                                player.time = 60
                                level += 1
                                ingame = True
                                bg_scroll = 0
                                if level == 3:
                                        time = 160
                                world_data = reset_level()
                                if level <= MAX_LEVELS:
                                    #load in level data and create world
                                    with open(f'level{level}_data.csv', newline='') as csvfile:
                                            reader = csv.reader(csvfile, delimiter=',')
                                            for x, row in enumerate(reader):
                                                    for y, tile in enumerate(row):
                                                            world_data[x][y] = int(tile)
                                    world = World()
                                    player, health_bar = world.process_data(world_data)
                        elif level >= 3:
                                start_game = False

            #player death
            else:
                player.update_action(2)
                pygame.mixer.music.pause()
                if death == False:
                        death = True
                        gameover_fx.play()
                        print(death)
                screen_scroll = 0
                if death_fade.fade():
                        screen.blit(gameover_img, (210,60))
                        pygame.draw.rect(screen, ORANGE, (175, 365, 455, 90))
                        pygame.draw.rect(screen, BLACK, (180, 370, 445, 80))
                        if player.score < 100:
                                draw_text(f'Your Score:{player.score}', font, ORANGE, 220, 390, 1)
                        if player.score >= 100:
                                draw_text(f'Your Score:{player.score}', font, ORANGE, 190, 390, 1)
                        if restart_button2.draw(screen):
                            death = False
                            pygame.mixer.music.play(-1, 0.0)
                            death_fade.fade_counter = 0
                            start_intro = True
                            bg_scroll = 0
                            world_data = reset_level()
                            #load in level data and create world
                            with open(f'level{level}_data.csv', newline='') as csvfile:
                                    reader = csv.reader(csvfile, delimiter=',')
                                    for x, row in enumerate(reader):
                                            for y, tile in enumerate(row):
                                                    world_data[x][y] = int(tile)
                            world = World()
                            player, health_bar = world.process_data(world_data)
                            
        for event in pygame.event.get():
                #quit game
                if event.type == pygame.QUIT:
                        run = False
                #keyboard presses
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a and player.alive and pause == False and ingame == True and player.loading == 1200:
                                moving_left = True
                                shoot = False
                        if event.key == pygame.K_d and player.alive and pause == False and ingame == True and player.loading == 1200:
                                moving_right = True
                                shoot = False
                        if event.key == pygame.K_SPACE and shoot == False and ingame == True and player.loading == 1200:
                                moving_right = False
                                moving_left = False
                                shoot = True
                                player.shoot_cooldown = 30
                        if event.key == pygame.K_w and player.alive and pause == False and ingame == True and player.loading == 1200:
                                player.jump = True
                                jump_fx.play()
                        if event.key == pygame.K_ESCAPE and start_game == True and player.health != 0:
                                if ingame == True:
                                    if pause == False:
                                        pause = True
                                        pygame.mixer.music.set_volume(0)
                                    elif pause == True:
                                        pause = False
                                        if mute == False:
                                                pygame.mixer.music.set_volume(0.3)
                                        elif mute == True:
                                                pygame.mixer.music.set_volume(0)
                        if event.key == pygame.K_m and start_game == True and player.health != 0 and pause == False:
                                if mute == False:
                                        mute = True
                                        pygame.mixer.music.set_volume(0)
                                        jump_fx.set_volume(0)
                                        shot_fx.set_volume(0)
                                        gameover_fx.set_volume(0)
                                        gamefinished_fx.set_volume(0)
                                        pickup_fx.set_volume(0)
                                elif mute == True:
                                        mute = False
                                        pygame.mixer.music.set_volume(0.3)
                                        jump_fx.set_volume(0.5)
                                        shot_fx.set_volume(0.5)
                                        gameover_fx.set_volume(1)
                                        gamefinished_fx.set_volume(1)
                                        pickup_fx.set_volume(1)
                                
                if pause == True:
                    draw_bg()
                    moving_right = False
                    moving_left = False
                    screen.blit(gamepause_img, (185, 100))
                    draw_text(f'Press "ESC" to resume', font, ORANGE, 165, 320, .8)
                    if exit2_button.draw(screen):
                        run = False
                    if restart_button.draw(screen):
                        pygame.mixer.music.load('audio/Underclocked.mp3')
                        pygame.mixer.music.play(-1, 0.0)
                        if mute == False:
                                pygame.mixer.music.set_volume(0.3)
                        elif mute == True:
                                pygame.mixer.music.set_volume(0)
                        pause = False
                        start_intro = True
                        screen_scroll = 0
                        bg_scroll = 0
                        world_data = reset_level()
                        #load in level data and create world
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                                reader = csv.reader(csvfile, delimiter=',')
                                for x, row in enumerate(reader):
                                        for y, tile in enumerate(row):
                                                world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)

                        
                #keyboard button released
                if event.type == pygame.KEYUP:
                        if event.key == pygame.K_a:
                                moving_left = False
                        if event.key == pygame.K_d:
                                moving_right = False

        pygame.display.update()

pygame.quit()
