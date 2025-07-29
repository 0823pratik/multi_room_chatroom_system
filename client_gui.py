import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from datetime import datetime
from colorama import Fore, init
import random

init(autoreset=True)

HOST = '127.0.0.1'
PORT = 9090

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

username = ''
current_room = ''
user_colors = {}
color_pool = [Fore.CYAN, Fore.GREEN, Fore.MAGENTA, Fore.LIGHTBLUE_EX, Fore.YELLOW]


def timestamp():
    return datetime.now().strftime("%H:%M")


def assign_color(name):
    if name not in user_colors:
        user_colors[name] = random.choice(color_pool)
    return user_colors[name]


class ChatClient:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Multi-Room Chat")

        self.chat_area = scrolledtext.ScrolledText(self.win, state='disabled', wrap='word', width=60, height=25)
        self.chat_area.pack(padx=10, pady=10)

        self.entry_field = tk.Entry(self.win, width=50)
        self.entry_field.pack(side=tk.LEFT, padx=10, pady=10)
        self.entry_field.bind("<Return>", lambda event: self.send_message())

        self.send_btn = tk.Button(self.win, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT)

        self.win.protocol("WM_DELETE_WINDOW", self.quit_chat)

        self.running = True

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self):
        msg = self.entry_field.get().strip()
        if not msg:
            return

        global current_room

        if msg.startswith('/join') or msg.startswith('/create'):
            try:
                current_room = msg.split()[1]
            except IndexError:
                current_room = ''
        elif not msg.startswith('/') and current_room:
            self.display_message(current_room, username, msg)

        client.send(msg.encode('utf-8'))
        self.entry_field.delete(0, tk.END)

        if msg == '/quit':
            self.running = False
            self.win.quit()

    def receive_messages(self):
        while self.running:
            try:
                msg = client.recv(1024).decode('utf-8')
                if not msg:
                    break

                if "Enter your username" in msg:
                    self.prompt_username()
                    continue

                if msg.startswith("[") and "]" in msg and ": " in msg:
                    try:
                        room = msg.split("]")[0][1:]
                        name_msg = msg.split("] ")[1]
                        name, message = name_msg.split(": ", 1)
                        self.display_message(room, name, message)
                    except Exception:
                        self.show_chat(msg)
                else:
                    self.show_chat(msg)

            except:
                break

    def show_chat(self, msg):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, f"[{timestamp()}] {msg}\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def display_message(self, room, sender, message):
        color = assign_color(sender)
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, f"[{timestamp()}] [{room}] ", 'bold')
        self.chat_area.insert(tk.END, f"{sender}", color)
        self.chat_area.insert(tk.END, f": {message}\n")
        self.chat_area.tag_config(color, foreground=color.replace("Fore.", "").lower())
        self.chat_area.tag_config('bold', font=("Helvetica", 10, "bold"))
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def prompt_username(self):
        global username
        username = simpledialog.askstring("Username", "Enter your username:")
        client.send(username.encode('utf-8'))
        self.show_chat(f"Welcome {username}! Use /create or /join <room_name> to start chatting.")

    def quit_chat(self):
        self.running = False
        try:
            client.send('/quit'.encode('utf-8'))
        except:
            pass
        client.close()
        self.win.quit()


if __name__ == "__main__":
    ChatClient().win.mainloop()
