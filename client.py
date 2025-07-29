# ===============================
# client.py (Final Version with Unique Username Colors)
# ===============================

import socket
import threading
import sys
import time
from datetime import datetime
import os
import random
from collections import defaultdict
from colorama import init, Fore, Style

init(autoreset=True)

HOST = '127.0.0.1'
PORT = 9090
RETRY_DELAY = 3
running = True
username = ""
current_room = ""

# Color pool for usernames
color_pool = [
    Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.GREEN, Fore.BLUE,
    Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTBLUE_EX,
    Fore.LIGHTCYAN_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTYELLOW_EX
]
user_colors = defaultdict(lambda: random.choice(color_pool))

# Create logs folder
if not os.path.exists("logs"):
    os.makedirs("logs")

log_filename = f"logs/chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file = open(log_filename, "w", encoding="utf-8")

def log_message(msg):
    log_file.write(f"{msg}\n")
    log_file.flush()

def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
            print(Fore.GREEN + "[CONNECTED] Connected to server")
            return client
        except:
            print(Fore.YELLOW + f"[RETRYING] Server not available. Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)

client = connect_to_server()

def enter_username():
    global username
    while True:
        prompt = client.recv(1024).decode('utf-8')
        if "Enter your username" in prompt:
            sys.stdout.write(Fore.CYAN + prompt)
            sys.stdout.flush()
            username = input()
            client.send(username.encode('utf-8'))
        else:
            print(Fore.GREEN + prompt, end='')
            break

def timestamp():
    return datetime.now().strftime("%H:%M")

def receive():
    global running
    while running:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg:
                stamped = f"[{timestamp()}] {msg}"
                log_message(stamped)

                # Extract username from message if format matches [Room] User: msg
                try:
                    if msg.startswith("[") and "]" in msg:
                        room_split = msg.split("] ", 1)
                        if len(room_split) > 1 and ": " in room_split[1]:
                            user_part = room_split[1].split(":")[0]
                            color = user_colors[user_part]
                            sys.stdout.write(f"\r{color}{stamped}\n>")
                        else:
                            sys.stdout.write(Fore.YELLOW + f"\r{stamped}\n>")
                    elif "joined" in msg or "left" in msg:
                        sys.stdout.write(Fore.MAGENTA + f"\r{stamped}\n>")
                    else:
                        sys.stdout.write(f"\r{stamped}\n>")
                except:
                    sys.stdout.write(f"\r{stamped}\n>")

                sys.stdout.flush()
            else:
                break
        except:
            if running:
                print(Fore.RED + "\n[ERROR] Lost connection to server.")
            break

def reconnect():
    global client
    client = connect_to_server()
    enter_username()
    recv_thread = threading.Thread(target=receive)
    recv_thread.start()

def write():
    global running, current_room
    while True:
        try:
            msg = input("> ").strip()
            if not msg:
                continue

            # Detect /join or /create and update current_room
            if msg.startswith("/join") or msg.startswith("/create"):
                try:
                    current_room = msg.split()[1]
                except IndexError:
                    pass

            # Local echo if normal message
            if not msg.startswith('/'):
                if current_room:
                    preview = f"[{timestamp()}] [{current_room}] {username}: {msg}"
                    print(Fore.YELLOW + preview)
                    log_message(preview)
                else:
                    print(Fore.LIGHTBLACK_EX + "[Not in room] Message won't be seen by others.")

            client.send(msg.encode('utf-8'))

            if msg.strip() == '/quit':
                running = False
                break
        except:
            print(Fore.RED + "[ERROR] Sending message failed.")
            break

enter_username()
recv_thread = threading.Thread(target=receive)
recv_thread.start()

write()

try:
    client.shutdown(socket.SHUT_RDWR)
except:
    pass
client.close()
recv_thread.join()
log_file.close()
print(Fore.CYAN + "[EXITED] Chat closed cleanly.")