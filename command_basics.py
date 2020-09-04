import discord
from discord.ext import commands
import sqlite3
import dbobj
from util_classes import database
#from help import commands_help

class general(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="ping",help="Ping the bot and return its latency in ms.")
  async def ping(self, ctx):
    await ctx.send('Pong! **{0} ms**'.format(round(self.bot.latency*1000,1)))

  @commands.command(name="prefix",help="Change the command prefix for the bot.")
  async def change_prefix(self, ctx, prefix):
    data = (prefix,ctx.guild.id)
    database.update_data(dbobj.servers,data)
    await ctx.send('Command prefix changed to "**{0}**".'.format(prefix))

  @commands.command(name="search",help="Search for a specific command within this bot's available ones.")
  async def search_for_command(self, ctx, *, query):
    cmd = None
    cmd = self.bot.get_command(query)
    if(cmd is not None):
      await ctx.send("Command found! Qualified name: " + cmd.name)
    else:
      await ctx.send("Command not found.")

  @commands.command(name="cogsearch",help="Search for a specific cog within this bot.")
  async def search_for_cog(self, ctx, *, query):
    cog = self.bot.get_cog(query)
    if(cog is not None):
      await ctx.send("Cog `" + cog.qualified_name + "` found.")
    else:
      await ctx.send("Cog not found.")

  @commands.command(name="help",aliases=['h'],help="Display the command help message.")
  async def help(self, ctx, *, query=None):
    out = []
    out.append("```")
    if(query == None):
      out.append("~~~Command List~~~")
      out.append(list_commands(self, "general", "General: "))
      out.append(list_commands(self, "referrals", "Referrals: "))
      # add your other cogs here
      out.append("```")
      await ctx.send("\n".join(out))
    else:
      cmd = self.bot.get_command(query)
      if(cmd is not None):
        group = False
        namestr = ctx.prefix
        justcmdstring = ""
        if(cmd.parents != []):
          namestr = namestr + cmd.full_parent_name + " "
          justcmdstring = cmd.full_parent_name + " "
        justcmdstring = justcmdstring + cmd.name
        if(cmd.aliases == []):
          namestr = namestr + cmd.name
        else:
          namestr = namestr + "[" + cmd.name
          for alias in cmd.aliases:
            namestr = namestr + "|" + alias
          namestr = namestr + "]"
          #print(cmd.clean_params)
        for val in cmd.clean_params:
          namestr = namestr + " <" + val + ">"
        out.append(namestr)
        out.append(cmd.help)
        if(isinstance(cmd, commands.Group)):
          subcmdstring = "This command has subcommands. Valid subcommands are: "
          for subcmd in cmd.commands:
            subcmdstring = subcmdstring + subcmd.name + ", "
          subcmdstring = subcmdstring[:-2]
          out.append(subcmdstring)
          out.append("```")
          out.append("```")
          out.append("For information on a specific subcommand, use " + ctx.prefix + "help " + justcmdstring + " [subcommand]")
        out.append("```")
        await ctx.send("\n".join(out))
      else:
        out.append("Command not found")
        out.append("```")
        await ctx.send("\n".join(out))

  @commands.Cog.listener()
  async def on_guild_join(self, guild):
    database.insert_row(dbobj.servers,(guild.id,"$"))

def list_commands(self, name, string):
    cog = self.bot.get_cog(name)
    commands = cog.get_commands()
    for x, command in enumerate(commands):
        commands[x] = command.name
    commands = ", ".join(commands)
    return (string+commands)
