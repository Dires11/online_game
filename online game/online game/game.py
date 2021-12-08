import socket
import threading
from time import sleep
from main import *
import pygame 
from map import *
from sprites import *

IN_GAME = False

class Game:
    def __init__(self, w, h, fps, name) -> None:    
        self.WIDTH, self.HEIGHT = w, h
        self.FPS = fps
        self.clock = pygame.time.Clock()
        self.players =  pygame.sprite.Group()
        self.player = MainPlayer(name, 100, 0, 25, 25, (0, 0, 255)) 
        self.players.add(self.player)
        self.prev_offset = pygame.Vector2(0, 0)


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
        self.camera = Camera(self.player, self.WIDTH, self.HEIGHT, coords)
        self.follow = Follow(self.camera, self.player)
        self.border = Border(self.camera, self.player)
        self.camera.setmethod(self.follow)

        

    def run(self):
        self.running = True
        self.space_pressed =False
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        self.load()

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
                        self.player.position.x = 100-self.camera.offset.y
                        self.player.position.y = 0-self.camera.offset.y
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:         
                        self.space_pressed = False

            prev_pos =  [self.player.rect.x, self.player.rect.y]
            self.player.move(self.space_pressed, self.walls, dt)    
            if not (prev_pos[0] == self.player.rect.x and prev_pos[1] == self.player.rect.y) and IN_GAME:
                sleep(0.1)
                for player in self.players:
                    if player != self.player and self.prev_offset.x != self.camera.offset.x:
                        print('heeeee ha')
                        player.rect.x -= self.camera.offset.x
                        self.prev_offset.x = self.camera.offset.x
                client_socket.send(f'newpos:{self.player.rect.x}:{self.player.rect.y}'.encode())

            self.draw()
            self.walls = self.camera.scroll(self.walls)

    def draw(self):
        self.screen.fill((0, 0, 0))
        # self.walls.draw(self.screen)
        self.screen.blit(self.map_img, (0-self.camera.offset.x, 0-self.camera.offset.y))
        self.players.draw(self.screen)  
        pygame.display.update()



class MainPlayer(Player):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.teammates = []


def register():
    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 1986))

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
            msg = client_socket.recv(1024)
            print('MSG IN WHILE ', msg)
            if not msg or msg == b'leaveroom':
                break
            if 'newpl' in msg.decode():
                newplayernick = msg.decode().split(':')[1]
                mp.player.teammates.append(Player(newplayernick))
                mp.players.add(Player(newplayernick))
                print(mp.players)
                print('NEW PLAYER')
            elif 'newpos' in msg.decode():
                print(msg.decode().split(':'))
                assert len(msg.decode().split(':')) == 4, (msg, False)
                _, newplayernick, x, y = msg.decode().split(':')
                x, y = int(x), int(y)
                print('new pos for ', newplayernick, ':', x, y)
                
                for teammate in mp.player.teammates:
                    if teammate.name == newplayernick:
                        teammate.x, teammate.y = x, y
                for teammate in mp.players:
                    if teammate.name == newplayernick:
                        print('assinging', x, y)
                        teammate.rect.x = x
                        teammate.rect.y = y
    threadOn = False
    while True:
        command = input()

        if command == 'createroom':
            print('sended ')
            threadOn = True
            client_socket.send(b'createroom')
            roompass = client_socket.recv(1024)
            print(roompass)
        elif 'connect' in command:
            print("here")
            client_socket.send(command.encode())
            answer = client_socket.recv(1024)
            print(answer)
            if answer != b'1':
                threadOn = True
                players = answer.decode().split(';')
                print(players)
                for player in players:
                    mp.player.teammates.append(Player(player))
                for player in players:  
                    mp.players.add(Player(player))
            
        if threadOn:
            IN_GAME = True
            th3 = threading.Thread(target=servermessage)
            th3.start()
            th3.join()
            IN_GAME = False

if __name__ == '__main__':
    mp, client_socket = register()
    mp = Game(640, 320, 60, mp)

    clientThread = threading.Thread(target=client, args=(mp, client_socket))
    clientThread.start()
    while not IN_GAME: pass
    pygame.init()
    mp.run()







