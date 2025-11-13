import requests
import time
from datetime import datetime, timezone

ROBLOX_USER_IDS = [1026846981, 135106764, 608068734, 621488192, 720933785, 1228398060, 1517498817, 469684156, 1389647597, 452788654, 447289994, 1172283846, 1121492811, 59398350, 939726156, 1605582402, 857870527, 859957015, 1578310743, 885345063, 1613055156, 1628142302, 58410128, 198883329, 1026016004]
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1437486956090232842/WPZoJGi9fLqGwJpLmPBQESJsH-KEk4I0F0G_jBWd7b7oR0DIsBFqv-yzKAGbOeQQRhqT"
PING_MENTION = "<@&1437491686254051379>"
ROBLOX_COOKIE = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhACIhsKBGR1aWQSEzI5MjA5NDQ1MjMwNDAxNzk5NjIoAQ.s3O2Hk_T8wdKMmQIJP33cfthNW0EEsiGsBKquERmm-MWc4J2IvKQR-TQuHYQAKYtrthueDKVxB3qavYPpdSWZ_xbMH4Cj90oVykd-WOOavXo2Tnxjq-AWcr21VhiQZ-lr96dzbteSFay8BKjbckDPckusAeK7o0X8dGlkNdWiobnBcVGZSWJwj6nnGfzuE6sMlNlnCJMMTLxrnx3K1IVJLmZ5DPeIDEiW_In796yU1l6wqLOAeH1VTgTAClcCzJyjK5_540TIIe8OHwIw5VRZdMBGi1AQ255-xPhO0kSvVeSbOIObwJzyDX81TqkFmWYDHzE3dSvEpFtEoQwvHpaYvzpb657UIbtK6s5un_xiDXbSm6h8-zLuVQ43QoslOzvKJg3soBYJ5AUlJ7AUExcWPNiJt2zCYI06JArt7Cb3KP_DQ9yS8OhbBaWaApe8Dm2lV1XuIg1B7hPQpXgArXu9yAJpkdt2pNKONPuKIl5uZDf0O9AhTRx1d4ZzkNeI8c6WPNggmqDisz2lbxHwfwuJXdPDd6pU9HTQWHxeSi739jTdT3Fahae8ZhpNpVAetvd7eKtFhuK8G8Mu_hzOHDJi6YwalTUJWhbmljrrArjXlcMNZbmWS-w-qt8nYtKg87a2-0GsSFeg9rv2m1A1a2te9zOU6LNo9OrT-Vh4ol_b8bpvEWCEtQa2x6GbvCLe43fft7Y9P47yplXB1bR51Dejk_7bbv93s4p-o0pMGBXqKvXbukTHFq28Q9_ZymFAB-j3umP_Rsl2w60rLHWZkhciCBMJLxgu3OF83QAXe2qRmG8ape3zjE_hmZ7NRS_1-nLEriTA_1jsJuG-W-8kR2oSXHdWf_qdpodY4rFm-pCqaSfoO6D8WMIg4AUMRYLEcvEukbtUAQV1UdacEK_XylbSEx0vzWKPABQmYUpAD3Ww30SGwHO2EypixROkNuME3AKjB_8WJT2omjJXPtpGH6O15QAo0OfgxODHNAPJEp2hgwHf_YPaXId3yMeA1JSnkKAbpW9klY5hSjcfbyDqgLuiQowtBdcYcBGWBFgh-bedQ8kKoywc8cQbXycJChpeleDCMZHNEauX_uiGUDqyX8S_1Ah0zg2zTZKmZN-0IyImbQnwlNTrZctknvdDWXD6KlHO4MMnjJHNcd7wLdDzGtBW2XSd-c"

CSRF_TOKEN = None

usage_counter = 0

def fetch_usernames(user_ids):
    url = "https://users.roblox.com/v1/users"
    response = requests.post(url, json={"userIds": user_ids})
    if response.status_code == 200:
        data = response.json()["data"]
        return {user["id"]: user["name"] for user in data}
    else:
        raise Exception("Failed to fetch usernames")

def fetch_avatars(user_ids):
    if not user_ids:
        return {}
    user_ids_str = ','.join(map(str, user_ids))
    url = f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={user_ids_str}&size=150x150&format=Png&isCircular=false"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "data" not in data:
            print("Avatar API response missing 'data' field")
            return {}
        return {str(d["targetId"]): d["imageUrl"] for d in data["data"] if d.get("state") in ["0", "Completed"]}
    except requests.exceptions.HTTPError as e_http:
        print(f"HTTP error fetching avatars: {e_http} - Response: {response.text}")
        return {}
    except Exception as e:
        print(f"Error fetching avatars: {e}")
        return {}

