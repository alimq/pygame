import pygame
import os
import random

def load_image(name, colorkey=None):
    fullname = os.path.join('', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

running = True
pygame.init()
size = w, h = 800, 600
screen = pygame.display.set_mode(size)
keys = {32: 'jump',
        274: 'down',
        275: 'right',
        276: 'left'}

user_score = 0
all_sprites = pygame.sprite.Group()
obstacle_sprites = pygame.sprite.Group()
vertical_sprites = pygame.sprite.Group()
horizontal_sprites = pygame.sprite.Group()
hero_sprites = pygame.sprite.Group()
bomb_sprites = pygame.sprite.Group()
drop_sprites = pygame.sprite.Group()
trap_sprites = pygame.sprite.Group()
distance = -370
flag = False

all_obstacles = []
all_verticals = []
all_horizontals = []
all_drops = []
all_bombs = []
all_traps = []

def update_user_score():
    global user_score
    font = pygame.font.Font(None, 22)
    label = 'Score: ' + str(user_score)
    text = font.render(label, 1, pygame.Color('darkgreen'))
    screen.blit(text, (25, 30))
    
def user_lost():
    global running
    screen.fill(pygame.Color('white'))
    font = pygame.font.Font(None, 50)
    label = 'You lost! Score: ' + str(user_score)
    text = font.render(label, 1, pygame.Color('red'))
    screen.blit(text, (250, 250))    
    pygame.display.flip()
    running = False
    pygame.time.delay(100000)
    
def user_won():
    global running
    screen.fill(pygame.Color('white'))
    font = pygame.font.Font(None, 50)
    label = 'You won! Score: ' + str(user_score)
    text = font.render(label, 1, pygame.Color('darkgreen'))
    screen.blit(text, (250, 250))    
    pygame.display.flip()
    running = False
    pygame.time.delay(100000)

class Vertical:
    def __init__(self, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = load_image('vertical.png')
        self.sprite.rect = self.sprite.image.get_rect()
        all_sprites.add(self.sprite)
        vertical_sprites.add(self.sprite)
        self.x = x
        self.y = y
        self.sprite.rect.x = x
        self.sprite.rect.y = y 
        
    def move(self):
        self.sprite.rect.x = self.x - distance   
        
class Horizontal:
    def __init__(self, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = load_image('horizontal.png')
        self.sprite.rect = self.sprite.image.get_rect()
        all_sprites.add(self.sprite)
        horizontal_sprites.add(self.sprite)
        self.x = x
        self.y = y
        self.sprite.rect.x = x
        self.sprite.rect.y = y 
        
    def move(self):
        self.sprite.rect.x = self.x - distance   

class Obstacle:
    def __init__(self, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = load_image('obstacle.png')
        self.sprite.rect = self.sprite.image.get_rect()
        all_sprites.add(self.sprite)
        obstacle_sprites.add(self.sprite)
        self.x = x
        self.y = y
        self.sprite.rect.x = x
        self.sprite.rect.y = y
        all_verticals.append(Vertical(self.x - 4, self.y + 5))
        all_verticals.append(Vertical(self.x + 101, self.y + 5))
        all_horizontals.append(Horizontal(self.x, self.y + 80))      
        self.fallen = 0
        
    def move(self):
        self.sprite.rect.x = self.x - distance 
        
        
class Trap:
    def __init__(self, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = load_image('trap.png')
        self.sprite.rect = self.sprite.image.get_rect()
        all_sprites.add(self.sprite)
        trap_sprites.add(self.sprite)
        self.x = x
        self.y = y
        self.sprite.rect.x = x
        self.sprite.rect.y = y
        all_horizontals.append(Horizontal(self.x, self.y + 80))        
        
    def move(self):
        self.sprite.rect.x = self.x - distance     

def update_obstacles():
    for obstacle in all_obstacles:
        obstacle.move()
    for vertical in all_verticals:
        vertical.move()  
    for horizontal in all_horizontals:
        horizontal.move()
    for drop in all_drops:
        drop.move()
    for bomb in all_bombs:
        bomb.move()    
    for trap in all_traps:
        trap.move()
        
def update_obstacles2():
    for obstacle in all_obstacles:
        obstacle.move()
    for vertical in all_verticals:
        vertical.move()  
    for horizontal in all_horizontals:
        horizontal.move()
    for drop in all_drops:
        drop.move2()
    for bomb in all_bombs:
        bomb.move2()    
    for trap in all_traps:
        trap.move()

class Hero:
    def __init__(self, src):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = load_image(src)
        self.sprite.rect = self.sprite.image.get_rect()
        all_sprites.add(self.sprite)
        hero_sprites.add(self.sprite)
        self.sprite.rect.x = 370
        self.sprite.rect.y = 520
        self.jump = False
        self.right = False
        self.left = False
        self.fall = False
        self.jumping_order = [-15, -14, -13, -12, -10, -8, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 8, 10, 12, 13, 14, 15]
        self.jumping_index = 0
        
    def on_keydown(self, key):
        direction = keys.get(key, '')
        if direction == 'jump':
            self.jump = True
        elif direction == 'right':
            self.right = True
        elif direction == 'left':
            self.left = True
            
    def on_keyup(self, key):
        direction = keys.get(key, '')
        if direction == 'right':
            self.right = False
        elif direction == 'left':
            self.left = False
            
    def move(self):
        if pygame.sprite.spritecollideany(self.sprite, trap_sprites):
            user_lost()
            return
        
        if self.sprite.rect.y > 520:
            self.sprite.rect.y = 520
            self.fall = False
            self.jump = False
        if self.jump == True:
            if self.jumping_index >= len(self.jumping_order):
                self.jumping_index = 0
                self.jump = False
                return
            self.sprite.rect.y += self.jumping_order[self.jumping_index]
            self.jumping_index += 1
            if pygame.sprite.spritecollideany(self.sprite, horizontal_sprites):
                self.jumping_index -= 1
                self.sprite.rect.y -= self.jumping_order[self.jumping_index]
                self.jump = False                    
            if pygame.sprite.spritecollideany(self.sprite, obstacle_sprites):
                self.jumping_index = 0
                self.jump = False        
        global distance
        if self.right == True:
            distance += 4
            update_obstacles2()       
            if pygame.sprite.spritecollideany(self.sprite, vertical_sprites):
                distance -= 4        
        if self.left == True:
            distance -= 4   
            update_obstacles2()            
            if pygame.sprite.spritecollideany(self.sprite, vertical_sprites):
                distance += 4           
        if self.jump or pygame.sprite.spritecollideany(self.sprite, obstacle_sprites) or self.sprite.rect.y >= 520:
            self.fall = False
        else:
            self.fall = True
        if self.fall:
            self.sprite.rect.y += 8
            
class Drop:
    def __init__(self):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = load_image('drop.png')
        self.sprite.rect = self.sprite.image.get_rect()
        all_sprites.add(self.sprite)
        drop_sprites.add(self.sprite)
        self.x = random.randint(distance, distance + 800)
        self.y = 0
        self.sprite.rect.x = self.x
        self.sprite.rect.y = self.y    
        self.dropped = False
        
    def move(self):
        global user_score
        self.sprite.rect.y += random.randint(1, 5)
        if (self.sprite.rect.y > 600 or pygame.sprite.spritecollideany(self.sprite, obstacle_sprites)):
            self.sprite.kill()
            self.dropped = True
        if pygame.sprite.spritecollideany(self.sprite, hero_sprites) and not self.dropped:
            self.sprite.kill()
            self.dropped = True
            
            user_score += 100
            update_user_score()
            if (user_score >= 500):
                user_won()
        self.sprite.rect.x = self.x - distance 
        
    def move2(self):
        global user_score
        if (self.sprite.rect.y > 600 or pygame.sprite.spritecollideany(self.sprite, obstacle_sprites)):
            self.sprite.kill()
            self.dropped = True
        if pygame.sprite.spritecollideany(self.sprite, hero_sprites) and not self.dropped:
            self.sprite.kill()
            self.dropped = True
            
            user_score += 100
            update_user_score()
            if (user_score >= 500):
                user_won()
        self.sprite.rect.x = self.x - distance     
        
        
class Bomb:
    def __init__(self):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = load_image('bomb.png')
        self.sprite.rect = self.sprite.image.get_rect()
        all_sprites.add(self.sprite)
        bomb_sprites.add(self.sprite)
        self.x = random.randint(distance, distance + 800)
        self.y = 0
        self.sprite.rect.x = self.x
        self.sprite.rect.y = self.y    
        self.dropped = False
        
    def move(self):
        self.sprite.rect.y += random.randint(2, 7)
        if (self.sprite.rect.y > 600 or pygame.sprite.spritecollideany(self.sprite, obstacle_sprites)):
            self.sprite.kill()
            self.dropped = True
        if pygame.sprite.spritecollideany(self.sprite, hero_sprites) and not self.dropped:
            self.sprite.kill()
            self.dropped = True
            user_lost()
            return
        self.sprite.rect.x = self.x - distance 
        
    def move2(self):
        if (self.sprite.rect.y > 600 or pygame.sprite.spritecollideany(self.sprite, obstacle_sprites)):
            self.sprite.kill()
            self.dropped = True
        if pygame.sprite.spritecollideany(self.sprite, hero_sprites) and not self.dropped:
            self.sprite.kill()
            self.dropped = True
            user_lost()
            return
        self.sprite.rect.x = self.x - distance     
        

fps = 60
clock = pygame.time.Clock()
hero = Hero('hero.png')
all_obstacles.append(Obstacle(100, 520))
all_obstacles.append(Obstacle(200, 520))
all_obstacles.append(Obstacle(300, 520))
all_obstacles.append(Obstacle(400, 440))
all_traps.append(Trap(450, 570))
all_traps.append(Trap(525, 570))
all_traps.append(Trap(600, 570))
all_obstacles.append(Obstacle(570, 360))
all_obstacles.append(Obstacle(700, 280))
all_obstacles.append(Obstacle(640, 470))
all_obstacles.append(Obstacle(760, 520))
all_obstacles.append(Obstacle(890, 510))
all_obstacles.append(Obstacle(1090, 495))
all_traps.append(Trap(1190, 570))
all_traps.append(Trap(1265, 570))
all_traps.append(Trap(1340, 570))
all_obstacles.append(Obstacle(1220, 410))
all_obstacles.append(Obstacle(1330, 410))
all_obstacles.append(Obstacle(1600, 315))
all_obstacles.append(Obstacle(1580, 315))
all_traps.append(Trap(1450, 480))
all_obstacles.append(Obstacle(1450, 510))
all_obstacles.append(Obstacle(1600, 520))
all_obstacles.append(Obstacle(1790, 430))
all_obstacles.append(Obstacle(1930, 480))
all_obstacles.append(Obstacle(2150, 440))
all_obstacles.append(Obstacle(2450, 520))
all_obstacles.append(Obstacle(2550, 520))
all_obstacles.append(Obstacle(2650, 520))
all_obstacles.append(Obstacle(2750, 440))
all_traps.append(Trap(2800, 570))
all_traps.append(Trap(2875, 570))
all_traps.append(Trap(2950, 570))
all_obstacles.append(Obstacle(2920, 360))
all_obstacles.append(Obstacle(3050, 280))
all_obstacles.append(Obstacle(2990, 470))
all_obstacles.append(Obstacle(3110, 520))
all_obstacles.append(Obstacle(3240, 510))
all_obstacles.append(Obstacle(3340, 495))
all_traps.append(Trap(3440, 570))
all_traps.append(Trap(3515, 570))
all_traps.append(Trap(3590, 570))
all_obstacles.append(Obstacle(3470, 410))
all_obstacles.append(Obstacle(3580, 410))
all_obstacles.append(Obstacle(3850, 315))
all_obstacles.append(Obstacle(3830, 315))
all_traps.append(Trap(3700, 480))
all_obstacles.append(Obstacle(3700, 510))
all_obstacles.append(Obstacle(3850, 520))
all_obstacles.append(Obstacle(4040, 430))
all_obstacles.append(Obstacle(4180, 480))
all_obstacles.append(Obstacle(4400, 440))
all_obstacles.append(Obstacle(4600, 440))
all_traps.append(Trap(4700, 570))
all_traps.append(Trap(4800, 570))
all_traps.append(Trap(4900, 570))


if pygame.sprite.spritecollideany(hero.sprite, drop_sprites):
    all_obstacles.append(Obstacle(100, 520))
    all_obstacles.append(Obstacle(200, 520))
    all_obstacles.append(Obstacle(300, 520))
    all_obstacles.append(Obstacle(400, 440))
    all_traps.append(Trap(450, 570))
    all_traps.append(Trap(525, 570))
    all_traps.append(Trap(600, 570))
    all_obstacles.append(Obstacle(570, 360))
    all_obstacles.append(Obstacle(700, 280))
    all_obstacles.append(Obstacle(640, 470))
    all_obstacles.append(Obstacle(760, 520))
    all_obstacles.append(Obstacle(890, 510))
    all_obstacles.append(Obstacle(1090, 495))
    all_traps.append(Trap(1190, 570))
    all_traps.append(Trap(1265, 570))
    all_traps.append(Trap(1340, 570))
    all_obstacles.append(Obstacle(1220, 410))
    all_obstacles.append(Obstacle(1330, 410))
    all_obstacles.append(Obstacle(1600, 315))
    all_obstacles.append(Obstacle(1580, 315))
    all_traps.append(Trap(1450, 480))
    all_obstacles.append(Obstacle(1450, 510))
    all_obstacles.append(Obstacle(1600, 520))
    all_obstacles.append(Obstacle(1790, 430))
    all_obstacles.append(Obstacle(1930, 480))
    all_obstacles.append(Obstacle(2150, 440))
    all_obstacles.append(Obstacle(2450, 520))
    all_obstacles.append(Obstacle(2550, 520))
    all_obstacles.append(Obstacle(2650, 520))
    all_obstacles.append(Obstacle(2750, 440))
    all_traps.append(Trap(2800, 570))
    all_traps.append(Trap(2875, 570))
    all_traps.append(Trap(2950, 570))
    all_obstacles.append(Obstacle(2920, 360))
    all_obstacles.append(Obstacle(3050, 280))
    all_obstacles.append(Obstacle(2990, 470))
    all_obstacles.append(Obstacle(3110, 520))
    all_obstacles.append(Obstacle(3240, 510))
    all_obstacles.append(Obstacle(3340, 495))
    all_traps.append(Trap(3440, 570))
    all_traps.append(Trap(3515, 570))
    all_traps.append(Trap(3590, 570))
    all_obstacles.append(Obstacle(3470, 410))
    all_obstacles.append(Obstacle(3580, 410))
    all_obstacles.append(Obstacle(3850, 315))
    all_obstacles.append(Obstacle(3830, 315))
    all_traps.append(Trap(3700, 480))
    all_obstacles.append(Obstacle(3700, 510))
    all_obstacles.append(Obstacle(3850, 520))
    all_obstacles.append(Obstacle(4040, 430))
    all_obstacles.append(Obstacle(4180, 480))
    all_obstacles.append(Obstacle(4400, 440))
    all_obstacles.append(Obstacle(4600, 440))
    all_traps.append(Trap(4700, 570))
    all_traps.append(Trap(4800, 570))
    all_traps.append(Trap(4900, 570))
    all_obstacles.append(Obstacle(1580, 315))
    all_traps.append(Trap(1450, 480))
    all_obstacles.append(Obstacle(1450, 510))
    all_obstacles.append(Obstacle(1600, 520))
    all_obstacles.append(Obstacle(1790, 430))
    all_obstacles.append(Obstacle(1930, 480))
    all_obstacles.append(Obstacle(2150, 440))
    all_obstacles.append(Obstacle(2450, 520))
    all_obstacles.append(Obstacle(2550, 520))
    all_obstacles.append(Obstacle(2650, 520))
    all_obstacles.append(Obstacle(2750, 440))
    all_traps.append(Trap(2800, 570))
    all_traps.append(Trap(2875, 570))
    all_traps.append(Trap(2950, 570))
    all_obstacles.append(Obstacle(2920, 360))
    all_obstacles.append(Obstacle(3050, 280))
    all_obstacles.append(Obstacle(2990, 470))
    all_obstacles.append(Obstacle(3110, 520))
    all_obstacles.append(Obstacle(3240, 510))
    all_obstacles.append(Obstacle(3340, 495))
    all_traps.append(Trap(3440, 570))
    all_traps.append(Trap(3515, 570))
    all_traps.append(Trap(3590, 570))
    all_obstacles.append(Obstacle(3470, 410))
    all_obstacles.append(Obstacle(3580, 410))
    all_obstacles.append(Obstacle(3850, 315))
    all_obstacles.append(Obstacle(3830, 315))
    all_traps.append(Trap(3700, 480))
    all_obstacles.append(Obstacle(3700, 510))
    all_obstacles.append(Obstacle(3850, 520))
    all_obstacles.append(Obstacle(4040, 430))
    all_obstacles.append(Obstacle(4180, 480))
    all_obstacles.append(Obstacle(4400, 440))
    all_obstacles.append(Obstacle(4600, 440))
    all_traps.append(Trap(4700, 570))
    all_traps.append(Trap(4800, 570))
    all_traps.append(Trap(4900, 570))      




background = load_image('background.jpg')

while running:
    screen.blit(background, (0, 0))
    update_user_score()
    hero.move()
    if random.randint(1, 270) == 1:
        all_drops.append(Drop())
    if random.randint(1, 100) == 1:
        all_bombs.append(Bomb())    
    update_obstacles()
    update_obstacles2()
    all_sprites.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            hero.on_keydown(event.key)
        if event.type == pygame.KEYUP:
            hero.on_keyup(event.key)        
    pygame.display.flip()
    clock.tick(fps)