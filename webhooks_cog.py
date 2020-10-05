import discord
from discord.ext import commands, menus
from referral_cog import Confirm
import dbobj,os
from util_classes import database

def can_use_webhooks():
  def predicate(ctx):
    user_str = os.environ['WEBHOOKS_USERS']
    user_arr = user_str.split(",")
    return str(ctx.author.id) in user_arr
  return commands.check(predicate)

class webhooks(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @can_use_webhooks()
  @commands.command(name="webhook-say",aliases=['ws','message'],help="Send a webhook message in this channel if such a webhook exists.")
  async def webhook_test_cmd(self,ctx,*,msg):
    wh = await ctx.channel.webhooks()
    if wh == []:
      await ctx.send("No webhooks in this channel!")
    else:
      profile = database.select_one(database.webhook_profile,user_id=ctx.author.id)
      if profile == [] or profile == None:
        await ctx.message.delete()
        await wh[0].send(msg)
      else:
        await ctx.message.delete()
        if str(profile[2]) == "None":
          wh[0].send(msg,username=str(profile[1]))
        else:
          wh[0].send(msg,username=str(profile[1]),avatar_url=str(profile[2]))

  @can_use_webhooks()
  @commands.command(name="webhook-profile",aliases=['wp'],help="Add or update your webhook profile, usable on any webhook accessible by this bot.")
  async def webhook_profile(self,ctx,username,avatar_url=None):
    existing = database.select_one(database.webhook_profile,user_id=ctx.author.id)
    url_string = "None"
    if avatar_url != None:
      url_string = avatar_url
    if existing == []:
      database.insert_row(database.webhook_profile,(ctx.author.id,username,url_string))
    else:
      database.update_data(database.webhook_profile,(username,url_string,ctx.author.id))
