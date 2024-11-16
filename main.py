import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os
import datetime

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 5))
COOLDOWN = int(os.getenv('COOLDOWN', 20))
EXCLUDED_ACTIVITIES = os.getenv('EXCLUDED_ACTIVITIES', '').split(',')

intents = discord.Intents.default()
intents.presences = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

DEFAULT_GAME_ICON = "https://cdn.discordapp.com/attachments/1295110482520313864/1307284982259253309/ei_1731751379775-removebg-preview.png?ex=6739bf83&is=67386e03&hm=1736147d92f589698d659cd3870aafd31704ffcd2361742c41a33fca0187f813&"

user_game_status = {}
user_playtime = {}

def get_thumbnail():
    return DEFAULT_GAME_ICON

@client.event
async def on_ready():
    global guild, channel
    guild = client.get_guild(GUILD_ID)
    channel = client.get_channel(CHANNEL_ID)

    if not guild or not channel:
        print("❌ Could not access guild or channel!")
        return

    print(f'🎮 Logged in as {client.user} - Monitoring game/App activity for all online members! Made by @Timmy053')

@client.event
async def on_presence_update(before, after):
    global guild, channel

    if after.bot:
        return

    current_time = datetime.datetime.utcnow()
    current_activity = after.activity.name if after.activity and after.activity.type == discord.ActivityType.playing else None

    if current_activity in EXCLUDED_ACTIVITIES:
        return

    last_activity, last_sent = user_game_status.get(after.id, (None, datetime.datetime.min))
    play_start_time = user_playtime.get(after.id, None)

    if current_activity and current_activity != last_activity and (current_time - last_sent).total_seconds() >= COOLDOWN:
        embed = discord.Embed(
            title=f"🎮 Game/App Started: **{current_activity}**",
            description=f"{after.mention} has just launched **{current_activity}**!",
            color=discord.Color.green(),
            timestamp=current_time
        )
        embed.set_thumbnail(url=get_thumbnail())
        embed.add_field(name="👤 Player/User", value=f"{after.name}", inline=True)
        embed.add_field(name="🎮 Game/App", value=current_activity, inline=True)
        embed.set_footer(text="Game/App activity detected!")

        await channel.send(embed=embed)

        user_game_status[after.id] = (current_activity, current_time)
        user_playtime[after.id] = current_time

    elif last_activity and not current_activity and (current_time - last_sent).total_seconds() >= COOLDOWN:
        play_duration = (current_time - play_start_time).total_seconds() if play_start_time else 0
        play_duration_minutes = play_duration // 60

        embed = discord.Embed(
            title=f"🛑 Game/App Ended: **{last_activity}**",
            description=f"{after.mention} has stopped playing/using **{last_activity}** after {play_duration_minutes}!",
            color=discord.Color.red(),
            timestamp=current_time
        )
        embed.set_thumbnail(url=get_thumbnail())
        embed.add_field(name="👤 Player/User", value=f"{after.name}", inline=True)
        embed.add_field(name="🕒 Play/Usetime", value=f"{play_duration_minutes} minutes", inline=True)
        embed.add_field(name="🎮 Last Game/App", value=last_activity, inline=False)
        embed.set_footer(text="Game/App session ended! Time for a break? 🛋️")

        await channel.send(embed=embed)

        user_game_status[after.id] = (None, current_time)
        user_playtime.pop(after.id, None)

client.run(TOKEN)