def fetch_presences(user_ids):
    global CSRF_TOKEN
    url = "https://presence.roblox.com/v1/presence/users"
    headers = {
        "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    if CSRF_TOKEN:
        headers["X-CSRF-TOKEN"] = CSRF_TOKEN
    response = requests.post(url, headers=headers, json={"userIds": user_ids})
    if response.status_code == 403:
        new_csrf = response.headers.get("x-csrf-token")
        if new_csrf:
            CSRF_TOKEN = new_csrf
            headers["X-CSRF-TOKEN"] = new_csrf
            response = requests.post(url, headers=headers, json={"userIds": user_ids})
    if response.status_code == 200:
        data = response.json()["userPresences"]
        return {pres["userId"]: pres for pres in data}
    else:
        print(f"Presence API failed: {response.status_code} - {response.text}")
        raise Exception("Failed to fetch presences")

def fetch_game_icon(universe_id):
    if not universe_id:
        return None
    url = f"https://thumbnails.roblox.com/v1/games/icons?universeIds={universe_id}&returnPolicy=PlaceHolder&size=256x256&format=Png&isCircular=false"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data or "data" not in data or not data["data"]:
            print(f"Game icon API response for universe {universe_id} has no valid data array")
            return None
        if data["data"][0].get("state") in ["0", "Completed"]:
            return data["data"][0]["imageUrl"]
        else:
            print(f"Game icon for universe {universe_id} not ready (state: {data['data'][0].get('state')})")
            return None
    except requests.exceptions.HTTPError as e_http:
        print(f"HTTP error fetching game icon for universe {universe_id}: {e_http} - Response: {response.text}")
        return None
    except Exception as e:
        print(f"Error fetching game icon for universe {universe_id}: {e}")
    return None

def send_discord_notification(content, embed):
    embed["timestamp"] = datetime.now(timezone.utc).isoformat()
    embed["footer"] = {"text": "daniwani online tracker"}
    data = {"content": content, "embeds": [embed]}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code not in (200, 204):
        print(f"Failed to send Discord message: {response.status_code} - {response.text}")

usernames = fetch_usernames(ROBLOX_USER_IDS)
avatars = fetch_avatars(ROBLOX_USER_IDS)
previous_states = {user_id: {"type": None, "universe": None} for user_id in ROBLOX_USER_IDS}

print("Starting monitoring...")
print(f"Usernames: {usernames}")
print(f"Avatars: {avatars}")
while True:
    try:
        presences = fetch_presences(ROBLOX_USER_IDS)
        for user_id, pres in presences.items():
            username = usernames.get(user_id, str(user_id))
            user_avatar = avatars.get(str(user_id))
            curr_type = pres["userPresenceType"]
            curr_universe = pres.get("universeId", None)
            place_id = pres.get("placeId", None)
            job_id = pres.get("gameId", None)
            prev_type = previous_states[user_id]["type"]
            prev_universe = previous_states[user_id]["universe"]

            print(f"User {username} ({user_id}):")
            print(f"  type: {curr_type}, universe: {curr_universe}, place: {place_id}, job: {job_id}")
            print(f"  lastLocation: {pres.get('lastLocation', 'None')}")
            print(f"  prev_type: {prev_type}, prev_universe: {prev_universe}")

            notify = False
            if prev_type is not None and curr_type != prev_type:
                notify = True
            elif curr_type == 2 and curr_universe != prev_universe:
                notify = True

            if notify:
                embed = {"color": 0}
                embed["author"] = {
                    "name": username,
                    "url": f"https://www.roblox.com/users/{user_id}/profile",
                    "icon_url": user_avatar
                }
                if user_avatar:
                    embed["thumbnail"] = {"url": user_avatar}

                if curr_type == 0:
                    embed["title"] = f"{username} went offline"
                    embed["color"] = 0xFF0000
                    embed["description"] = "😴"
                elif curr_type == 1:
                    embed["title"] = f"{username} went online"
                    embed["color"] = 0x5865F2
                    embed["description"] = "🔵"
                elif curr_type == 2:
                    game_name = pres.get("lastLocation", "Unknown Game")
                    embed["title"] = f"{username} joined {game_name}"
                    embed["color"] = 0x00FF00
                    embed["description"] = 'Click "Join" to join their experience!'
                    if curr_universe:
                        game_icon = fetch_game_icon(curr_universe)
                        if game_icon:
                            embed["thumbnail"] = {"url": game_icon}
                    fields = []
                    if place_id:
                        fields.append({
                            "name": "Game Page",
                            "value": f"[View](https://www.roblox.com/games/{place_id}/)",
                            "inline": True
                        })
                    if place_id and job_id:
                        join_url = f"https://www.roblox.com/games/start?placeId={place_id}&gameInstanceId={job_id}"
                        fields.append({
                            "name": "Join Server",
                            "value": f"[Join]({join_url})",
                            "inline": True
                        })
                    if fields:
                        embed["fields"] = fields

                print(f"Sending embed for {username} (type {curr_type})")
                send_discord_notification(PING_MENTION, embed)

            previous_states[user_id]["type"] = curr_type
            previous_states[user_id]["universe"] = curr_universe

        usage_counter += 1
        print("\nAmount of total script iterations: " + str(usage_counter))
        time.sleep(60)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)