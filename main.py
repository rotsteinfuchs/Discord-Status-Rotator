import requests
import time
import random
import json
import os
from colorama import init, Fore


def read_statuses(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]


def get_user_info(token):
    header = {"authorization": token}
    r = requests.get("https://discord.com/api/v10/users/@me", headers=header)
    if r.status_code == 200:
        user_info = r.json()
        return user_info["username"], True
    else:
        return "Invalid token", False


def change_status(token, message, emoji_name, emoji_id, status):
    header = {"authorization": token}

    current_status = requests.get(
        "https://discord.com/api/v10/users/@me/settings", headers=header
    ).json()

    custom_status = current_status.get("custom_status", {})
    if custom_status is None:
        custom_status = {}
    custom_status["text"] = message
    custom_status["emoji_name"] = emoji_name
    if emoji_id:
        custom_status["emoji_id"] = emoji_id

    jsonData = {
        "custom_status": custom_status,
        "activities": current_status.get("activities", []),
        "status": status,
    }

    r = requests.patch(
        "https://discord.com/api/v10/users/@me/settings", headers=header, json=jsonData
    )
    return r.status_code


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def load_config():
    with open("config.json", "r") as file:
        return json.load(file)


def color_text(text, color_code):
    return f"{color_code}{text}{Fore.RESET}"


init()

config = load_config()
token = config["token"]
clear_enabled = config["clear_enabled"]
clear_interval = config["clear_interval"]
speed_rotator = config["speed_rotator"]
status_sequence = config["status_sequence"]

status_count = random.randint(0, len(status_sequence))
emoji_count = 0

while True:
    current_status = status_sequence[status_count % len(status_sequence)]
    user_info, is_valid_token = get_user_info(token)
    statuses = read_statuses("text.txt")
    emojis = read_statuses("emojis.txt")

    status = statuses[status_count % len(statuses)]
    time_formatted = color_text(time.strftime("%I:%M %p:"), Fore.MAGENTA)
    if is_valid_token:
        token_color_code = Fore.GREEN
    else:
        token_color_code = Fore.RED
    token_masked = token[:6] + "******"
    token_info = f"{token_masked} | {user_info}"
    token_colored = color_text(token_info, token_color_code)
    status_colored = color_text(status, Fore.CYAN)

    emoji_data = emojis[emoji_count % len(emojis)].split(":")
    if len(emoji_data) == 2:
        emoji_name, emoji_id = emoji_data
    elif len(emoji_data) == 1:
        emoji_name = emoji_data[0]
        emoji_id = None
    else:
        print(f"Invalid emoji: {emojis[emoji_count % len(emojis)]}")
        continue

    print(
        f"{time_formatted} Status changed for: {token_colored}. New status message: {status_colored}. | Emoji: ({emoji_name}) | Status: {current_status}"
    )
    change_status(token, status, emoji_name, emoji_id, current_status)

    status_count += 1
    emoji_count += 1

    if speed_rotator > 0:
        time.sleep(speed_rotator)
    else:
        quit()
    if clear_enabled and status_count % clear_interval == 0:
        clear_console()
