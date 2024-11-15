import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime

# Load configurations from .env file
load_dotenv()
TOKEN = ('MTI5MTEyMDc4MjQzNjQ3MDc4NQ.G9U47c.lUIFPklQucl3_3FfGOft5HX7aSzv4PJPUMVnCk')

intents = discord.Intents.default()
intents.presences = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
game_activity_channels = {}  # Dictionary to store guild_id -> channel_id mapping
user_game_status = {}
user_playtime = {}

COOLDOWN = 20  # Cooldown for activity log in seconds


@bot.event
async def on_ready():
    print(f'🎮 Logged in as {bot.user} - Ready to monitor game activity!')
    try:
        await bot.tree.sync()
        print("Commands synced successfully.")
    except Exception as e:
        print(f"Error syncing commands: {e}")


# Slash command to fetch the server (guild) ID
@bot.tree.command(name="get_guild_id", description="Get the server's ID for configuration purposes.")
async def get_guild_id(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"The server ID for **{interaction.guild.name}** is `{interaction.guild.id}`. Use this ID when configuring activity logs.",
        ephemeral=True,
    )


# Slash command to set the game activity log channel
@bot.tree.command(name="set_game_activity_channel", description="Set the channel to log game activities. Use `/get_guild_id` to fetch the server ID.")
@app_commands.describe(
    guild_id="The ID of the server (guild) to monitor.",
    channel="The channel to log game activities."
)
async def set_game_activity_channel(interaction: discord.Interaction, guild_id: int, channel: discord.TextChannel):
    if interaction.guild.id != guild_id:
        await interaction.response.send_message(
            "The server ID you entered does not match this server. Please double-check and try again.",
            ephemeral=True,
        )
        return

    # Save the channel for the given guild
    game_activity_channels[guild_id] = channel.id
    await interaction.response.send_message(
        f"Game activity logs for **{interaction.guild.name}** will now be sent to {channel.mention}.",
        ephemeral=True,
    )


@bot.event
async def on_presence_update(before, after):
    # Check if activity log channel is set for the guild
    guild_id = after.guild.id
    if guild_id not in game_activity_channels:
        return

    channel_id = game_activity_channels[guild_id]
    channel = bot.get_channel(channel_id)
    if not channel or not isinstance(channel, discord.TextChannel):
        print(f"❌ Channel not found or invalid for guild {guild_id}.")
        return

    # Ignore bots
    if after.bot:
        return

    # Track activity
    current_time = datetime.datetime.utcnow()
    current_activity = None
    for activity in after.activities:
        if activity.type == discord.ActivityType.playing:
            current_activity = activity.name
            break

    last_activity, last_sent = user_game_status.get(after.id, (None, datetime.datetime.min))
    play_start_time = user_playtime.get(after.id, None)

    # Handle activity start
    if current_activity and current_activity != last_activity and (current_time - last_sent).total_seconds() >= COOLDOWN:
        embed = discord.Embed(
            title=f"🎮 Game Started: **{current_activity}**",
            description=f"{after.mention} has just launched **{current_activity}**!",
            color=discord.Color.green(),
            timestamp=current_time,
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.add_field(name="👤 Player", value=f"{after.name}", inline=True)
        embed.add_field(name="🎮 Game", value=current_activity, inline=True)
        embed.set_footer(text="Game activity detected!")

        await channel.send(embed=embed)

        user_game_status[after.id] = (current_activity, current_time)
        user_playtime[after.id] = current_time  # Track playtime start

    # Handle activity stop
    elif last_activity and not current_activity and (current_time - last_sent).total_seconds() >= COOLDOWN:
        play_duration = (current_time - play_start_time).total_seconds() if play_start_time else 0
        play_duration_minutes = play_duration // 60
        embed = discord.Embed(
            title=f"🛑 Game Ended: **{last_activity}**",
            description=f"{after.mention} has stopped playing **{last_activity}** after {play_duration_minutes} minutes of fun! 🎮",
            color=discord.Color.red(),
            timestamp=current_time,
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.add_field(name="👤 Player", value=f"{after.name}", inline=True)
        embed.add_field(name="🕒 Playtime", value=f"{play_duration_minutes} minutes", inline=True)
        embed.add_field(name="🎮 Last Game", value=last_activity, inline=False)
        embed.set_footer(text="Game session ended! Time for a break? 🛋️")

        await channel.send(embed=embed)

        user_game_status[after.id] = (None, current_time)
        user_playtime.pop(after.id, None)  # Remove playtime tracking

bot.run(TOKEN)
