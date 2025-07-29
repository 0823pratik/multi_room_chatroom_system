# ===============================
# server.py (With Admin Panel, Colors, Persistent Usernames)
# ===============================

import socket
import threading
from datetime import datetime
import os
from colorama import init, Fore, Style
import hashlib
import json

init(autoreset=True)

HOST = '127.0.0.1'
PORT = 9090

# Create logs folder
if not os.path.exists("server_logs"):
    os.makedirs("server_logs")

log_filename = f"server_logs/server_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file = open(log_filename, "w", encoding="utf-8")

# Persistent username storage
USER_STORE_FILE = "user_data.json"
if os.path.exists(USER_STORE_FILE):
    with open(USER_STORE_FILE, "r") as f:
        persistent_users = json.load(f)
else:
    persistent_users = {}

clients = {}       # socket -> username
rooms = {}         # room_name -> set of sockets
client_rooms = {}  # socket -> room_name
user_colors = {}   # username -> color code

COLORS = [Fore.CYAN, Fore.GREEN, Fore.MAGENTA, Fore.YELLOW, Fore.BLUE, Fore.RED]
color_index = 0

def assign_color(username):
    global color_index
    if username not in user_colors:
        user_colors[username] = COLORS[color_index % len(COLORS)]
        color_index += 1
    return user_colors[username]

def timestamp():
    return datetime.now().strftime("%H:%M")

def log(msg):
    log_file.write(msg + "\n")
    log_file.flush()

def broadcast(message, room_name, sender_socket=None):
    if room_name not in rooms:
        return
    for client in rooms[room_name]:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
    log(f"[{timestamp()}] {message}")

def save_persistent_users():
    with open(USER_STORE_FILE, "w") as f:
        json.dump(persistent_users, f)

def handle_client(client):
    try:
        client.send("Enter your username: ".encode('utf-8'))
        username = client.recv(1024).decode('utf-8').strip()

        # Load or assign user ID
        if username in persistent_users:
            pass
        else:
            persistent_users[username] = str(len(persistent_users)+1)
            save_persistent_users()

        clients[client] = username
        color = assign_color(username)
        client.send(f"Welcome {username}! Use /create or /join <room_name> to start chatting.\n".encode('utf-8'))
        client.send("Type /help to see available commands.\n".encode('utf-8'))

        print(color + f"[CONNECTED] {username}")
        log(f"[{timestamp()}] {username} connected.")

        while True:
            msg = client.recv(1024).decode('utf-8')

            if msg.startswith('/'):
                parts = msg.strip().split()
                command = parts[0]

                if command == '/create':
                    if len(parts) < 2:
                        client.send("Usage: /create <room_name>\n".encode('utf-8'))
                        continue
                    room_name = parts[1]
                    rooms.setdefault(room_name, set()).add(client)
                    client_rooms[client] = room_name
                    client.send(f"Created and joined room: {room_name}\n".encode('utf-8'))
                    broadcast(f"{username} joined the room.", room_name, client)

                elif command == '/join':
                    if len(parts) < 2:
                        client.send("Usage: /join <room_name>\n".encode('utf-8'))
                        continue
                    room_name = parts[1]
                    if room_name in rooms:
                        rooms[room_name].add(client)
                        client_rooms[client] = room_name
                        client.send(f"Joined room: {room_name}\n".encode('utf-8'))
                        broadcast(f"{username} joined the room.", room_name, client)
                    else:
                        client.send(f"Room '{room_name}' does not exist. Use /create to create it.\n".encode('utf-8'))

                elif command == '/leave':
                    room_name = client_rooms.get(client)
                    if room_name:
                        rooms[room_name].discard(client)
                        client.send(f"Left room: {room_name}\n".encode('utf-8'))
                        broadcast(f"{username} left the room.", room_name, client)
                        del client_rooms[client]
                    else:
                        client.send("You're not in any room.\n".encode('utf-8'))

                elif command == '/list':
                    room_list = ', '.join(rooms.keys()) or "No active rooms."
                    client.send(f"Available rooms: {room_list}\n".encode('utf-8'))

                elif command == '/admin':
                    user_list = ', '.join(clients.values())
                    room_status = '\n'.join([f"{room}: {len(sockets)} user(s)" for room, sockets in rooms.items()])
                    admin_msg = f"\n[ADMIN PANEL]\nUsers: {user_list}\nRooms:\n{room_status}\n"
                    client.send(admin_msg.encode('utf-8'))

                elif command == '/help':
                    help_msg = """
Available Commands:
/create <room_name>  - Create and join a room
/join <room_name>    - Join an existing room
/leave               - Leave the current room
/list                - List all active rooms
/admin               - View active users & rooms
/quit                - Disconnect from chat
/help                - Show this help message
"""
                    client.send(help_msg.encode('utf-8'))

                elif command == '/quit':
                    client.send("Goodbye!\n".encode('utf-8'))
                    break

                else:
                    client.send("Unknown command. Type /help for available options.\n".encode('utf-8'))
            else:
                room_name = client_rooms.get(client)
                if room_name:
                    color = assign_color(username)
                    full_msg = f"{color}[{room_name}] {username}: {msg}"
                    print(Fore.WHITE + f"[{timestamp()}] {room_name} | {username}: {msg}")
                    broadcast(f"[{room_name}] {username}: {msg}", room_name, client)
                else:
                    client.send("Join a room first using /join <room_name>.\n".encode('utf-8'))

    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}")
    finally:
        disconnect_client(client)

def disconnect_client(client):
    username = clients.get(client)
    if not username:
        return
    room_name = client_rooms.get(client)
    print(Fore.RED + f"[DISCONNECTED] {username}")
    log(f"[{timestamp()}] {username} disconnected.")
    if room_name:
        rooms[room_name].discard(client)
        broadcast(f"{username} left the room.", room_name)
    clients.pop(client, None)
    client_rooms.pop(client, None)
    try:
        client.close()
    except:
        pass

def receive_loop():
    while True:
        try:
            client_socket, address = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket,))
            thread.start()
        except KeyboardInterrupt:
            print(Fore.RED + "\n[SERVER STOPPED]")
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(Fore.GREEN + f"[SERVER STARTED] Listening on {HOST}:{PORT}")
receive_loop()
log_file.close()
