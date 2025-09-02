from blackchat.core.user_manager import UserManager
from blackchat.core.chat_manager import ChatManager
from blackchat.core.grup import Grup
from blackchat.utils.node import P2PNode
from blackchat.utils.notifier import notify
from blackchat.utils.peers import save_peer, load_peers

import os
import json
import time

def get_unread_messages(user_id):
    messages_file = "blackchat/data/users/messages.json"
    if not os.path.exists(messages_file):
        return []
    with open(messages_file, "r") as f:
        try:
            all_messages = json.load(f)
        except:
            all_messages = []
    unread = []
    for m in all_messages:
        if not isinstance(m, dict):
            continue
        if m.get("receiver_id") == user_id and not m.get("read", False):
            unread.append(m)
    return unread

def mark_messages_as_read(user_id):
    messages_file = "blackchat/data/users/messages.json"
    if not os.path.exists(messages_file):
        return
    with open(messages_file, "r") as f:
        try:
            all_messages = json.load(f)
        except:
            all_messages = []
    updated = False
    for m in all_messages:
        if not isinstance(m, dict):
            continue
        if m.get("receiver_id") == user_id:
            m["read"] = True
            updated = True
    if updated:
        with open(messages_file, "w") as f:
            json.dump(all_messages, f, indent=4)

def main():
    print("Memulai program BlackChat Offline")
    user_manager = UserManager()
    nodes = {}
    current_user_id = None
    current_port = None

    while True:
        print("\nMenu:")
        print("1. Registrasi")
        print("2. Login")
        print("3. Tambah Kontak")
        print("4. Kirim Pesan")
        print("5. Buat Grup")
        print("6. Tambah Anggota Grup")
        print("7. Kirim Pesan Grup")
        print("8. Lihat Jaringan (ASCII)")
        print("9. Logout / Keluar")
        print("10. Lihat Pesan Belum Dibaca")
        choice = input("Pilih opsi (1-10): ")

        try:
            if choice == "1":
                username = input("Masukkan username: ")
                pin = input("Masukkan PIN: ")
                user_id, port = user_manager.register(username, pin)
                print(f"User terdaftar: {username} (ID: {user_id}, Port: {port})")

            elif choice == "2":
                username = input("Masukkan username: ")
                pin = input("Masukkan PIN: ")
                user_id, port = user_manager.login(username, pin)
                current_user_id, current_port = user_id, port

                if user_id not in nodes:
                    nodes[user_id] = P2PNode(port, user_id)
                    nodes[user_id].start()

                # === LOAD PEERS DARI FILE ===
                nodes[user_id].peers = load_peers(user_id)

                # === REGISTER CALLBACK NOTIF PESAN BARU ===
                nodes[user_id].register_new_message_callback(
                    lambda m: notify(f"Pesan baru dari {m['sender_id']}: {m['message']}")
                )

                print(f"Login berhasil: {username} (ID: {user_id}, Port: {port})")

            elif choice == "3":
                if not current_user_id:
                    print("Login dulu!")
                    continue
                contact_id = input("Masukkan user ID kontak: ")
                if contact_id not in user_manager.users:
                    print(f"User {contact_id} tidak ditemukan!")
                    continue
                user_manager.add_contact(current_user_id, contact_id)
                nodes[current_user_id].peers[contact_id] = user_manager.users[contact_id]["port"]
                save_peer(current_user_id, contact_id, user_manager.users[contact_id]["port"])
                print(f"Kontak ditambahkan: {contact_id}")

            elif choice == "4":
                if not current_user_id:
                    print("Login dulu!")
                    continue
                contacts = user_manager.get_contacts(current_user_id)
                if not contacts:
                    print("Belum ada kontak!")
                    continue
                print("Kontak tersedia:", list(contacts.keys()))
                receiver_id = input("Masukkan user ID penerima: ")
                if receiver_id not in contacts:
                    print("Kontak tidak ditemukan!")
                    continue
                message = input("Masukkan pesan: ")

                # Simpan pesan ke messages.json
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
                    "sender_id": current_user_id,
                    "receiver_id": receiver_id,
                    "message": message,
                    "timestamp": time.time(),
                    "read": False
                }
                all_messages.append(new_message)
                with open(messages_file, "w") as f:
                    json.dump(all_messages, f, indent=4)

                # Kirim melalui node
                chat_manager = ChatManager(nodes[current_user_id])
                chat_manager.send_direct_message(current_user_id, receiver_id, contacts[receiver_id], message)
                notify(f"Pesan terkirim ke {receiver_id}")

            elif choice == "5":
                if not current_user_id:
                    print("Login dulu!")
                    continue
                group_name = input("Masukkan nama grup: ")
                group = Grup(group_name, current_user_id)
                group.add_member(current_user_id, current_port)
                group.save()
                nodes[current_user_id].add_group(group)
                print(f"Grup dibuat: {group_name} (ID: {group.group_id})")

            elif choice == "6":
                if not current_user_id:
                    print("Login dulu!")
                    continue
                group_id = input("Masukkan ID grup: ")
                user_id_add = input("Masukkan user ID untuk ditambahkan: ")
                if user_id_add not in user_manager.users:
                    print(f"User {user_id_add} tidak ditemukan!")
                    continue
                port = user_manager.users[user_id_add]["port"]
                group_file = f"blackchat/data/groups/group_{group_id}.json"
                if not os.path.exists(group_file):
                    print(f"Grup {group_id} tidak ditemukan!")
                    continue
                with open(group_file, "r") as f:
                    group_data = json.load(f)
                group = Grup(group_data["name"], group_data["creator_id"])
                group.members = group_data["members"]
                group.add_member(user_id_add, port)
                group.save()
                nodes[current_user_id].add_group(group)
                print(f"Anggota {user_id_add} ditambahkan ke grup {group_id}")

            elif choice == "7":
                if not current_user_id:
                    print("Login dulu!")
                    continue
                group_id = input("Masukkan ID grup: ")
                if group_id not in nodes[current_user_id].groups:
                    print(f"Grup {group_id} tidak ditemukan!")
                    continue
                message = input("Masukkan pesan grup: ")
                chat_manager = ChatManager(nodes[current_user_id])
                chat_manager.send_group_message(current_user_id, group_id, message)
                notify(f"Pesan grup terkirim ke {group_id}")

            elif choice == "8":
                if not current_user_id:
                    print("Login dulu!")
                    continue
                nodes[current_user_id].print_network()

            elif choice == "9":
                break

            elif choice == "10":
                if not current_user_id:
                    print("Login dulu!")
                    continue
                unread = get_unread_messages(current_user_id)
                if not unread:
                    print("Tidak ada pesan belum dibaca.")
                else:
                    print("Pesan belum dibaca:")
                    for m in unread:
                        sender_name = user_manager.users.get(m.get("sender_id", ""), {}).get("username", m.get("sender_id", "Unknown"))
                        print(f"Dari {sender_name}: {m.get('message', '')}")
                    mark_messages_as_read(current_user_id)
                    notify(f"{len(unread)} pesan telah dibaca.")

        except Exception as e:
            print(f"Error: {e}")

    for node in nodes.values():
        node.stop()
    print("Program selesai")

if __name__ == "__main__":
    main()

