import pygame
from pygame.surfarray import pixels_alpha 
import pytmx 
from abc import ABC, abstractmethod

pygame.init()


class Map:
    def __init__(self, filename) -> None:
        self.tmxdata = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.tmxdata.width * self.tmxdata.tilewidth
        self.height = self.tmxdata.height * self.tmxdata.tileheight

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile: 
                        surface.blit(tile, (x*self.tmxdata.tilewidth, y*self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


vec = pygame.math.Vector2

class Camera:
    def __init__(self, player) -> None:
        self.player = player
        self.offset = vec(0, 0)
        self.offset_float = vec(0, 0)
        self.DISPLAY_W, self.DISPLAY_HEIGHT = 1200, 800
        self.CONST = vec(-self.DISPLAY_W/2 + player.radius, -self.player.y+player.radius + 20)

    def setmethod(self, method):
        self.method = method
    
    def scroll(self):
        self.method.scroll()


class CamScroll(ABC):
    def __init__(self, camera, player):
        self.camera = camera
        self.player = player

    
    @abstractmethod
    def scroll(self):
        pass


class Follow(CamScroll):
    def __init__(self, camera, player):
        super().__init__(camera, player)
    

    def scroll(self):
       self.camera.offset_float.x += (self.player.x-self.player.radius - self.camera.offset_float.x + self.camera.CONST.x)
    #    self.camera.offset_float.y += (self.player.y+self.player.radius - self.camera.offset_float.y)
       self.camera.offset_float.y += 0
       self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)

class Border(CamScroll):
    def __init__(self, camera, player):
        super().__init__(camera, player)
    

    def scroll(self):
        self.camera.offset_float.x += (self.player.x-self.player.radius - self.camera.offset_float.x + self.camera.CONST.x)
        # self.camera.offset_float.y += (self.player.y+self.player.radius - self.camera.offset_float.y + self.camera.CONST.y)
        self.camera.offset_float.y += 0
        self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)
        self.camera.offset.x = max(0, self.camera.offset.x)
        self.camera.offset.x = min(self.camera.DISPLAY_W, self.camera.offset.x)

class Auto(CamScroll):
    def __init__(self, camera, player):
        super().__init__(camera, player)
    

    def scroll(self):
      self.camera.offset.x += 1