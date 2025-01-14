import discord
import tweepy
from discord.ext import tasks
import tweepy.errors
import time
import os
import asyncio

# API and Tokens Infos
discordBotToken = os.getenv("discordBotToken")
twitterBearerToken = os.getenv("twitterBearerToken")

if discordBotToken is None:
    raise ValueError("discordBotToken environment variable is not set.")
if twitterBearerToken is None:
    raise ValueError("twitterBearerToken environment variable is not set.")

twitterUserID = "1787757306815696896"   # Twitter User ID is not userName (it's a number)

# Tweepy Setting
client = tweepy.Client(bearer_token=twitterBearerToken)

# Discord Setting
intents = discord.Intents.default() # 봇의 권한
intents.message_content = True  # Enable message content
bot = discord.Client(intents=intents)   # 봇의 인스턴스 생성

# 가장 최근 트윗 ID
lastTweetID = None


@tasks.loop(seconds=60)
async def checkTwitter():
    global lastTweetID

    try:
        response = client.get_users_tweets(
            id=twitterUserID,
            max_results=5,
            tweet_fields=['id', 'text', 'created_at']
        )
        tweets = response.data

        for tweet in tweets:
            if lastTweetID is None:
                lastTweetID = tweet.id
                print(f"최초 실행: {tweet.text}")
            elif lastTweetID < tweet.id:
                lastTweetID = tweet.id
                print(f"새로운 트윗: {tweet.text}")

    except tweepy.errors.TooManyRequests as e:
        resetTime = int(e.response.headers.get("x-rate-limit-reset"))
        sleepTime = resetTime - int(time.time())
        print(f"Rate limit exceeded. Sleeping for {sleepTime} seconds.")
        await asyncio.sleep(sleepTime)
        checkTwitter.restart()  # Restart the task after sleeping



@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    checkTwitter.start()

@bot.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")  # Debugging statement
    
    if message.content == 'hello':
        print('입력받음 "hello"')
        await message.channel.send('Hello!')

bot.run(discordBotToken)