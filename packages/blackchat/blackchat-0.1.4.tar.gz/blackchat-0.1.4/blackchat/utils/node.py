import threading
import time
import json
import os

class P2PNode:
    def __init__(self, port, user_id):
        self.port = port
        self.user_id = user_id
        self.groups = {}
        self.peers = {}  # {peer_id: port}
        self.running = False
        self.message_listener_thread = None
        self.last_checked = 0  # timestamp terakhir cek pesan
        self.new_message_callbacks = []  # list fungsi notif

    def start(self):
        self.running = True
        self.message_listener_thread = threading.Thread(target=self.listener, daemon=True)
        self.message_listener_thread.start()

    def stop(self):
        self.running = False
        if self.message_listener_thread:
            self.message_listener_thread.join()

    def listener(self):
        while self.running:
            self.check_incoming_messages()
            time.sleep(1)

    def register_new_message_callback(self, callback):
        """
        Callback dipanggil saat pesan baru diterima
        callback(message_dict)
        """
        self.new_message_callbacks.append(callback)

    def notify_new_message(self, message):
        for cb in self.new_message_callbacks:
            cb(message)

    def check_incoming_messages(self):
        messages_file = "blackchat/data/users/messages.json"
        if not os.path.exists(messages_file):
            return
        with open(messages_file, "r") as f:
            try:
                messages = json.load(f)
            except:
                messages = []

        updated = False
        for m in messages:
            if not isinstance(m, dict):
                continue
            receiver_id = m.get("receiver_id")
            if receiver_id == self.user_id and not m.get("read", False):
                sender_id = m.get("sender_id", "unknown")
                message_text = m.get("message", "")
                # langsung notif ke callback
                self.notify_new_message({
                    "sender_id": sender_id,
                    "message": message_text
                })
                m["read"] = True
                updated = True

        if updated:
            with open(messages_file, "w") as f:
                json.dump(messages, f, indent=4)

    def send_direct_notification(self, peer_id, message):
        """
        Kirim notif langsung ke peer jika peer ada di peers dict
        """
        print(f"[NODE {self.port}] Notif ke {peer_id}: {message}")

    def broadcast_message(self, message):
        print(f"[NODE {self.port}] Broadcast: {message}")

    def add_group(self, group):
        self.groups[group.group_id] = group

    def print_network(self):
        print(f"\nNode {self.user_id} (Port {self.port})")
        if not self.peers:
            print("Belum ada peer terhubung.")
            return

        print("┌─────────┐")
        print(f"│ {self.user_id} │")
        print("└─────┬───┘")

        peer_ids = list(self.peers.keys())
        for i, pid in enumerate(peer_ids):
            connector = "└──" if i == len(peer_ids) - 1 else "├──"
            print(f"    {connector} {pid} (Port {self.peers[pid]})")

