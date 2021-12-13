import pygame
import pytmx
from abc import ABC, abstractmethod

pygame.init()
vec = pygame.math.Vector2


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
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:
    def __init__(self, player, width, height, orig_objects) -> None:
        self.player = player
        self.offset = vec(0, 0)
        self.offset_float = vec(0, 0)
        self.DISPLAY_W, self.DISPLAY_HEIGHT = width, height
        self.CONST = vec(-self.DISPLAY_W / 2 + player.rect.width / 2, -self.player.rect.y + player.rect.height / 2 + 20)

        self.orig_objects = orig_objects

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
        self.camera.offset.x += (self.player.rect.x + self.player.rect.width / 2 -
                                 self.camera.offset.x - self.camera.DISPLAY_W / 2) / 20
        self.camera.offset.x = min(self.camera.DISPLAY_W / 2, max(0, self.camera.offset.x))


if __name__ == '__main__':
    pass
