import pygame
import socket
import server
import pickle

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
WIDTH = 1280
HEIGHT = 720


class Striker():
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.rect = pygame.Rect(posx, posy, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def data_to_send(self):
        return pickle.dumps(self)

    def response_data(self, pickled_data):
        return pickle.loads(pickled_data)

    def update_rect(self):
        self.rect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def update(self, yFac):
        self.posy = self.posy + yFac * self.speed
        if self.posy < 0:
            self.posy = 0
        elif self.posy + self.height >= HEIGHT:
            self.posy = HEIGHT - self.height
            self.striker = (self.posx, self.posy, self.width, self.height)


# Placeholder for the striker
striker = None
running = True


def initialize_striker(player_1_or_2):
    global striker
    if int(player_1_or_2) == 1:
        striker = Striker(20, HEIGHT // 2 - 50, 10, 100, 10, GREEN)
    elif int(player_1_or_2) == 2:
        striker = Striker(WIDTH - 30, HEIGHT // 2 - 50, 10, 100, 10, GREEN)


running = True


def client():
    global striker
    global running
    host = '127.0.0.1'
    port = 65434
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        # Ask if Player 1 or Player 2
        player_1_or_2 = input("Are you player 1 or 2: ")
        if int(player_1_or_2) == 1:
            initialize_striker(1)
            # print(striker)
        elif int(player_1_or_2) == 2:
            initialize_striker(2)
            # print(striker)
        else:
            print("Invalid player number. Exiting...")
            return
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        strikeryFac = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        strikeryFac -= 1
                    if event.key == pygame.K_DOWN:
                        strikeryFac += 1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        strikeryFac = 0
            screen.fill(BLACK)
            # Draw the striker if it exists
            if striker:
                striker.update(strikeryFac)
                striker.draw(screen)
            raw_data = striker.data_to_send()
            client_socket.sendall(raw_data)

            client_socket.settimeout(5)  # Timeout after 5 seconds
            response_data = b''
            try:
                response_data = client_socket.recv(4096)
                if not response_data:
                    response_data = b''
                    # break
            except socket.timeout:
                print("Timed out waiting for response")
                # break
            # Deserialize and draw the other striker
            if response_data:
                try:
                    other_striker = pickle.loads(response_data)
                    # if not other_striker:
                    #     break
                    other_striker.update_rect()
                    other_striker.draw(screen)
                except (pickle.UnpicklingError, AttributeError) as e:
                    print("Failed to process server data.")
            else:
                print("continue")
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()


# def run_game():
#     print("trying to run game")
