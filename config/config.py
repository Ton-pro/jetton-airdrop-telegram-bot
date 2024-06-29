import logging
from pathlib import Path

import pytz
import betterlogging as bl

from os import environ as env

import requests
from aiogram.client.default import DefaultBotProperties
from cache.user import UserCache
from cache.translation import TranslationCache
from dotenv import load_dotenv
from aiogram import Dispatcher, Bot

from tonsdk.contract.wallet import Wallets, WalletVersionEnum


load_dotenv()

logger = logging.getLogger(__name__)
bl.basic_colorized_config(level=logging.INFO)

INITIAL_BALANCE = float(env['INITIAL_BALANCE'])
INITIAL_REFERRAL_TOKENS = float(env['INITIAL_REFERRAL_TOKENS'])
SECOND_LEVEL_REFERRAL_TOKENS = float(env['SECOND_LEVEL_REFERRAL_TOKENS'])
CHANNELS_LIST = env['CHANNELS_LIST'].split(",")
AIRDROP_START_DATE=env['AIRDROP_START_DATE']
AIRDROP_END_DATE=env['AIRDROP_END_DATE']
AIRDROP_AMOUNT=float(env['AIRDROP_AMOUNT'])
AIRDROP_MAX_COUNT_USERS=int(env['AIRDROP_MAX_COUNT_USERS'])
AIRDROP_JETTON_WALLET=env['AIRDROP_JETTON_WALLET']
AIRDROP_JETTON_MASTER=env['AIRDROP_JETTON_MASTER']
AIRDROP_JETTON_NAME=env['AIRDROP_JETTON_NAME']
BOT_API_TOKEN = env['BOT_API_TOKEN']
BOT_NAME = env['BOT_NAME']
TONCENTER_API = env['TONCENTER_API']
MANIFEST_URL = env['MANIFEST_URL']
MNEMONICS = env['MNEMONICS'].split(" ")
TIMEZONE = pytz.timezone(env['TIMEZONE'])
url = f"https://t.me/{env['LINK']}?start="
LINK = url + "{}"

POSTGRES_URI = f"postgresql://{env['DATABASE_USER']}:{env['DATABASE_PASS']}@{env['DATABASE_HOST']}/{env['DATABASE_NAME']}"

bot = Bot(token=BOT_API_TOKEN,
          default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

keystore_dir = '/tmp/ton_keystore'
Path(keystore_dir).mkdir(parents=True, exist_ok=True)

ton_config = requests.get("https://ton.org/global.config.json").json()

mnemonics, pub_k, priv_k, wallet = Wallets.from_mnemonics(mnemonics=MNEMONICS, version=WalletVersionEnum.v4r2)

translations_cache = TranslationCache()
users_cache = UserCache()

logger.info(wallet.address.to_string(True, True))
