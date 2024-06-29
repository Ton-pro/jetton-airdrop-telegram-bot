import asyncio
import time

from aiogram.fsm.context import FSMContext
from pytonconnect.exceptions import UserRejectsError
from aiogram.types import CallbackQuery, Message
from tonsdk.utils import to_nano

from database import Database
from datetime import datetime
from config import TIMEZONE, logger, wallet, LINK, BOT_NAME, translations_cache
from database.schemas.airdrop import Airdrop
from database.schemas.user import User
from handlers.wallet import get_connector
from keyboards import InlineKeyboard
from utils import transaction, get_comment_message


async def payment(callback: CallbackQuery, texts: dict, user: User, airdrop: Airdrop, state: FSMContext):
    connector = await get_connector(callback.message.chat.id)
    connected = await connector.restore_connection()
    if not connected:
        raise ImportWarning

    transfer_fee = 0.07 if airdrop.jetton_wallet else user.balance * 0.005
    cur_transaction = {
        'valid_until': int(time.time() + 15 * 60),
        'messages': [await get_comment_message(destination_address=wallet.address.to_string(),
                                               amount=to_nano(transfer_fee, 'ton'),
                                               comment=BOT_NAME)]
    }

    name = airdrop.jetton_name if airdrop.jetton_name else "TON"
    call = await callback.message.edit_text(text=texts['wait_payment'].format(fee=transfer_fee,
                                                                              amount=user.balance,
                                                                              name=name),
                                            reply_markup=await InlineKeyboard(texts).payment(user.wallet_provider))
    await state.update_data(cl=call)

    await asyncio.wait_for(connector.send_transaction(transaction=cur_transaction), 15 * 60)


async def check_participation(message: Message, user: User, airdrop: Airdrop, texts: dict):
    claimed_users = airdrop.users_got
    if claimed_users is None:
        claimed_users = []

    if not (user.user_id in claimed_users) and len(claimed_users) < airdrop.max_count_users:
        await transaction(user, user.balance, airdrop.jetton_wallet)
        claimed_users.append(user.user_id)
        await Database.update_users_airdrop(airdrop.id, claimed_users)
        await Database.update_balance(user.user_id, 0)

        name = airdrop.jetton_name if airdrop.jetton_name else "TON"
        await message.edit_text(
            text=texts["successful_airdrop"].format(amount=user.balance, name=name))
    elif user.user_id in claimed_users:
        await message.edit_text(text=texts["completed_airdrop"])
    elif len(claimed_users) >= airdrop.max_count_users:
        await message.edit_text(text=texts["failed_airdrop"])
    else:
        await message.edit_text(text=texts["no_server"])

    user = await Database.get_user(user.user_id)

    await message.answer(text=texts['menu_description'].format(link=LINK.format(message.chat.id), wallet=user.wallet,
                                                               tokens=user.balance, level_1=user.level_1,
                                                               level_2=user.level_2),
                         reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None,
                                                                    LINK.format(message.chat.id)),
                         disable_web_page_preview=True)


async def pay_fee(callback: CallbackQuery, texts: dict, user: User, airdrop: Airdrop, state: FSMContext) -> bool:
    try:
        await payment(callback=callback, texts=texts, user=user, airdrop=airdrop, state=state)
        return True
    except asyncio.TimeoutError:
        data = await state.get_data()
        await data["cl"].edit_text(text=texts['timeout_airdrop'])
    except UserRejectsError:
        data = await state.get_data()
        await data["cl"].edit_text(text=texts['user_rejects'])
    except ImportWarning:
        await callback.answer(text=texts['wallet_not_verified'], show_alert=True)
        return False

    await data["cl"].answer(
        text=texts['menu_description'].format(link=LINK.format(callback.message.chat.id),
                                              wallet=user.wallet,
                                              tokens=user.balance, level_1=user.level_1,
                                              level_2=user.level_2),
        reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None,
                                                   LINK.format(callback.message.chat.id)),
        disable_web_page_preview=True)
    return False


async def claim_airdrop(callback: CallbackQuery, state: FSMContext):
    user = await Database.get_user(callback.message.chat.id)
    texts = translations_cache.cache[user.lang]

    if user.balance == 0:
        await callback.answer(text=texts['zero_balance'], show_alert=True)
        return

    airdrops = await Database.get_airdrops()
    now = datetime.now(tz=TIMEZONE).timestamp()
    for airdrop in airdrops:
        try:
            if airdrop.end_date:
                if datetime.strptime(airdrop.start_date, "%H:%M %d.%m.%Y").timestamp() <= now <= datetime.strptime(
                        airdrop.end_date, "%H:%M %d.%m.%Y").timestamp():
                    is_paid_fee = await pay_fee(callback=callback, texts=texts, user=user, airdrop=airdrop, state=state)
                    if is_paid_fee:
                        data = await state.get_data()
                        await check_participation(data['cl'], user, airdrop, texts)
                    return
            elif datetime.strptime(airdrop.start_date, "%H:%M %d.%m.%Y").timestamp() == now:
                is_paid_fee = await pay_fee(callback=callback, texts=texts, user=user, airdrop=airdrop, state=state)
                if is_paid_fee:
                    data = await state.get_data()
                    await check_participation(data['cl'], user, airdrop, texts)
                return
        except Exception as e:
            logger.error(e)
            msg = (await state.get_data()).get("cl", callback)
            if isinstance(msg, CallbackQuery):
                await msg.answer(text=texts['no_server'], show_alert=True)
                return
            await msg.answer(text=texts['no_server'])
            return

    await callback.answer(text=texts['no_airdrop'], show_alert=True)
