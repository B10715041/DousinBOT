from discord.ext import commands
from vndb_api_utils import format_vndb_response_as_embed, search_vndb
import asyncio
import discord
import json

with open('config.json', 'r') as file:
    config = json.load(file)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Event listener for when the bot is ready
@bot.event
async def on_ready():
    if bot.user is None:
        print('Not not connected')
    else:
        print(f'Logged in as {bot.user.name}')

# Command to echo back what the user said
@bot.command(name='echo')
async def echo(ctx, *, content:str):
    await ctx.send(content)

@bot.command(name='clear')
async def clear(ctx, num: int):
    await ctx.channel.purge(limit=num + 1)

bot.remove_command('help')
@bot.command(name='help')
async def help_command(ctx):
    help_text = (
        "**Commands and Features:**\n"
        "- `!echo [message]`: The bot will repeat whatever message you write.\n"
        "- `!clear [number]`: Deletes the specified number of messages from the channel.\n"
        "- `!help`: Shows this help message.\n"
        "- Query VNDB: Typing `?[search term]` triggers a search in the VNDB. For example:\n"
        "   - `?hamidashi` searches for 'hamidashi'\n"
        "  - `?ハミダシクリエイティブ` searches for 'ハミダシクリエイティブ'\n"
        "The bot responds with information about the visual novel, including title, aliases, developer, release date, length, rating, vote count, and a link. It also lists voice actors and staff involved, with hyperlinks to their VNDB pages."
    )
    await ctx.send(help_text)

@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author.bot:
        return

    # Check if the message starts with '?' for search
    if message.content.startswith('?'):
        search_query = message.content[1:].strip()

        async with message.channel.typing():
            # Call the VNDB API with the search query
            response_data = await search_vndb(search_query)

            response_msg = ""
            embed = ""
            embed2 = ""
            if isinstance(response_data, str):
                # If response_data is a string, an error occurred.
                # await message.channel.send(response_data)
                response_msg = response_data
            else:
                for entry in response_data['results']:
                    if 'titles' in entry and entry['titles']:
                        print(entry['titles'][0]['title'])
                # Successfully retrieved data, create an embed to send it
                embed, embed2 = format_vndb_response_as_embed(response_data)
                response_msg = "幫お兄ちゃん找到囉"

            await message.channel.send(f"{message.author.mention} {response_msg}")
            await message.channel.send(embed=embed)
            await message.channel.send(embed=embed2)
            await asyncio.sleep(1)

        return  # Return to avoid processing commands

    # Process other commands
    await bot.process_commands(message)


# Replace 'YOUR_TOKEN_HERE' with your bot's token
bot.run(config['token'])



