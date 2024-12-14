import pygame
import socket
import pickle
import random
import time

# Pygame inicijalizacija
pygame.init()

# Konstantne vrednosti
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 30
STARTING_MONEY = 1000  # Početni novac svakog igrača

# Karte
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['♠', '♣', '♦', '♥']

# Funkcija za kreiranje špila
def create_deck():
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append(f'{rank}{suit}')
    random.shuffle(deck)
    return deck

# Funkcija za izračunavanje broja poena
def calculate_points(hand):
    points = 0
    ace_count = 0
    for card in hand:
        rank = card[:-1]
        if rank in ['J', 'Q', 'K']:
            points += 10
        elif rank == 'A':
            points += 11
            ace_count += 1
        else:
            points += int(rank)
    
    while points > 21 and ace_count:
        points -= 10
        ace_count -= 1
    return points

# Server setup
server_ip = '10.14.89.195'  # Tvoj IP adresa
server_port = 5555
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(2)  # Samo 2 korisnika mogu da se povežu

# Funkcija za slanje stanja igračima
def send_game_state(players, player_data):
    for player_socket in players:
        # Samo šaljemo podatke o igračima, bez soketa
        player_data_without_sockets = {
            player_socket.getpeername(): player_data[player_socket]
            for player_socket in player_data.keys()
        }
        player_socket.send(pickle.dumps(player_data_without_sockets))

# Glavna logika servera
def game_loop():
    print(f"Server started on {server_ip}:{server_port}")
    clients = []
    player_data = {}

    while len(clients) < 2:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        player_data[client_socket] = {
            "money": STARTING_MONEY,
            "hand": [],
            "bet": 0,
            "stand": False
        }
        print(f"Client {client_address} connected. {len(clients)} player(s) connected.")
    
    # Kreiramo špil
    deck = create_deck()

    # Početak igre
    for player_socket in player_data.keys():
        player_data[player_socket]["hand"] = [deck.pop(), deck.pop()]

    # Pošaljite početnu ruku igračima
    send_game_state(clients, player_data)

    # Igrači postavljaju opkladu
    for player_socket in player_data.keys():
        bet = 0
        while bet <= 0 or bet > player_data[player_socket]["money"]:
            # Pitanje za opkladu
            bet = 100  # U realnoj igri, ovo bi bilo postavljeno kroz interfejs
        player_data[player_socket]["bet"] = bet
        player_data[player_socket]["money"] -= bet

    # Glavna logika igre
    player_turns = [player_socket for player_socket in player_data.keys()]
    winner = None
    while player_turns:
        for player_socket in player_turns[:]:
            if player_data[player_socket]["stand"]:
                player_turns.remove(player_socket)
                continue
            
            # Čekaj akciju od igrača: Hit ili Stand
            action = "hit"  # Ovdje bi bilo čekanje za unos korisnika, za sada simuliramo 'hit'
            
            if action == "hit":
                player_data[player_socket]["hand"].append(deck.pop())
            elif action == "stand":
                player_data[player_socket]["stand"] = True

            # Recalculate points
            player_points = calculate_points(player_data[player_socket]["hand"])
            
            if player_points > 21:  # Igrač je izgubio
                player_data[player_socket]["stand"] = True
                winner = "dealer"
        
        send_game_state(clients, player_data)

    # Dilerov potez (diler mora da stoji na 17 ili više)
    dealer_hand = [deck.pop(), deck.pop()]
    dealer_points = calculate_points(dealer_hand)
    
    while dealer_points < 17:
        dealer_hand.append(deck.pop())
        dealer_points = calculate_points(dealer_hand)
    
    # Izračunaj pobednika
    for player_socket in player_data.keys():
        player_points = calculate_points(player_data[player_socket]["hand"])
        if player_points > 21:
            player_data[player_socket]["money"] -= player_data[player_socket]["bet"]
        elif dealer_points > 21 or player_points > dealer_points:
            player_data[player_socket]["money"] += player_data[player_socket]["bet"]
        else:
            # Izjednaceno
            pass

    send_game_state(clients, player_data)
    
    # Zatvaranje konekcija
    for client in clients:
        client.close()

if __name__ == "__main__":
    game_loop()

