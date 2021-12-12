import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, name, x=0, y=200, width=25, height=25, color=(0, 0, 255)):
        self.name = name
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x    
        self.rect.y = y
        self.gravity, self.friction = .35, -.12
        self.position, self.velocity = pygame.math.Vector2(x, y), pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        self.MAX_FALLING_SPEED = 7
        self.MAX_SPEED = 4
        self.JUMP_SPEED = 7
        self.on_ground = False

    def handle_collisions(self, walls):
        hits = pygame.sprite.spritecollide(self, walls, False)
        self.position.x, self.position.y = self.rect.x, self.rect.y
        for hit in hits:
            if hit.rect.collidepoint(self.rect.centerx, self.rect.y + self.rect.height):
                self.on_ground = True
                self.velocity.y = 0
                self.rect.y = hit.y - self.rect.height
                self.position.y = self.rect.y 

            if hit.rect.collidepoint(self.rect.centerx, self.rect.y):
                self.rect.y = hit.y + hit.height
                self.position.y = self.rect.y
                self.velocity.y = 0
            
            if hit.rect.collidepoint(self.rect.x, self.rect.centery): 
                self.rect.x = hit.rect.x + hit.rect.width
                self.position.x = self.rect.x
                self.velocity.x = 0
                
            if hit.rect.collidepoint(self.rect.x + self.rect.width, self.rect.centery): 
                self.rect.x = hit.rect.x - self.rect.width
                self.position.x = self.rect.x
                self.velocity.x = 0
                
    def horizontal_movement(self, keys, dt):
        self.acceleration.x = 0
        if keys[pygame.K_d]:
            self.acceleration.x += 1
        if keys[pygame.K_a]:
            self.acceleration.x -= 1

        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.velocity.x = max(-self.MAX_SPEED, min(self.velocity.x, self.MAX_SPEED))
        self.velocity.x = 0 if 0 < abs(self.velocity.x) < 0.1 else self.velocity.x   
        self.position.x += self.velocity.x * dt + (self.acceleration.x * .5) * (dt ** 2)
        self.rect.x = self.position.x

    # def horizontal_movement(self, keys, dt):
    #     if keys[pygame.K_d]:
    #         self.rect.x += 4
    #     if keys[pygame.K_a]:
    #         self.rect.x -= 4

    def vertical_movement(self, space_pressed, dt):
        if space_pressed and self.on_ground:
            self.velocity.y -= self.JUMP_SPEED
            self.on_ground = False

        self.velocity.y = min(self.MAX_FALLING_SPEED, (self.velocity.y + self.acceleration.y * dt))
        self.velocity.y = 0 if 0 < self.velocity.y < 0.1 else self.velocity.y   
        self.position.y += self.velocity.y * dt + (self.acceleration.y * .5) * (dt * dt)
        self.acceleration.y = self.gravity    
        self.rect.y = self.position.y
        
    def move(self, space_pressed, walls, dt):
        keys=pygame.key.get_pressed()
        self.horizontal_movement(keys, dt)
        self.vertical_movement(space_pressed, dt)
        #Checks if obstacle is on player's way if yes player doesn't move
        self.handle_collisions(walls)
        

class MainPlayer(Player):
    pass



class CustomGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()

    def draw(self, surface, main_spr, cam_off):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, (spr.rect.x-cam_off.x, spr.rect.y-cam_off.y))
        
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface([w, h])
        self.image.fill((255, 0, 0))


