# utils/peers.py
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

