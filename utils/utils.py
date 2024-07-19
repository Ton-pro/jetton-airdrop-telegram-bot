from base64 import urlsafe_b64encode

from keyboards.inline import InlineKeyboard
from pytoniq_core import begin_cell
from TonTools import Wallet, TonCenterClient
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

from database.schemas.user import User
from config import logger, bot, LINK
from config.config import mnemonics, TONCENTER_API

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

def get_referral_id(message: Message, self_id: int) -> int:
    referral_id = message.text.split(' ')
    if len(referral_id) == 2:
        if int(referral_id[1]) != self_id:
            referral_id = int(referral_id[1])
        else:
            referral_id = None
    else:
        referral_id = None
    return referral_id

async def  check_channels(channels, user_id: int, texts: dict, message: Message) -> bool:
    all_channels_sb = True
    for channel in channels:
        user_info = await bot.get_chat_member(chat_id=f"@{channel.username}", user_id=user_id)
        if user_info.status == 'left':
            all_channels_sb = False
        channel.status = user_info.status
    if not all_channels_sb:
        try:
            await message.edit_text(text=texts['not_subscribed'],
                                reply_markup=await InlineKeyboard(texts).subscribe_kb(channels))
        except TelegramAPIError as e:
            if "message can't be edited" in str(e):
                await message.answer(text=texts['not_subscribed'],
                                reply_markup=await InlineKeyboard(texts).subscribe_kb(channels))
            else:
                logger.error(e)
        except Exception as e:
            logger.error(e)
        return False
    return True

async def main_menu(user, texts: dict, message: Message):
    try:
        await message.edit_text(
            text=texts['menu_description'].format(link=LINK.format(user.user_id),
                                                wallet=user.wallet, tokens=user.balance, level_1=user.level_1,
                                                level_2=user.level_2),
            reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None, LINK.format(user.user_id)),
            disable_web_page_preview=True)
    except TelegramAPIError as e:
        if "message can't be edited" in str(e):
            await message.reply(
                text=texts['menu_description'].format(link=LINK.format(user.user_id),
                                                    wallet=user.wallet, tokens=user.balance, level_1=user.level_1,
                                                    level_2=user.level_2),
                reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None, LINK.format(user.user_id)),
                disable_web_page_preview=True)
        else:
            logger.error(e)
    except Exception as e:
        logger.error(e)
