import os
import json
import uuid

GROUPS_DIR = "blackchat/data/groups"
os.makedirs(GROUPS_DIR, exist_ok=True)

class Grup:
    def __init__(self, name, creator_id):
        self.group_id = uuid.uuid4().hex[:8]
        self.name = name
        self.creator_id = creator_id
        self.members = {}  # {user_id: port}

    def add_member(self, user_id, port):
        self.members[user_id] = port

    def save(self):
        group_file = os.path.join(GROUPS_DIR, f"group_{self.group_id}.json")
        with open(group_file, "w") as f:
            json.dump({
                "group_id": self.group_id,
                "name": self.name,
                "creator_id": self.creator_id,
                "members": self.members
            }, f, indent=4)

