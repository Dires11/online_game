import pygame 
from map import *

class Player():
    def __init__(self, screen,  name, radius, color, x, y):
        self.screen = screen
        self.name = name
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y
        


    def draw_player(self, coords):
        return pygame.draw.circle(self.screen, self.color, (self.x-coords.x, self.y-coords.y), (self.radius))

    def move(self, event):
        keys=pygame.key.get_pressed()
        
        if keys[pygame.K_d]:
            self.x += 6
        if keys[pygame.K_a]:
            self.x -= 6
        if keys[pygame.K_w]:
            self.y -= 10
        if keys[pygame.K_s]:
            self.y += 6

pygame.init()
screen = pygame.display.set_mode([1200, 800])
clock = pygame.time.Clock()
FPS = 60
player_1 = Player(screen, 1, 8, (255, 0, 0), 100, 100)
# Mapy kanchely stexic a 
map = Map('bigger_map.tmx')
map_img = map.make_map()
map_rect = map_img.get_rect()
map_img = pygame.transform.scale2x(map_img)
# screen = pygame.transform.scale2x(screen)
# Cameran el stexic
camera = Camera(player_1)
follow = Follow(camera, player_1)
border = Border(camera, player_1)
camera.setmethod(border)

while True:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    player_1.move(event)    
    camera.scroll()
    screen.fill((0, 0, 0))
    # u stex nkareluc camera.offset.x u y piti hanes sax obyektneric
    screen.blit(map_img, (0-camera.offset.x, 0-camera.offset.y))
    player_1.draw_player(camera.offset)
    pygame.display.update()

