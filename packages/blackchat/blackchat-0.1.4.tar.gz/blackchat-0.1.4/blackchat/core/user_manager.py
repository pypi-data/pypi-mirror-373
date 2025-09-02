# blackchat/core/user_manager.py
import os
import json
import base64
from hashlib import sha256
from cryptography.fernet import Fernet

DATA_DIR = "blackchat/data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
KEYS_DIR = os.path.join(DATA_DIR, "keys")
os.makedirs(KEYS_DIR, exist_ok=True)

class UserManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({}, f)
        with open(USERS_FILE, "r") as f:
            self.users = json.load(f)

    def save_users(self):
        with open(USERS_FILE, "w") as f:
            json.dump(self.users, f, indent=4)

    def _generate_key(self, pin: str):
        """
        Buat Fernet key deterministik dari PIN.
        """
        key = sha256(pin.encode()).digest()  # hash PIN jadi 32 byte
        fernet_key = base64.urlsafe_b64encode(key)
        return Fernet(fernet_key)

    def register(self, username: str, pin: str):
        """
        Register user baru, generate user_id & port, simpan encrypted auth key
        """
        # Cek username udah ada
        for u in self.users.values():
            if u["username"] == username:
                raise Exception("Username sudah digunakan")

        user_id = os.urandom(4).hex()  # 8 hex digit
        port = 5000 + len(self.users)

        fernet = self._generate_key(pin)
        private_key_file = os.path.join(KEYS_DIR, f"{user_id}_auth.key")
        with open(private_key_file, "wb") as f:
            f.write(fernet.encrypt(user_id.encode()))

        self.users[user_id] = {
            "username": username,
            "port": port,
            "contacts": []
        }
        self.save_users()
        return user_id, port

    def login(self, username: str, pin: str):
        """
        Login user berdasarkan username + PIN
        """
        for uid, data in self.users.items():
            if data["username"] == username:
                private_key_file = os.path.join(KEYS_DIR, f"{uid}_auth.key")
                if not os.path.exists(private_key_file):
                    raise Exception("Private key tidak ditemukan untuk user ini.")
                fernet = self._generate_key(pin)
                with open(private_key_file, "rb") as f:
                    try:
                        _ = fernet.decrypt(f.read())
                    except:
                        raise Exception("PIN salah")
                return uid, data["port"]
        raise Exception("User tidak ditemukan")

    def add_contact(self, user_id, contact_id):
        if contact_id not in self.users:
            raise Exception("User ID tidak ada")
        if contact_id not in self.users[user_id]["contacts"]:
            self.users[user_id]["contacts"].append(contact_id)
            self.save_users()

    def get_contacts(self, user_id):
        contacts = {}
        for cid in self.users[user_id]["contacts"]:
            contacts[cid] = self.users[cid]["username"]
        return contacts

