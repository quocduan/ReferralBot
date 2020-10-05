import discord
from discord.ext import commands, menus
import sqlite3
import dbobj
from util_classes import database

# This is the module with all of the main functionality of the bot inside it. It
# mostly just consists of the main referrals class, which extends the base Cog
# class, and then its internal members, the methods that will be developed into
# commands. It needs to be loaded both into the help command and into the main
# base bot script so that it will actually load the functionality properly. If
# I have completed the project, I have most likely added those lines to those
# scripts already. If I haven't, sorry about that. My bad. It also includes a
# class that creates a new sort of menu that'll work all nice for confirmations,
# which I want to use to have people confirm a change to their referral.

class Confirm(menus.Menu):
    def __init__(self, msg):
        super().__init__(timeout=30.0, delete_message_after=True)
        self.msg = msg
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await channel.send(self.msg)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def do_confirm(self, payload):
        self.result = True
        self.stop()

    @menus.button('\N{CROSS MARK}')
    async def do_deny(self, payload):
        self.result = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.result

class referrals(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.cooldown(1,10,commands.BucketType.guild)
  @commands.command(name="referred-by",aliases=['rb','recruited-by'],help="Inform the bot that you were referred to the server by a specific user.")
  async def referred_by(self,ctx,user:discord.User=None):
    # Error conditions
    if(user == None):
      await ctx.send("You must tag a user!")
      return
    elif(user == ctx.author):
      await ctx.send("You cannot refer yourself.")
      return
    existing_user = database.select_one(dbobj.user_link, source=ctx.author.id)
    if(existing_user != None and existing_user != []):
      existing_user = existing_user[1]
      user_obj = self.bot.get_user(existing_user)
      if(user == user_obj):
        await ctx.send("You are already registered as referred by that user!")
        return
      confirm = await Confirm("Are you sure you want to change your referring user from **" + user_obj.name + "#" + user_obj.discriminator + "** to **" + user.name + "#" + user.discriminator + "**?").prompt(ctx)
      if confirm:
        data = (user.id,ctx.author.id)
        database.update_data(dbobj.user_link,data)
        decreasing_score = database.select_one(dbobj.scores, user_id=user_obj.id)[1]
        data_2 = (decreasing_score-1,user_obj.id)
        database.update_data(dbobj.scores,data_2)
      else:
        await ctx.send("Process canceled.")
        return
    else:
      confirm = await Confirm("Are you sure you want to set your referring user to **" + user.name + "#" + user.discriminator + "**?").prompt(ctx)
      if confirm:
        data = (ctx.author.id,user.id)
        database.insert_row(dbobj.user_link,data)
      else:
        await ctx.send("Process canceled.")
        return
    increasing_score = database.select_one(dbobj.scores, user_id=user.id)
    if(increasing_score != None and increasing_score != []):
      increasing_score = increasing_score[1]
      data = (increasing_score+1,user.id)
      database.update_data(dbobj.scores,data)
    else:
      data = (user.id,1)
      database.insert_row(dbobj.scores,data)
    await ctx.send("Process complete!")
    #await ctx.send("This command is not yet fully implemented. Sorry.")

  @commands.command(name="score",aliases=['sc','referrals'],help="Check the referral score of yourself or another user.")
  async def score_check(self,ctx,user:discord.User=None):
    # error correction
    target = None
    if(user == None):
      target = ctx.author
    else:
      target = user
    record = database.select_one(dbobj.scores, user_id=target.id)
    score = 0 if record == None or record == [] else record[1]
    await ctx.send("Requested score: **" + str(score) + "**.")

  @commands.command(name="leaderboard",help="Display the top 10 users, sorted in descending order by number of referrals credited to them.")
  async def leaderboard(self,ctx,page=1):
    sorted_records = database.select_many(dbobj.scores, select_all=True, ORDER_BY="score", ORDER_DESC=True)
    start_number = (page-1)*10
    if len(sorted_records) <= start_number:
      await ctx.send("Not enough recorded users to make a leaderboard there!")
      return
    text = []
    for x in range(10):
      try:
        user_record = sorted_records[start_number + x]
        user_obj = self.bot.get_user(user_record[0])
        text.append(str(start_number + x + 1) + ". " + user_obj.mention + ": " + str(user_record[1]))
      except IndexError:
        break
    text_unlisted = "\n".join(text)
    embed=discord.Embed(title="Referrals Leaderboard", color=0x3845e9)
    embed.add_field(name="Top Users", value=text_unlisted, inline=False)
    embed.set_footer(text="Requested by " + ctx.author.name)
    await ctx.send(embed=embed)
    #await ctx.send("Sorry, this command has not yet been implemented. Please contact the developer if it's not done soon.")
