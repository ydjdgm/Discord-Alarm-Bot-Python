import os
import discord
import tweepy
from discord.ext import commands
from dotenv import load_dotenv
import time

# 환경 변수에서 디스코드 봇 토큰 불러오기
load_dotenv("tokens.env")  # .env 파일 로드
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# 트위터 API 클라이언트 생성
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
# 최근 트윗 ID 저장 변수
last_tweet_id = None
# API 사용 제한 종료 시간 (too many requests 에러 발생시 사용)
cooldown_end_time = None


# 봇 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True

# 봇 객체 생성
class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()  # 슬래시 명령어를 디스코드 서버와 동기화
        print("명령어가 동기화 되었습니다.")

    async def on_ready(self):
        print(f"봇이 로그인되었습니다: {self.user}")


# Too Many Requests 에러 발생시
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
        await interaction.response.send_message("뭔가가 잘못됐습니다. 하지만 이런 젠장! 뭐가 잘못된걸까요?")
        return

# 봇 인스턴스 생성
bot = MyBot()



################### 명령어 ###################

# /hello, 명령어 작동 확인용
@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.name}!")


# /tweet, 최근 트윗 가져오기
@bot.tree.command(name="tweet", description="트위터에서 최신 트윗을 가져옵니다.")
async def tweet(interaction: discord.Interaction, userid: str):
    global last_tweet_id
    # 최근 트윗 가져오기
    try:
        response = client.get_users_tweets(
            id=userid,
            max_results=5,
            tweet_fields=["text"],
            expansions=["author_id"]
        )
        tweets = response.data

        if not tweets:
            await interaction.response.send_message("새로운 트윗이 없습니다.")
            return

        for tweet in tweets:
            if last_tweet_id is None or last_tweet_id < tweet.id:
                last_tweet_id = tweet.id
                tweet_url = f"https://twitter.com/{tweet.author_id}/status/{tweet.id}"  #이 부분 되는지 체크
                await interaction.response.send_message(f"최근 트윗: {tweet.id}")
                break
        else:
            await interaction.response.send_message("새로운 트윗이 없습니다.")
    except tweepy.TooManyRequests as e:
        print(f"Error fetching tweets: {e}")
        await interaction.response.send_message(await handle_too_many_requests_error(interaction, e.response))
        return
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        await interaction.response.send_message("최근 트윗 업데이트에 실패했습니다.")
        return



# /get_id, 유저의 ID 가져오기 (숫자로만 이루어진 ID)
@bot.tree.command(name="get_id", description="유저의 ID를 가져옵니다.")
async def get_user_id(interaction: discord.Interaction, username: str):
    try:
        user_info = client.get_user(username = username)
        if user_info:
            try:
                await interaction.response.send_message(user_info)
            except Exception as e:
                print(f"Error fetching tweets: {e}")
                await interaction.response.send_message("ID를 가져올 수 없습니다.")
        else:
            await interaction.response.send_message("유저를 찾을 수 없습니다.")
    except tweepy.TooManyRequests as e:
        print(f"Error fetching tweets: {e}")
        await interaction.response.send_message(await handle_too_many_requests_error(interaction, client))
        return
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        await interaction.response.send_message("ID를 가져올 수 없습니다.")
        return

##############################################


# 봇 실행
if DISCORD_BOT_TOKEN:
    bot.run(DISCORD_BOT_TOKEN)
else:
    print("ERROR: 환경 변수 DISCORD_BOT_TOKEN이 설정되지 않았습니다.")
