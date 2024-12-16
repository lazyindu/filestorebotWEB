
import aiohttp
import pytz #add this
from datetime import date #add this
import random 
import string
from config import *
# ./done_lazy_baby 
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from database.database import add_user, del_user, full_userbase, present_user

VERIFIED = {} 
TOKENS = {} # also add this in verification steps

async def extract_verified_short_link(link):
    API = LAZY_SHORTNER_API # ||---->> if LAZY_SHORTNER_API else URL_SHORTNER_WEBSITE_API
    URL = LAZY_SHORTNER_URL # ||---->> if LAZY_SHORTNER_URL else URL_SHORTENR_WEBSITE
    https = link.split(":")[0]
    if "http" == https:
        https = "https"
        link = link.replace("http", https)

    if URL == "api.shareus.in":
        url = f"https://{URL}/shortLink"
        params = {"token": API,
                  "format": "json",
                  "link": link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json(content_type="text/html")
                    if data["status"] == "success":
                        return data["shortlink"]
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/shortLink?token={API}&format=json&link={link}'

        except Exception as e:
            logger.error(e)
            return f'https://{URL}/shortLink?token={API}&format=json&link={link}'
    else:
        url = f'https://{URL}/api'
        params = {'api': API,
                  'url': link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json()
                    if data["status"] == "success":
                        return data['shortenedUrl']
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/api?api={API}&link={link}'

        except Exception as e:
            logger.error(e)
            print(e)
            return f'{URL}/api?api={API}&link={link}'

async def check_token(bot, userid, token):
    user = await bot.get_users(userid)
    
    if not await present_user(user.id):
        try:
            await add_user(user.id)
        except Exception as e:
            print(f"Error adding user: {e}")
            pass

    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            is_used = TKN[token]
            if is_used == True:
                return False
            else:
                return True
    else:
        return False

async def get_token(bot, userid, link):
    user = await bot.get_users(userid)
    if not await present_user(user.id):
        try:
            await add_user(user.id)
        except Exception as e:
            print(f"Error adding user: {e}")
            pass
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    link = f"{link}verify-{user.id}-{token}"
    print(link)
    final_verified_lazy_link = await extract_verified_short_link(link)
    return str(final_verified_lazy_link)

async def verify_user(bot, userid, token):
    user = await bot.get_users(userid)
    if not await present_user(user.id):
        try:
            await add_user(user.id)
        except Exception as e:
            print(f"Error adding user: {e}")
            pass
    TOKENS[user.id] = {token: True}
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    VERIFIED[user.id] = str(today)

async def check_verification(bot, userid):
    user = await bot.get_users(userid)
    if not await present_user(user.id):
        try:
            await add_user(user.id)
        except Exception as e:
            print(f"Error adding user: {e}")
            pass
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    if user.id in VERIFIED.keys():
        EXP = VERIFIED[user.id]
        years, month, day = EXP.split('-')
        comp = date(int(years), int(month), int(day))
        if comp<today:
            return False
        else:
            return True
    else:
        return False
 