from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import Database
from utils import load_texts
from keyboards import InlineKeyboard

from config import bot, LINK, logger


async def start(message: Message, state: FSMContext):

    user_id = message.chat.id
    referral_id = message.text.split(' ')
    if len(referral_id) == 2:
        if int(referral_id[1]) != message.chat.id:
            referral_id = int(referral_id[1])
        else:
            referral_id = None
    else:
        referral_id = None

    user = await Database.get_user(user_id)
    if user is None:
        await state.update_data(referral_id=referral_id)
        await message.answer(
        text=f"Это демо бот. Для дальнейшей работы выберите язык.\nThis is a demo bot. For further work, select your language.\nhttps://github.com/Ton-pro/jetton-airdrop-telegram-bot", reply_markup=await InlineKeyboard.select_lang(),
        disable_web_page_preview=True)
        return

    texts = await load_texts(user.lang)
    await state.update_data(lang=user.lang)

    # Проверка подписки
    all_channels_sb = True
    channels = await Database.get_channels()
    for channel in channels:
        user_info = await bot.get_chat_member(chat_id=f"@{channel.username}", user_id=message.chat.id)
        if user_info.status == 'left':
            all_channels_sb = False
        channel.status = user_info.status
    if not all_channels_sb:
        await message.edit_text(text=texts['not_subscribed'],
                             reply_markup=await InlineKeyboard(texts).subscribe_kb(channels))
        await state.update_data(referral_id=referral_id)
        return

    await message.answer(
        text=texts['menu_description'].format(link=LINK.format(message.chat.id), wallet=user.wallet,
                                              tokens=user.balance, level_1=user.level_1, level_2=user.level_2),
        reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None, LINK.format(message.chat.id)),
        disable_web_page_preview=True)


async def start_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not 'lang' in data:
        user = await Database.get_user(callback.message.chat.id)
        if user is None:
            await callback.message.edit_text(
            text="Это демо бот https://github.com/Ton-pro/jetton-airdrop-telegram-bot. Для дальнейшей работы выбереи язык", reply_markup=await InlineKeyboard.select_lang(),
            disable_web_page_preview=True)
            return
        lang=user.lang
    else:
        lang=data['lang']
    texts = await load_texts(lang)

    all_channels_sb = True
    channels = await Database.get_channels()
    for channel in channels:
        user_info = await bot.get_chat_member(chat_id=f"@{channel.username}", user_id=callback.message.chat.id)
        if user_info.status == 'left':
            all_channels_sb = False
        channel.status = user_info.status
    if not all_channels_sb:
        await callback.answer(text=texts['not_subscribed'], show_alert=True)
        return
    if 'referral_id' in data:
        await Database.insert_user(callback.message.chat.id, data['referral_id'], lang)

    user = await Database.get_user(callback.message.chat.id)

    try:
        await callback.message.edit_text(
            text=texts['menu_description'].format(link=LINK.format(callback.message.chat.id),
                                                  wallet=user.wallet, tokens=user.balance, level_1=user.level_1,
                                                  level_2=user.level_2),
            reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None, LINK.format(callback.message.chat.id)),
            disable_web_page_preview=True)
    except Exception as e:
        logger.error(e)


async def star_lang_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'lang_ru':
        lang = 'ru'
    if callback.data == 'lang_en':
        lang = 'en'
    await state.update_data(lang=lang)
    texts = await load_texts(lang)

    all_channels_sb = True
    channels = await Database.get_channels()
    for channel in channels:
        user_info = await bot.get_chat_member(chat_id=f"@{channel.username}", user_id=callback.message.chat.id)
        if user_info.status == 'left':
            all_channels_sb = False
        channel.status = user_info.status
    if not all_channels_sb:
        await callback.message.edit_text(text=texts['not_subscribed'],
                             reply_markup=await InlineKeyboard(texts).subscribe_kb(channels))
        return

    data = await state.get_data()
    if 'referral_id' in data:
        await Database.insert_user(callback.message.chat.id, data['referral_id'], data['lang'])

    user = await Database.get_user(callback.message.chat.id)

    try:
        await callback.message.edit_text(
            text=texts['menu_description'].format(link=LINK.format(callback.message.chat.id),
                                                  wallet=user.wallet, tokens=user.balance, level_1=user.level_1,
                                                  level_2=user.level_2),
            reply_markup=await InlineKeyboard(texts).start_kb(user.wallet is not None, LINK.format(callback.message.chat.id)),
            disable_web_page_preview=True)
    except:
        pass

