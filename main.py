import os
import discord
import pickle
from dotenv import load_dotenv

# Configuration
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DATA_FILE = 'pregnant_man_counts.pkl'
ADMIN_ID = 253739732276740096

# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Data management
try:
    with open(DATA_FILE, 'rb') as f:
        pregnant_man_counts = pickle.load(f)
except FileNotFoundError:
    pregnant_man_counts = {}


# Pregnant Functions
def save_counts():
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(pregnant_man_counts, f)


# Command handlers
async def handle_pregnant_count(message):
    user = message.mentions[0] if message.mentions else message.author
    count = pregnant_man_counts.get(str(user.id), 0)
    await message.channel.send(f"{user.mention} has {count} 🫃 reactions!")


async def handle_gif_reaction(message):
    replied_message = await message.channel.fetch_message(message.reference.message_id)
    await replied_message.add_reaction('🫃')
    user_id = str(replied_message.author.id)
    pregnant_man_counts[user_id] = pregnant_man_counts.get(user_id, 0) + 1
    save_counts()


async def handle_reset(message):
    if message.mentions:
        for user in message.mentions:
            if (user_id := str(user.id)) in pregnant_man_counts:
                del pregnant_man_counts[user_id]
        await message.channel.send(f"🧹 Reset counts for {len(message.mentions)} user(s)!")
    else:
        pregnant_man_counts.clear()
        await message.channel.send("🧹 Nuked all pregnancy counts!")
    save_counts()
###################################


# Event handlers
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    message_split = message.content.lower().split()
    if not message_split:
        return

    try:
        # Pregnant stuff
        if message_split[0] == '!pregnantcount':
            await handle_pregnant_count(message)

        elif (message_split[0] == '!reset'
              and message.author.id == ADMIN_ID):
            await handle_reset(message)

        elif (message.reference
              and message.content == "https://tenor.com/view/jarvis-react-this-user-pregnant-man-gif"
                                     "-7314513712895381143"):
            await handle_gif_reaction(message)
        ######################

    except Exception as e:
        print(f"Error handling message: {e}")
        await message.channel.send("❌ Something went wrong!")


client.run(TOKEN)
