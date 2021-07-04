import discord
from discord.ext import commands, menus
from referral_cog import Confirm
import dbobj,os
from util_classes import database
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.context import ComponentContext

class debug(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.is_owner()
  @commands.command(name="clear-referral",aliases=['cr'],help="Usable only by bot owner for debug purposes.")
  async def clear_referral_cmd(self,ctx,user:discord.User=None):
    if(user == None):
      await ctx.send("You must tag a user!")
      return
    existing_user = database.select_one(dbobj.user_link, source=user.id)
    if(existing_user != None and existing_user != []):
      existing_user = existing_user[1]
      user_obj = self.bot.get_user(existing_user)
      confirm = await Confirm("Are you sure you want to clear the record for **" + user.name + "#" + user.discriminator + "** who declared themselves as referred by **" + user_obj.name + "#" + user_obj.discriminator + "**?  (this will lower the referrer's score)").prompt(ctx)
      if confirm:
        statement = "DELETE FROM user_link WHERE source = %s"
        data = (user.id,)
        decreasing_score = database.select_one(dbobj.scores, user_id=user_obj.id)[1]
        data_2 = (decreasing_score-1,user_obj.id)
        #database.delete_data(statement,data)
        database.test_delete(dbobj.user_link,source=user.id)
        database.update_data(dbobj.scores,data_2)
      else:
        await ctx.send("Process canceled.")
        return
    else:
      await ctx.send("That user has not declared anyone as their referrer yet!")

  @commands.is_owner()
  @commands.command(name="repair-database",help="Create database tables (other than servers, since if that table doesn't exist, nothing will work) if they do not already exist. Add new lines to the code if you add new tables.")
  async def db_repair(self,ctx):
    database.repair_table(dbobj.webhook_profile)
    database.repair_table(dbobj.scores)
    database.repair_table(dbobj.user_link)

  @commands.command(name="button-test",help="Show a message with a button on it. That's it.")
  async def test_button(self,ctx):
    buttons = [create_button(style=ButtonStyle.secondary, label="Grey Button", custom_id="grey"), create_button(style=ButtonStyle.green, label="Green Button", custom_id="green")]
    action_row = create_actionrow(*buttons)
    await ctx.send("Wow, this message really does have some buttons!",components=[action_row])

  @commands.Cog.listener()
  async def on_component(ctx: ComponentContext):
    # you may want to filter or change behaviour based on custom_id or message
    author = ctx.author
    id = ctx.custom_id
    if id == "grey":
      await ctx.edit_origin(content="{0.mention} pressed a grey button.".format(author))
    elif id == "green":
      await ctx.edit_origin(content="{0.mention} pressed a green button.".format(author))
    else:
      await ctx.edit_origin(content="{0.mention} pressed a button".format(author))
