# TODO load/unload/reload etc.

import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

PRODUCTION: bool = bool(int(os.getenv('PRODUCTION')))
NO_TYPING_COMMANDS: list = os.getenv('NO_TYPING_COMMANDS').split()
PREFIX: str = str(os.getenv('PREFIX'))

intents: discord.Intents = discord.Intents(
    messages=True,
    guilds=True
)

bot: commands.Bot = commands.Bot(command_prefix=f'{PREFIX} ', case_insensitive=True,
                                 intents=intents, help_command=None,
                                 guild_ready_timeout=1, max_messages=None,
                                 description='Seamless GitHub-Discord integration.',
                                 fetch_offline_members=False)

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s: %(message)s')
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logger: logging.Logger = logging.getLogger('main')

extensions: list = [
    'core.background.release_feed',
    'core.background.misc',
    'core.debug',
    'cogs.github.base.user',
    'cogs.github.base.org',
    'cogs.github.base.repo',
    'cogs.github.numbered.pr',
    'cogs.github.numbered.issue',
    'cogs.github.complex.gist',
    'cogs.github.other.lines',
    'cogs.github.other.info',
    'cogs.github.other.license',
    'cogs.ecosystem.help',
    'cogs.ecosystem.config',
    'cogs.ecosystem.bot_info',
    'cogs.handle.errors',
    'cogs.handle.events'
]

if PRODUCTION:
    extensions.extend([f'cogs.botlists.{file[:-3]}' for file in os.listdir('cogs/botlists')])

for extension in extensions:
    logger.info(f'Loading {extension}...')
    bot.load_extension(extension)


@bot.check
async def global_check(ctx: commands.Context) -> bool:
    if not isinstance(ctx.channel, discord.DMChannel) and ctx.guild.unavailable:
        return False

    return True


@bot.before_invoke
async def before_invoke(ctx: commands.Context) -> None:
    if str(ctx.command) not in NO_TYPING_COMMANDS:
        await ctx.channel.trigger_typing()


@bot.event
async def on_ready() -> None:
    logger.info(f'The bot is ready.')
    logger.info(f'discord.py version: {discord.__version__}\n')


if __name__ == '__main__':
    bot.run(os.getenv('BOT_TOKEN'))
