import discord,sqlite3,argparse,logging,time,asyncio
from discord.ext import commands
from discord.ext.commands import when_mentioned
import command_basics,referral_cog,dbobj,debug_cog,webhooks_cog
from util_classes import database
from config.config_vars import config
from discord_slash.context import ComponentContext
from discord_slash import SlashCommand
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from debug_cog import some_callback

# things you should do before running this bot:
# - install dependencies (obviously)
# - fill in the config variables in config/config_vars.py . without those variables,
#   the bot will not function properly. the logging ones are just channel id's
# - make a database with at least one table (servers) according to the schema in
#   dbobj.py
# - Fill in the database file path in util_classes.py (there is a comment at the top
#   of the file that tells you where to go to replace)
# - (optional) change the name of the logger. if you're ok with the logger name being
#   "your-logger" (and you having to enter that whenever you want to load it), you're
#   all good and you don't have to change it. If you do want to change it, it's on line
#   number 111

class DiscordLogger(logging.Handler):

  def __init__(self, loggingChannel, bot, rateLimiting):
    logging.Handler.__init__(self)
    self.bot = bot
    self.loggingChannel = int(loggingChannel)
    self.lastSent = time.time()
    self.logStore = []
    self.rateLimiting = rateLimiting

  def emit(self, record):
    if self.rateLimiting == True:
      # Add to store and calculate current total message
      self.logStore.append("```{}```".format(self.format(record)))
      message = "".join(self.logStore)
      # Rate limiting, only send every 30 seconds or when length > 1500 chars
      if self.lastSent + (30) < time.time() or len(message) > 1500:
        channel = self.bot.get_channel(self.loggingChannel)
        asyncio.ensure_future(channel.send(message))
        self.lastSent = time.time()
        self.logStore = []
    # This channel isn't rate limited, just send
    else:
      channel = self.bot.get_channel(self.loggingChannel)
      asyncio.ensure_future(channel.send("```{}```".format(self.format(record))))

def get_prefix(bot, message):
    try:
      v = database.select_many(dbobj.servers, id=message.guild.id)
    except:
      return ["$"]
    #print(v[0][1])
    test = False
    if v != [] and v != None and test == False:
      templist = [v[0][1]]
      templist.extend(when_mentioned(bot,message))
      return templist
    else:
      return when_mentioned(bot,message)

# argparse setup
parser = argparse.ArgumentParser(description='Start the discord bot.')
parser.add_argument("-t","--testing",help="Activate testing mode. The bot will respond to other bots while in this mode. Not implemented yet, sorry.", action="store_true")

args = parser.parse_args()

# Initialize the bot object and pass in the get_prefix method
# as the way that the bot object will access prefixes and de-
# -termine which to use.

# https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.default()
intents.members = True

# client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Remove the bot's default help command, as I replace it in a
# different file with a more attractive help menu. You're we-
# -lcome.
bot.remove_command('help')

# Provide a simple printed message to signal that it is fini-
# -shed initializing as well as finished connecting to the d-
# -iscord client and is therefore online and ready to use.
@bot.event
async def on_ready():
  logger.info("Ready!")
  print("Ready!")

# Special error handling method. If it's the sort of error I
# haven't programmed a special handler for, simply raise it
# again.
@bot.event
async def on_command_error(ctx,error):
  if(isinstance(error, commands.errors.CommandNotFound)):
    await ctx.send('"{0}" is not a valid command.'.format(ctx.invoked_with))
  elif(isinstance(error, commands.errors.NoPrivateMessage)):
    await ctx.send('"{0}" can not be invoked outside of a server.'.format(ctx.invoked_with))
  elif(isinstance(error, commands.errors.CommandOnCooldown)):
    await ctx.send('Please wait **{0}** seconds before using that command.'.format(round(error.retry_after,1)))
  elif(isinstance(error, commands.errors.CheckFailure)):
    print("Someone did something they should not have...")
    name = ctx.command.qualified_name if ctx.command else "None"
    logger.exception("Permissions failure with command {0} in guild {1.name} ({1.id})\nUser {2.name} ({2.id}) attempted to use command, does not have permission.".format(name,ctx.guild,ctx.author))
  else:
    name = ctx.command.qualified_name if ctx.command else "None"
    await ctx.send("Command error. Please contact the developer if this persists.")
    #await ctx.send("```\n" + str(error) + "\n```")
    #print(str(error))
    logger.exception("Error with command {0} in guild {1.name} ({1.id}): {2}".format(name,ctx.guild,error))
    raise error

#@bot.event
async def on_component(ctx: ComponentContext):
  await ctx.edit_origin(content="This (otherwise non-functional) keypad has been interacted with at least once.")

async def min_keypad(ctx: ComponentContext):
  buttons = [create_button(style=ButtonStyle.primary, label="Expand", custom_id="expand_keypad")]
  actionrow = create_actionrow(*buttons)
  await ctx.edit_origin(components=[actionrow])

async def max_keypad(ctx: ComponentContext):
  buttons1 = [create_button(style=ButtonStyle.secondary, label=str(i), custom_id="btn_"+str(i)) for i in range(1,4)]
  buttons2 = [create_button(style=ButtonStyle.secondary, label=str(i), custom_id="btn_"+str(i)) for i in range(4,7)]
  buttons3 = [create_button(style=ButtonStyle.secondary, label=str(i), custom_id="btn_"+str(i)) for i in range(7,10)]
  buttons4 = [create_button(style=ButtonStyle.green, label="O", custom_id="btn_go"), create_button(style=ButtonStyle.secondary, label="0", custom_id="btn_0"), create_button(style=ButtonStyle.red, label="X", custom_id="btn_no")]

  action_row1 = create_actionrow(*buttons1)
  action_row2 = create_actionrow(*buttons2)
  action_row3 = create_actionrow(*buttons3)
  action_row4 = create_actionrow(*buttons4)
  await ctx.edit_origin(components=[action_row1, action_row2, action_row3, action_row4])

#slash.add_component_callback(some_callback,components=["green","grey"],use_callback_name=False)
btns = ["btn_"+str(i) for i in range(10)]
btns.extend(["btn_go"])
print(btns)
slash.add_component_callback(on_component, components=btns, use_callback_name=False)
slash.add_component_callback(min_keypad, components=["btn_no"], use_callback_name=False)
slash.add_component_callback(max_keypad, components=["expand_keypad"], use_callback_name=False)

# Load all of the cogs made in the other python files in this
# project. See the other files in the folder for more details
bot.add_cog(command_basics.general(bot))
bot.add_cog(referral_cog.referrals(bot))
bot.add_cog(debug_cog.debug(bot))
bot.add_cog(webhooks_cog.webhooks(bot))

infoformatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s - %(message)s','%Y-%m-%d %H:%M')
debugformatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s - %(message)s','%Y-%m-%d %H:%M:%S')

debug_log = DiscordLogger(config.log_debug, bot, True)
debug_log.setLevel(logging.DEBUG)
debug_log.setFormatter(debugformatter)

info_log = DiscordLogger(config.log_info, bot, False)
info_log.setLevel(logging.INFO)
info_log.setFormatter(infoformatter)

logger = logging.getLogger("your-logger") # fill this in
logger.setLevel(logging.DEBUG)
logger.addHandler(info_log)
logger.addHandler(debug_log)


# Run the bot using the token generated by the Discord Devel-
# -oper Portal for use with the Bot Profile that I made to u-
# -se with this particular application.
bot.run(config.token)
