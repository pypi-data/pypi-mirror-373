import os

def notify(message):
    try:
        # Termux notification
        os.system(f"termux-notification -t 'BlackChat' -c '{message}'")
    except:
        print(f"NOTIF: {message}")

