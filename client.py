import socket
import threading
from multiprocessing import Lock
from map import *
from sprites import *

lk = Lock()
IN_GAME = False


class Game:
    players = CustomGroup()

    def __init__(self, w, h, fps, main_player) -> None:

        self.WIDTH, self.HEIGHT = w, h
        self.FPS = fps
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        print(self.screen)
        self.main_player = main_player
        self.players.add(main_player)
        pygame.display.set_caption(main_player.name)
        self.map = Map('map/map1/test.tmx')
        self.map_img = pygame.transform.scale2x(self.map.make_map())
        self.map_rect = self.map_img.get_rect()
        self.walls = pygame.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'wall':
                self.walls.add(
                    Obstacle(tile_object.x * 2, tile_object.y * 2, tile_object.width * 2, tile_object.height * 2))
        coords = [[wall.rect.x, wall.rect.y] for wall in self.walls]
        self.camera = Camera(self.main_player, self.WIDTH, self.HEIGHT, coords)
        self.players.add(self.main_player)
        self.follow = Follow(self.camera, self.main_player)
        self.camera.setmethod(self.follow)

    def create_player(self, player: Player):
        self.players.add(player)

    def run(self):

        while not IN_GAME:
            pass

        pygame.init()
        self.clock = pygame.time.Clock()
        self.space_pressed = False

        while True:
            dt = self.clock.tick(self.FPS) * 0.001 * self.FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.space_pressed = True
                    if event.key == pygame.K_r:
                        self.main_player.rect.x = 0
                        self.main_player.rect.y = 0
                        self.main_player.position.x = 0
                        self.main_player.position.y = 0
                        with lk:
                            if IN_GAME:
                                client_socket.send(
                                    f'newpos:{self.main_player.rect.x}:{self.main_player.rect.y};'.encode())
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.space_pressed = False

            prev_pos = [self.main_player.rect.x, self.main_player.rect.y]
            self.main_player.move(self.space_pressed, self.walls, dt)
            with lk:
                if IN_GAME and not (prev_pos[0] == self.main_player.rect.x and prev_pos[1] == self.main_player.rect.y):
                    print('SENDING POSITIONS', 'prev pos', prev_pos[1], prev_pos[0])
                    print('newpois', self.main_player.rect.x, self.main_player.rect.y)
                    client_socket.send(f'newpos:{self.main_player.rect.x}:{self.main_player.rect.y};'.encode())

            self.camera.scroll()
            self.draw()

    def draw(self):

        self.screen.fill((0, 0, 0))
        # self.walls.draw(self.screen)
        self.screen.blit(self.map_img, (0 - self.camera.offset.x, 0 - self.camera.offset.y))
        self.players.draw(self.screen, self.camera.offset)

        pygame.display.update()


def register():
    while True:
        cl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl_socket.connect(('127.0.0.1', 2077))

        nick = input()
        cl_socket.send(nick.encode())
        answer = cl_socket.recv(1024)
        if answer != b'0':
            print('Try another name')
            cl_socket.close()
        else:
            return nick, cl_socket


def switch():
    global IN_GAME
    with lk:
        IN_GAME = not IN_GAME


def client(main_player, sock):
    def servermessage():
        while True:
            msg = sock.recv(1024).decode()
            commands = msg[:-1].split(';')

            for command in commands:
                if not command or command == 'leaveroom':
                    return
                if 'newpl' in command:
                    newplayernick = command.split(':')[1]
                    Game.players.add(Player(newplayernick))
                elif 'newpos' in command:
                    assert len(command.split(':')) == 4, (command, False)
                    _, newplayernick, x, y = command.split(':')

                    for teammate in Game.players:
                        if teammate.name == newplayernick:
                            teammate.rect.x, teammate.rect.y = int(x), int(y)

    threadOn = False
    while True:
        request = input()

        if request == 'createroom':
            threadOn = True
            sock.send(b'createroom')
            roompass = sock.recv(1024)
            print(roompass)
        elif 'connect' in request:
            sock.send(request.encode())
            answer = sock.recv(1024)
            if answer != b'1':
                threadOn = True
                players = answer.decode().split(';')
                Game.players = CustomGroup()
                Game.players.add(main_player)
                for player in players:
                    Game.players.add(Player(player))

        if threadOn:
            switch()
            th3 = threading.Thread(target=servermessage)
            th3.start()
            th3.join()
            switch()


if __name__ == '__main__':
    mp_name, client_socket = register()
    mp = MainPlayer(mp_name)

    clientThread = threading.Thread(target=client, args=(mp, client_socket))
    clientThread.start()

    game = Game(1200, 320, 60, mp)
    game.run()
