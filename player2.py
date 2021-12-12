import socket
import threading
from time import sleep
from multiprocessing import Lock

import pygame 

from map import *
from sprites import *

lk = Lock()
IN_GAME = False


class Game:
    def __init__(self, w, h, fps, main_player) -> None:    

        self.WIDTH, self.HEIGHT = w, h
        self.FPS = fps
        self.players =  pygame.sprite.Group()
        self.main_player = main_player
        self.players.add(main_player)
        self.map = Map('test.tmx')
        self.map_img = pygame.transform.scale2x(self.map.make_map())
        self.map_rect = self.map_img.get_rect()
        self.walls = pygame.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'wall':
                self.walls.add(Obstacle(tile_object.x*2, tile_object.y*2, tile_object.width*2, tile_object.height*2))
        self.setup()
        coords = [[wall.rect.x, wall.rect.y] for wall in self.walls]
        self.camera = Camera(self.main_player, self.WIDTH, self.HEIGHT, coords)
        self.players.add(self.main_player)
        self.follow = Follow(self.camera, self.main_player)
        self.border = Border(self.camera, self.main_player)
        self.camera.setmethod(self.follow)

        
    def create_player(self, player: Player):
        
        self.players.add(player)

    def run(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        self.clock = pygame.time.Clock()
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
                        print(self.main_player.rect.x, self.main_player.rect.y)
                        self.main_player.position.x = 100-self.camera.offset.y
                        self.main_player.position.y = 0-self.camera.offset.y
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:         
                        self.space_pressed = False

            prev_pos =  [self.main_player.rect.x, self.main_player.rect.y]
            self.main_player.move(self.space_pressed, self.walls, dt)    
            
            if not (prev_pos[0] == self.main_player.rect.x and prev_pos[1] == self.main_player.rect.y):
                client_socket.send(f'newpos:{self.main_player.x}:{self.main_player.y};'.encode())

            self.draw()
            self.walls = self.camera.scroll(self.walls)

    def draw(self):
        
        self.screen.fill((0, 0, 0))
        # self.walls.draw(self.screen)
        self.screen.blit(self.map_img, (0-self.camera.offset.x, 0-self.camera.offset.y))
        self.players.draw(self.screen)  

        pygame.display.update()

def register():
    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 2075))

        nick = input()
        print(nick)
        client_socket.send(nick.encode())
        answer = client_socket.recv(1024)
        if answer != b'0':
            print('close')
            client_socket.close()
        else:
            print('yes')
            return (nick, client_socket)



def client(mp, client_socket):
    global IN_GAME
    def servermessage():
        while True:
            print('WAITING')
            msg = client_socket.recv(1024).decode()
            commands = msg.split(';')

            for command in commands:
                if not command or command == 'leaveroom':
                    return
                if 'newpl' in command:
                    newplayernick = command.split(':')[1]
                    game.players.add(Player(newplayernick))
                    print('NEW PLAYER')
                elif 'newpos' in command:
                    assert len(command.split(':')) == 4, (command, False)
                    _, newplayernick, x, y = command.split(':')
                    print('new pos for ', newplayernick, ':', x, y)
                    
                    for teammate in game.players:
                        if teammate.name == newplayernick:
                            teammate.rect.x, teammate.rect.y = x, y

    threadOn = False
    while True:
        command = input()

        if command == 'createroom':
            threadOn = True
            client_socket.send(b'createroom')
            roompass = client_socket.recv(1024)
            print(roompass)
        elif 'connect' in command:
            client_socket.send(command.encode())
            answer = client_socket.recv(1024)
            if answer == b'0':
                threadOn = True
                players = client_socket.recv(1024).decode().split(';')
                mp.teammates.clear()
                for player in players:
                    mp.teammates.append(Player(player))
            
        if threadOn:
            IN_GAME = True
            th3 = threading.Thread(target=servermessage)
            th3.start()
            th3.join()
            IN_GAME = False

if __name__ == '__main__':
    mp_name, client_socket = register()
    mp = MainPlayer(mp_name)

    clientThread = threading.Thread(target=client, args=(mp, client_socket))
    clientThread.start()

    game = Game(640, 320, 60, mp)
    game.run()

