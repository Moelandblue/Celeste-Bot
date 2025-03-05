import datetime
import logging
import os
from pkgutil import iter_modules
from typing import Literal, Optional

import discord
from discord.ext import commands
import dotenv
import aiosqlite


class MyBot(commands.Bot):
    def __init__(self, command_prefix, *, intents: discord.Intents) -> None:
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db = None

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        # Load database
        bot.db = await aiosqlite.connect('bot.db')
        print('Successfully connected to database')

        # Load extensions
        for extension in iter_modules(['extensions']):
            await self.load_extension(f'extensions.{extension.name}')


dotenv.load_dotenv()
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all() # Overkill for now
bot = MyBot(command_prefix=".", intents=intents)


@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    """
    Umbra's CommandTree sync
    https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html
    """
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


@bot.tree.command()
async def help(interaction: discord.Interaction):
    """Bot information and help"""
    embed = discord.Embed(
        color=discord.Color.blue(),
        title=bot.user.display_name,
        description="*This is going to be a heist of a lifetime!*\n",
        timestamp=datetime.datetime.now(datetime.UTC)
    )
    embed.set_thumbnail(url=bot.user.display_avatar)

    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(os.getenv('DISCORD_TOKEN'), log_handler=handler, log_level=logging.DEBUG, root_logger=True)
