# 🗨️ Multi-Room Chatroom System

A Python-based terminal and GUI chatroom system supporting **multiple rooms**, **username persistence**, **color-coded usernames**, and a built-in **admin panel**. Designed for local network use with support for both CLI and GUI clients.

---

## 📂 Project Structure

```
multiroom_chatroom_system/
├── server.py             # Main chat server
├── client.py             # Terminal-based client
├── client_gui.py         # GUI-based client using Tkinter
├── user_data.json        # Persistent username storage
├── server_logs/          # Server logs folder (auto-created)
├── logs/                 # Client logs folder (auto-created)
└── README.md             # This file
```

---

##  Features

###  Server Features (`server.py`)
- Multi-room support (`/create`, `/join`, `/leave`)
- Persistent usernames (`user_data.json`)
- Color-coded usernames using `colorama`
- Real-time room and user listing with `/admin`
- Command-based interface (`/help`, `/list`, `/quit`, etc.)
- Auto logging to `server_logs/`
<img width="1011" height="214" alt="image" src="https://github.com/user-attachments/assets/d695e8a3-4b7f-4884-936b-d1275e7866ab" />

###  Terminal Client (`client.py`)
- Auto reconnection to server
- Persistent logging to `logs/`
- Color-coded chat display
- Local echo of sent messages
- Command interface
<img width="1000" height="741" alt="image" src="https://github.com/user-attachments/assets/b1ad1228-c170-4582-82c3-c4dd1ea3038b" />
<img width="912" height="432" alt="image" src="https://github.com/user-attachments/assets/1a602bd5-dd33-4da2-adfc-40eee5ec2f89" />

###  GUI Client (`client_gui.py`)
- Tkinter-based GUI
- Scrollable chat history
- Color-coded usernames
- Message formatting and tag-based styling
- Modal prompt for username

---

## 🛠️ Installation & Setup

### Requirements
- Python 3.7+
- `colorama` module (for color support)

Install dependencies:
```bash
pip install colorama
```

### Running the Server
```bash
python server.py
```

### Running the Terminal Client
```bash
python client.py
```

###  Running the GUI Client
```bash
python client_gui.py
```

---

## 💬 Chat Commands

| Command            | Description                                |
|--------------------|--------------------------------------------|
| `/create <room>`   | Create and join a new room                 |
| `/join <room>`     | Join an existing room                      |
| `/leave`           | Leave the current room                     |
| `/list`            | Show all available rooms                   |
| `/admin`           | Show active users and room status          |
| `/quit`            | Disconnect from the server                 |
| `/help`            | Display all available commands             |

---

##  Username Persistence

Usernames are stored persistently in `user_data.json`. On first login, each user is assigned an ID and color. Color consistency is maintained during the session.

---

##  Logging

- Server logs: `server_logs/server_log_<timestamp>.log`
- Client logs: `logs/chat_<timestamp>.log`

These logs track all messages and activity for monitoring and debugging.

---

##  Notes

- This system runs on `127.0.0.1:9090` by default (localhost). To run over a LAN, update `HOST` in `server.py` and clients accordingly.
- GUI and terminal clients can both connect simultaneously.
- Designed for educational or small team use; not production-ready for public internet.

---

## License

This project is open-source and provided under the [MIT License](LICENSE).

---

## Acknowledgements

- `colorama` for cross-platform color support
- `tkinter` for GUI framework
- Python’s `socket`, `threading`, and `json` modules

