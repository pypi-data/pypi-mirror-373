import json, os

PEERS_FILE = "blackchat/data/peers.json"

def save_peer(node_id, peer_id, peer_port):
    if os.path.exists(PEERS_FILE):
        with open(PEERS_FILE, "r") as f:
            peers = json.load(f)
    else:
        peers = {}
    if node_id not in peers:
        peers[node_id] = {}
    peers[node_id][peer_id] = peer_port
    with open(PEERS_FILE, "w") as f:
        json.dump(peers, f, indent=4)

def load_peers(node_id):
    if not os.path.exists(PEERS_FILE):
        return {}
    with open(PEERS_FILE, "r") as f:
        peers = json.load(f)
    return peers.get(node_id, {})


# Tambahkan kelas Peers supaya bisa di-import dari __init__.py
class Peers:
    def __init__(self, node_id):
        self.node_id = node_id

    def save(self, peer_id, peer_port):
        save_peer(self.node_id, peer_id, peer_port)

    def load(self):
        return load_peers(self.node_id)

