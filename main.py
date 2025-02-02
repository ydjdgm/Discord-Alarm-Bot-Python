import os
import tweepy
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv("tokens.env")
# Discord Bot Token
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
# Twitter API Keys
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')


# Twitter API Client
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)


# manage bot intents
intents = discord.Intents.default()
intents.message_content = True


# define bot class
class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()  # commands are now synced(동기화)
        print("Commands are now synced.\n명령어가 동기화되었습니다.")

    async def on_ready(self):
        print(f"Logged in as {self.user}.\n{self.user}로 로그인했습니다.")
bot = MyBot()   # create bot instance


# handle Too Many Requests error
async def handle_too_many_requests_error(interaction: discord.Interaction, response):
    try:
        print("Handling Too Many Requests error")
        headers = response.headers
        reset_time = int(headers["x-rate-limit-reset"])
        remaining_time = reset_time - time.time()
        print(f"Reset time: {reset_time}, Remaining time: {remaining_time}")
        if remaining_time > 0:
            minutes, seconds = divmod(remaining_time, 60)
            return f"API 제한 해제까지 남은 시간: {int(minutes)}분 {int(seconds)}초."
        else:
            return "API 제한이 해제되었습니다."
    except Exception as e:
        print(f"Error handling Too Many Requests: {e}")
        return
    

####################################################################################################
###########################################COMMANDS#################################################

# /hello, to check commands work
@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.name}!")


# /getuserid, to get User's ID (int ID)
@bot.tree.command(name="getuserid", description="Get User's ID")
async def get_user_id(interaction: discord.Interaction, username: str):
    try:
        user_info = client.get_users(usernames=username).data
        await interaction.response.send_message(f"username = {user_info.username}\nname = {user_info.name}\nid = {user_info.id}")
    except tweepy.TooManyRequests as e:
        print (f"Error: {e}")
        await interaction.response.send_message(await handle_too_many_requests_error(interaction, e.response))
    except Exception as e:
        print (f"Error: {e}")
        await interaction.response.send_message(f"Unexpected error: {e}")


# /gettweeturl, to get Tweet's URL
@bot.tree.command(name="gettweeturl", description="Get Tweet's URL")
async def get_tweet_url(interaction: discord.Interaction, username: str):
    try:
        userinfo = client.get_users(usernames=username).data
        tweets = client.get_users_tweets(id=userinfo.id).data
        await interaction.response.send_message(f"https://x.com/{username}/status/{tweets[0].id}")
    except tweepy.TooManyRequests as e:
        print (f"Error: {e}")
        await interaction.response.send_message(await handle_too_many_requests_error(interaction, e.response))
    except Exception as e:
        print (f"Error: {e}")
        await interaction.response.send_message(f"Unexpected error: {e}")

###########################################COMMANDS#################################################
####################################################################################################

if DISCORD_BOT_TOKEN:
    bot.run(DISCORD_BOT_TOKEN)
else:
    print("ERROR: 환경 변수 DISCORD_BOT_TOKEN이 설정되지 않았습니다.")