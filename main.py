import os
import threading
import discord
import pickle
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DATA_FILE = 'pregnant_man_counts.pkl'
ADMIN_ID = 253739732276740096

# Print token status
print(f"[INIT] DISCORD_TOKEN loaded: {bool(TOKEN)}")

# Initialize Flask app
app = Flask(__name__)
print("[INIT] Flask app initialized.")

@app.route('/render-health')
def render_health_check():
    print("[FLASK] /render-health endpoint called.")
    return "OK", 200

@app.route('/')
def health_check():
    print("[FLASK] / endpoint called.")
    return "🤖 Bot is running!", 200

# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
print("[INIT] Discord client initialized.")

# Data management
try:
    with open(DATA_FILE, 'rb') as f:
        pregnant_man_counts = pickle.load(f)
    print(f"[DATA] Loaded data from {DATA_FILE}.")
except FileNotFoundError:
    pregnant_man_counts = {}
    print(f"[DATA] {DATA_FILE} not found. Starting with empty counts.")

def save_counts():
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(pregnant_man_counts, f)
    print("[DATA] Counts saved.")

# Command handlers
async def handle_pregnant_count(message):
    user = message.mentions[0] if message.mentions else message.author
    count = pregnant_man_counts.get(str(user.id), 0)
    print(f"[COMMAND] !pregnantcount by {message.author} for {user} (count={count})")
    await message.channel.send(f"{user.mention} has {count} 🫃 reactions!")

async def handle_gif_reaction(message):
    replied_message = await message.channel.fetch_message(message.reference.message_id)
    await replied_message.add_reaction('🫃')
    user_id = str(replied_message.author.id)
    pregnant_man_counts[user_id] = pregnant_man_counts.get(user_id, 0) + 1
    save_counts()
    print(f"[COMMAND] GIF reaction handled for {replied_message.author} (new count={pregnant_man_counts[user_id]})")

async def handle_reset(message):
    if message.mentions:
        for user in message.mentions:
            if (user_id := str(user.id)) in pregnant_man_counts:
                del pregnant_man_counts[user_id]
        print(f"[COMMAND] Reset counts for {len(message.mentions)} user(s) by {message.author}.")
        await message.channel.send(f"🧹 Reset counts for {len(message.mentions)} user(s)!")
    else:
        pregnant_man_counts.clear()
        print(f"[COMMAND] Nuked all pregnancy counts by {message.author}.")
        await message.channel.send("🧹 Nuked all pregnancy counts!")
    save_counts()

# Discord events
@client.event
async def on_ready():
    print(f"[DISCORD] {client.user} has connected to Discord!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f"[DISCORD] Message received: '{message.content}' from {message.author}")

    message_split = message.content.lower().split()
    if not message_split:
        return

    try:
        if message_split[0] == '!pregnantcount':
            await handle_pregnant_count(message)
        elif message_split[0] == '!reset' and message.author.id == ADMIN_ID:
            await handle_reset(message)
        elif (message.reference and
              message.content.startswith("https://tenor.com/view/jarvis-react-this-user-pregnant-man-gif")):
            await handle_gif_reaction(message)
    except Exception as e:
        print(f"[ERROR] Error handling message: {e}")
        await message.channel.send("❌ Something went wrong!")

def run_flask():
    port = int(os.getenv('PORT', 10000))
    print(f"[FLASK] Starting Flask on port {port}...")
    app.run(host='0.0.0.0', port=port)

def run_bot():
    print("[DISCORD] Starting Discord bot...")
    client.run(TOKEN)

if __name__ == "__main__":
    print("[MAIN] Starting Flask thread...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("[MAIN] Running Discord bot in main thread.")
    run_bot()
