from xml.etree.ElementTree import XML
import pygame
from pygame.surfarray import pixels_alpha 
import pytmx 
from abc import ABC, abstractmethod
from copy import deepcopy

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
    def __init__(self, player, width, height, orig_objects) -> None:
        self.player = player
        self.offset = vec(0, 0)
        self.offset_float = vec(0, 0)
        self.DISPLAY_W, self.DISPLAY_HEIGHT = width, height
        self.CONST = vec(-self.DISPLAY_W/2 + player.rect.width / 2, -self.player.rect.y+player.rect.height/2 + 20)
      
        self.orig_objects = orig_objects
    def setmethod(self, method):
        self.method = method
    
    def scroll(self, objects):
        self.method.scroll()
        # return self.move_objects(objects)

    def move_objects(self, objects):
        for i, object in enumerate(objects):  
            object.rect.x = self.orig_objects[i][0] - self.offset.x
            object.rect.y = self.orig_objects[i][1] - self.offset.y
        
        return objects

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
        self.camera.offset.x +=(self.player.rect.x+self.player.rect.width/2-self.camera.offset.x-self.camera.DISPLAY_W/2)/20
        self.camera.offset.x = min(self.camera.DISPLAY_W/2, max(0, self.camera.offset.x))
# class Follow(CamScroll):
#     def __init__(self, camera, player):
#         super().__init__(camera, player)
    

#     def scroll(self):
#         self.camera.offset_float.x += (self.player.rect.x - self.camera.offset_float.x + self.camera.CONST.x)
#         # self.camera.offset_float.y += (self.player.rect.y - self.camera.offset_float.y + self.camera.CONST.y)

#         self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)
#     #    self.camera.offset_float.x += (self.player.rect.x+self.player.rect.width - self.camera.offset_float.x + self.camera.CONST.x)
#     #    self.camera.offset_float.y += (self.player.y+self.player.radius - self.camera.offset_float.y)
#     #    self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)

# class Border(CamScroll):
#     def __init__(self, camera, player):
#         super().__init__(camera, player)
    

#     def scroll(self):
#         self.camera.offset_float.x += (self.player.rect.x-self.player.rect.width/2 - self.camera.offset_float.x + self.camera.CONST.x)
#         # self.camera.offset_float.y += (self.player.y+self.player.radius - self.camera.offset_float.y + self.camera.CONST.y)
#         self.camera.offset_float.y += 0
#         self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)
#         self.camera.offset.x = max(0, self.camera.offset.x)
#         self.camera.offset.x = min(self.camera.DISPLAY_W, self.camera.offset.x)

# class Auto(CamScroll):
#     def __init__(self, camera, player):
#         super().__init__(camera, player)
    

#     def scroll(self):
#       self.camera.offset.x += 1