# Discord Referral Bot

Welcome! This repository is for, as you have hopefully already guessed, a referral bot for Discord. Hosted individually on Heroku (though it can be locally installed), this code just connects to Discord through a bot profile you create using the Discord Developer Portal, and then waits for you to use it. It's really nothing special.

## Setup

Unfortunately, this bot isn't all ready to go from step one. There's more to it, although thankfully not much. This section details in steps how to set up your own instance of this single-server bot.

### 1: Bot Profile

First things first, create a Discord bot profile through the Discord Developer portal [here.](https://discord.com/developers/) Find the bot token and copy it into a text file so it can easily be found later. At this time, designate two channels of your choice in a Discord server you own (or have moderator privileges on) as logging channels. Logging doesn't strictly work with the latest version of the bot, but it'll break if you don't give it channels it can access so just bear with me. Copy the channel ids of these channels into the same text file.

### 2: Heroku App

Next you need to add this bot to your Heroku account by pressing this button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/geekkid1/ReferralBot)

First it will probably ask you for an app name, which you can set to anything you want really, and then after that some config variables. This is where the token and channel ids come in. Paste them into their respective config variable boxes. Then continue. This will, if it works correctly, auto-deploy the app to your Heroku account. If you don't have one, this will prompt you to create one or log in to one.
