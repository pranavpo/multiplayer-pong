import socket
import threading
import pickle
import pygame

# Initialize the players list to hold two player objects or None
players = [None, None]

score_player_1 = 0
score_player_2 = 0

# This function handles communication with each connected client


class Ball:
    def __init__(self, x, y, radius, speed_x, speed_y, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.y - self.radius <= 0 or self.y + self.radius >= 768:
            self.speed_y = -self.speed_y

        self.y = max(self.radius, min(self.y, 768 - self.radius))

    def check_collision(self, striker):
        # Check collision with a striker
        if (
            self.x - self.radius < striker.rect.right
            and self.x + self.radius > striker.rect.left
            and self.y > striker.rect.top
            and self.y < striker.rect.bottom
        ):
            self.speed_x = -self.speed_x

    def check_goal(self):
        global score_player_1, score_player_2

        if self.x - self.radius < 0:
            score_player_2 += 1
            self.reset_ball()

        if self.x + self.radius > 1024:
            score_player_1 += 1
            self.reset_ball()

    def reset_ball(self):
        self.x = 1024 // 2
        self.y = 1024 // 2
        self.speed_x = -self.speed_x

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           (int(self.x), int(self.y)), self.radius)


WHITE = (255, 255, 255)
ball = Ball(1024 // 2, 768 // 2, 10, 5, 5, WHITE)


def handle_client(conn, addr, player_number):
    print(f"Player {player_number} connected from {addr}")
    try:
        while True:
            # Receive data from client
            data = conn.recv(4096)
            if not data:
                print(f"Player {player_number} disconnected.")
                break

            # Deserialize the received data (Striker object)
            striker = pickle.loads(data)

            # Update the player's striker in the players list
            players[player_number - 1] = striker
            if players[0] is not None and players[1] is not None:
                ball.move()
                ball.check_collision(players[0])
                ball.check_collision(players[1])
                ball.check_goal()

            # for player in players:
            #     if player:
            #         ball.check_collision(player)

            game_state = {
                "ball": ball,
                "players": players,
                "scores": [score_player_1, score_player_2]
            }
            # Send data for both players to the client
            conn.sendall(pickle.dumps(game_state))

    except Exception as e:
        print(f"Error handling Player {player_number}: {e}")
    finally:
        # Ensure the connection is closed when done
        conn.close()

# Main server function


def server():
    host = input("Enter the server's IPv4 address: ")
    port = int(input("Enter the port number: "))
    player_count = 0  # Counter to track the number of players connected

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(2)  # Maximum of 2 players

        print(f"Server listening on {host}:{port}...")

        # Accept connections for 2 players
        while player_count < 2:
            conn, addr = server_socket.accept()

            # Assign player number (1 or 2)
            player_count += 1
            player_number = player_count

            # Start a thread for each player
            threading.Thread(target=handle_client, args=(
                conn, addr, player_number)).start()

        print("Both players are connected. Server is running...")


# Start the server
if __name__ == "__main__":
    server()
