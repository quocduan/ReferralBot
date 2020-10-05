import discord
from discord.ext import commands, menus
from referral_cog import Confirm
import dbobj,os
from util_classes import database

def can_use_webhooks():
  def predicate(ctx):
    user_str = os.environ['WEBHOOKS_USERS']
    user_arr = user_str.split(",")
    return str(ctx.user.id) in user_arr
  return commands.check(predicate)

class webhooks(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.is_owner()
  @commands.command(name="webhook-say",aliases=['ws','message'],help="Send a webhook message in this channel if such a webhook exists.")
  async def webhook_test_cmd(self,ctx,*,msg):
    wh = await ctx.channel.webhooks()
    if wh == []:
      await ctx.send("No webhooks in this channel!")
    else:
      await ctx.message.delete()
      await wh[0].send(msg)
