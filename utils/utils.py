import json
from base64 import urlsafe_b64encode

from pytoniq_core import begin_cell
from TonTools import Wallet, TonCenterClient
from config.config import mnemonics, TONCENTER_API
from database.schemas.user import User
from config import logger, bot, AIRDROP_JETTON_MASTER


async def load_texts(language: str = 'ru'):
    with open('texts.json', 'r', encoding='utf-8') as f:
        texts = json.load(f)
    return texts.get(language, texts['en'])


async def transaction(user: User, amount: float, jetton_address: str = None):
    client = TonCenterClient(base_url='https://toncenter.com/api/v2/',
                             key=TONCENTER_API)
    wal = Wallet(mnemonics=mnemonics, provider=client)
    if jetton_address:
        await wal.transfer_jetton_by_jetton_wallet(destination_address=user.wallet,
                                                   jetton_wallet=jetton_address,
                                                   jettons_amount=amount)
    else:
        await wal.transfer_ton(destination_address=user.wallet,
                               amount=amount)

async def get_comment_message(destination_address: str, amount: int, comment: str) -> dict:
    data = {
        'address': destination_address,
        'amount': str(amount),
        'payload': urlsafe_b64encode(
            begin_cell()
            .store_uint(0, 32)
            .store_string(comment)
            .end_cell()
            .to_boc()
        )
        .decode()
    }

    return data

async def get_chat_info(channel_username):
    try:
        chat = await bot.get_chat("@" + channel_username)
        return chat
    except Exception as e:
        logger.error(f"An error occurred: {e}")
