import os
import discord
from discord.ext import commands

from config import *
from image_generator import create_welcome_card

# ==========================
# BOT SETUP
# ==========================

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ==========================
# READY
# ==========================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("=" * 50)

# ==========================
# MEMBER JOIN
# ==========================

@bot.event
async def on_member_join(member):

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel is None:
        print("Welcome channel not found.")
        return

    try:

        image = await create_welcome_card(member)

        file = discord.File(
            image,
            filename="welcome.png"
        )

        await channel.send(
            content=f"**Hey {member.mention}, welcome to Cashout RP!**",
            file=file
        )

        if os.path.exists(image):
            os.remove(image)

    except Exception as e:
        print(f"Error sending welcome card: {e}")


# ==========================
# TEST COMMAND
# ==========================

@bot.command(name="testwelcome")
@commands.has_permissions(administrator=True)
async def testwelcome(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    image = await create_welcome_card(member)

    file = discord.File(
        image,
        filename="welcome.png"
    )

    await ctx.send(
        content=f"**Hey {member.mention}, welcome to Cashout RP!**",
        file=file
    )

    if os.path.exists(image):
        os.remove(image)


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


# ==========================
# START BOT
# ==========================

bot.run(TOKEN)