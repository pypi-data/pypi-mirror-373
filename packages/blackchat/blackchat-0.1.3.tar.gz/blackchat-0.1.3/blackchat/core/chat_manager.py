import os
import json
import time


DATA_DIR = "blackchat/data/users"
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, "w") as f:
        json.dump([], f, indent=4)

class ChatManager:
    def __init__(self, node):
        self.node = node

    def send_direct_message(self, sender_id, receiver_id, receiver_port, message):
        # simpan ke messages.json
        messages_file = "blackchat/data/users/messages.json"
        os.makedirs(os.path.dirname(messages_file), exist_ok=True)
        if not os.path.exists(messages_file):
            with open(messages_file, "w") as f:
                json.dump([], f, indent=4)
        with open(messages_file, "r") as f:
            try:
                all_messages = json.load(f)
            except:
                all_messages = []

        new_message = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message": message,
            "timestamp": time.time(),
            "read": False
        }
        all_messages.append(new_message)
        with open(messages_file, "w") as f:
            json.dump(all_messages, f, indent=4)

        # notif realtime ke node
        self.node.send_direct_notification(receiver_id, message)
