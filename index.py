import pygame
import random
import math

pygame.init()

WIDTH = 1000
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
game1 = True
game = True
bg = pygame.image.load("galaxy.png")
ship1image = pygame.image.load("spaceship1.png")
ship1image = pygame.transform.scale(ship1image,(100, 100))
ship1image = pygame.transform.rotate(ship1image,90)
ship = pygame.image.load("spaceship.png")
ship = pygame.transform.scale(ship,(100, 100))
ship = pygame.transform.rotate(ship,270)
gun = pygame.mixer.Sound("gun.mp3")

red_bullets = pygame.sprite.Group()
yellow_bullets = pygame.sprite.Group()
font = pygame.font.SysFont(None, 22)

class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.rect = pygame.Rect(x, y, 10, 5)
        
    def update(self):
        if self.color == "red":
            self.rect.x += 5
            if self.rect.x > WIDTH:
                self.kill()
        if self.color == "yellow":
            self.rect.x -= 5
            if self.rect.x < 0:
                self.kill()

class prop(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__() 
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.health = 100
        
        if self.color == "red":
            self.image = ship1image
        if self.color == "yellow":
            self.image = ship
            
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x, self.y
        self.speed = 400

    def update(self, dt, keys):
        dx, dy = 0, 0
        if self.color == "red":
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
        elif self.color == "yellow":
            if keys[pygame.K_UP]: dy -= 1
            if keys[pygame.K_DOWN]: dy += 1
            if keys[pygame.K_LEFT]: dx -= 1
            if keys[pygame.K_RIGHT]: dx += 1
            
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        
        self.x = max(0, min(WIDTH - self.rect.width, self.x))
        self.y = max(0, min(HEIGHT - self.rect.height, self.y))
        
        if self.color == "yellow":
            self.x = max(500, min(WIDTH - self.rect.width, self.x))
        if self.color == "red":
            self.x = max(0, min(490 - self.rect.width, self.x))
            
        self.rect.topleft = (self.x, self.y)

redship = prop(WIDTH/4, HEIGHT/2, "red")
yellowship = prop(WIDTH*3/4, HEIGHT/2, "yellow")

running = True

while running:
    t = clock.tick(60) / 1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets = bullet(redship.rect.x, redship.rect.y + 45.4, "red")
                red_bullets.add(bullets)
                gun.play()
            if event.key == pygame.K_RSHIFT:
                bullets = bullet(yellowship.rect.x, yellowship.rect.y + 45.4, "yellow")
                yellow_bullets.add(bullets)
                gun.play()
                
    keys = pygame.key.get_pressed()
    
    redship.update(t, keys)
    yellowship.update(t, keys)

    screen.blit(bg, (0,0))
    
    pygame.draw.rect(screen, (80, 80, 80), (50, 50, 200, 20))
    pygame.draw.rect(screen, (255, 0, 0), (50, 50, redship.health * 2, 20))
    
    pygame.draw.rect(screen, (80, 80, 80), (750, 50, 200, 20))
    pygame.draw.rect(screen, (255, 217, 0), (750, 50, yellowship.health * 2, 20))
    
    pygame.draw.rect(screen, "#FFFFFF", (490, 0, 10, 800))
    screen.blit(redship.image, redship.rect.topleft)
    screen.blit(yellowship.image, yellowship.rect.topleft)
    if game == True:
        yellow_bullets.update()
        yellow_bullets.update()
    if game1 == True:
        red_bullets.update()
        red_bullets.update()
    if game == False:
        for b in yellow_bullets:
            b.kill()
    if game1 == False:
        for b1 in red_bullets:
            b1.kill()
    for b in red_bullets:
        pygame.draw.rect(screen, "red", b.rect)
        if b.rect.colliderect(yellowship.rect):
            yellowship.health -= 20
            red_bullets.remove(b)
        for b1 in yellow_bullets:
            if b1.rect.colliderect(b.rect):
                red_bullets.remove(b)
                yellow_bullets.remove(b1)
        if yellowship.health <= 0:
            game = False
    for b in yellow_bullets:
        pygame.draw.rect(screen, "yellow", b.rect)
        if b.rect.colliderect(redship.rect):
            redship.health -= 20
            yellow_bullets.remove(b)
            if redship.health <= 0:
                game1 = False
    pygame.display.flip()

pygame.quit()