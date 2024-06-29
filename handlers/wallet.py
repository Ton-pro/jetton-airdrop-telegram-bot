import asyncio
from io import BytesIO

import qrcode
from aiogram.types import CallbackQuery, BufferedInputFile
from pytonconnect.storage import IStorage
from pytonconnect import TonConnect
from pytoniq_core import Address
from aiogram.fsm.context import FSMContext

from config import MANIFEST_URL, LINK, translations_cache
from database import Database
from keyboards import InlineKeyboard

storage = {}


class TcStorage(IStorage):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def _get_key(self, key: str):
        return str(self.chat_id) + key

    async def set_item(self, key: str, value: str):
        storage[self._get_key(key)] = value

    async def get_item(self, key: str, default_value: str = None):
        return storage.get(self._get_key(key), default_value)

    async def remove_item(self, key: str):
        storage.pop(self._get_key(key))


async def get_connector(chat_id: int):
    return TonConnect(MANIFEST_URL, storage=TcStorage(chat_id))


async def connect_wallet(callback: CallbackQuery, state: FSMContext, cached_user):
    texts = translations_cache.cache[cached_user.lang]

    try:
        await callback.message.edit_text(text=texts['connect'], reply_markup=await InlineKeyboard(texts).list_wallets())
    except:
        await callback.message.delete()
        await callback.message.answer(text=texts['connect'], reply_markup=await InlineKeyboard(texts).list_wallets())


async def connected_wallet(callback: CallbackQuery, state: FSMContext, cached_user):
    texts = translations_cache.cache[cached_user.lang]

    wallet_name = callback.data.split(':')[1]
    connector = await get_connector(callback.message.chat.id)

    wallets_list = connector.get_wallets()
    wal = None

    for w in wallets_list:
        if w['name'] == wallet_name:
            wal = w

    if wal is None:
        await callback.message.edit_text(text=texts['not_found_wallet'])
        return

    generated_url = await connector.connect(wal)
    img = qrcode.make(generated_url)
    stream = BytesIO()
    img.save(stream)
    file = BufferedInputFile(file=stream.getvalue(), filename='qrcode')

    await callback.message.delete()
    msg = await callback.message.answer_photo(photo=file,
                                              reply_markup=await InlineKeyboard(texts).connect_kb(generated_url),
                                              caption=texts['time_connect'].format(wal_name=wallet_name))
    for i in range(1, 5 * 60):
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                wallet_address = connector.account.address
                wallet_address = Address(wallet_address).to_str(is_bounceable=False)
                await Database.update_wallet(callback.message.chat.id, wallet_address, 1, wallet_name)

                await msg.delete()
                await callback.message.answer(text=texts['wallet_connected'].format(wallet=wallet_address))
                user = await Database.get_user(callback.message.chat.id)
                await callback.message.answer(
                    text=texts['menu_description'].format(link=LINK.format(callback.message.chat.id),
                                                          wallet=user.wallet,
                                                          tokens=user.balance, level_1=user.level_1,
                                                          level_2=user.level_2),
                    reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None,
                                                               LINK.format(callback.message.chat.id)),
                    disable_web_page_preview=True)
            return
    await msg.delete()
    await callback.message.answer(text=texts['timeout_error'], reply_markup=await InlineKeyboard(texts).list_wallets())


async def disconnect_wallet(callback: CallbackQuery, state: FSMContext, cached_user):
    texts = translations_cache.cache[cached_user.lang]

    try:
        connector = await get_connector(callback.message.chat.id)
        await connector.restore_connection()
        await connector.disconnect()
    except:
        pass

    await Database.update_wallet(callback.message.chat.id, None, 0, None)
    user = await Database.get_user(callback.message.chat.id)
    await callback.message.edit_text(text=texts['wallet_disconnected'])
    await callback.message.answer(text=texts['menu_description'].format(link=LINK.format(callback.message.chat.id),
                                                                        wallet=user.wallet,
                                                                        tokens=user.balance, level_1=user.level_1,
                                                                        level_2=user.level_2),
                                  reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None,
                                                                             LINK.format(callback.message.chat.id)),
                                  disable_web_page_preview=True)
