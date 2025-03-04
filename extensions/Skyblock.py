import discord
from discord import app_commands

@app_commands.command()
async def flip(interaction: discord.Interaction, money: int, max_items: int):
    pass # TODO: Implement

async def setup(bot):
    bot.tree.add_command(flip)
