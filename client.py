import pygame
import socket
import pickle

# Pygame inicijalizacija
pygame.init()

# Konstantne vrednosti
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 30

# Funkcija za renderovanje karata
def render_hand(screen, hand, x, y):
    font = pygame.font.SysFont('Arial', 36)
    for i, card in enumerate(hand):
        card_text = font.render(card, True, BLACK)
        screen.blit(card_text, (x + i * 100, y))

# Povezivanje na server
server_ip = '10.14.89.195'  # IP servera
server_port = 5555
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Glavna logika klijenta
def game_loop():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Blackjack")

    running = True
    player_hand = []
    dealer_hand = []
    money = 0
    bet = 0
    
    while running:
        screen.fill(WHITE)
        data = client_socket.recv(4096)
        
        if data:
            player_data = pickle.loads(data)
            player_hand = player_data[list(player_data.keys())[0]]["hand"]
            dealer_hand = player_data[list(player_data.keys())[0]]["hand"]
            money = player_data[list(player_data.keys())[0]]["money"]

            render_hand(screen, player_hand, 100, 300)
            render_hand(screen, dealer_hand, 100, 100)
        
        pygame.display.update()

        # Check for quit or player input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:  # Hit
                    client_socket.send(b"hit")
                elif event.key == pygame.K_s:  # Stand
                    client_socket.send(b"stand")

    pygame.quit()

if __name__ == "__main__":
    game_loop()

