# Using https://discordpy.readthedocs.io/en/latest/index.html
import discord
from discord.ext import commands
from json import load

# Reading configs.json into config (token, etc.)
with open("discord/config.json", "r") as config_file:
	config: dict[str,str] = load(config_file)

# This seems to be just necessary for the bot authorization. I did not understand in detail
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
# command_prefix is a string specifying what the commands for the bot look like. By default, "/"

# Initialization of the function responsible for the bot's response to the command "<prefix>ping"
@bot.command("ping")
async def Ping(ctx: commands.context):
	await ctx.send("pong")


# Launching function
def launch():
	bot.run(config["token"])


if __name__ == "__main__":
	launch()