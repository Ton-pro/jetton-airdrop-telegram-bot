from aiogram.types import Message, CallbackQuery

from database import Database
from utils import check_channels, main_menu
from keyboards import InlineKeyboard

from config import translations_cache, users_cache, INITIAL_REFERRAL_TOKENS


async def start(message: Message, cached_user):
    texts = translations_cache.cache[cached_user.lang]
    await main_menu(cached_user, texts, message)

async def start_callback(callback: CallbackQuery, cached_user):
    texts = translations_cache.cache[cached_user.lang]
    await main_menu(cached_user, texts, callback.message)

async def start_lang_callback(callback: CallbackQuery, cached_user):
    user_id = cached_user.user_id
    if callback.data == 'lang_ru':
        lang = 'ru'
    if callback.data == 'lang_en':
        lang = 'en'

    texts = translations_cache.cache[lang]

    await Database.update_lang(user_id, lang)

    if not cached_user.isSubscribe:
        channels = await Database.get_channels()
        status = await check_channels(channels, cached_user.user_id, texts, callback.message)
        if status:
            if not cached_user.isSubscribe:
                await Database.update_subscription_status(cached_user.user_id)
            if cached_user.referral_id:
                await Database.update_referrals(cached_user.referral_id, 1, INITIAL_REFERRAL_TOKENS)
        else:
            user = await Database.get_user(user_id)
            users_cache.update_user(user)
            return
    user = await Database.get_user(user_id)
    users_cache.update_user(user)
    await main_menu(user, texts, callback.message)
