import pygame 
from map import *
from sprites import *

class Game:
    def __init__(self, w, h, fps, name) -> None:    
        pygame.init()
        self.WIDTH, self.HEIGHT = w, h
        self.FPS = fps
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        self.clock = pygame.time.Clock()
        self.name = name
        self.load()

    def load(self):
        self.map = Map('test.tmx')
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.map_img = pygame.transform.scale2x(self.map_img)
        self.walls = pygame.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'wall':
                self.walls.add(Obstacle(tile_object.x*2, tile_object.y*2, tile_object.width*2, tile_object.height*2))
        self.setup()


    def setup(self):
        coords = [[wall.rect.x, wall.rect.y] for wall in self.walls]
        self.player = Player(self.name)  
        self.camera = Camera(self.player, self.WIDTH, self.HEIGHT, coords)
        self.players =  pygame.sprite.Group()
        self.players.add(self.player)
        self.follow = Follow(self.camera, self.player)
        self.border = Border(self.camera, self.player)
        self.camera.setmethod(self.follow)

        

    def run(self):
        self.running = True
        self.space_pressed =False
        while self.running:
            dt = self.clock.tick(self.FPS) * 0.001 * self.FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.space_pressed = True
                    if event.key == pygame.K_r:
                        print(self.player.rect.x, self.player.rect.y)
                        self.player.position.x = 100-self.camera.offset.y
                        self.player.position.y = 0-self.camera.offset.y
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:         
                        self.space_pressed = False

            prev_pos =  [self.player.rect.x, self.player.rect.y]
            self.player.move(self.space_pressed, self.walls, dt)    
            if not (prev_pos[0] == self.player.rect.x and prev_pos[1] == self.player.rect.y):
                pass
            
               

            self.draw()
            self.walls = self.camera.scroll(self.walls)

    def draw(self):
        self.screen.fill((0, 0, 0))
        # self.walls.draw(self.screen)
        self.screen.blit(self.map_img, (0-self.camera.offset.x, 0-self.camera.offset.y))
        self.players.draw(self.screen)  
        pygame.display.update()

if __name__ == '__main__':
   
    game = Game(640, 320, 60, '1')
    game.run()
