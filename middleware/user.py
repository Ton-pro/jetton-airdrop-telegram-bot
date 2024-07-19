import re
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram import BaseMiddleware
from database import Database
from keyboards.inline import InlineKeyboard
from utils import get_referral_id, check_channels
from config import users_cache, translations_cache, INITIAL_REFERRAL_TOKENS, logger

class UserCacheMiddleware(BaseMiddleware):
    def __init__(self):
        self.cache = users_cache.cache

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        if user_id in self.cache:
            data['cached_user'] = self.cache[user_id]
        else:
            user = await Database.get_user(user_id)
            if user is not None:
                self.cache[user_id] = user
                data['cached_user'] = user
            else:
                referral_id = None
                if isinstance(event, Message):
                    referral_id = get_referral_id(event, int(user_id))
                user = await Database.insert_user(user_id, referral_id)
                self.cache[user_id] = user
                data['cached_user'] = user
        if isinstance(event, CallbackQuery) and re.search('^lang_[a-z]{2}$', event.data):
            return await handler(event, data)
        if self.cache[user_id].lang:
            if not self.cache[user_id].isSubscribe:
                texts = translations_cache.cache[self.cache[user_id].lang]
                channels = await Database.get_channels()
                status = await check_channels(channels, user_id, texts, event)
                if status:
                    if not self.cache[user_id].isSubscribe:
                        await Database.update_subscription_status(user_id)
                        user = await Database.get_user(user_id)
                        users_cache.update_user(user)
                        data['cached_user'] = user
                    if self.cache[user_id].referral_id:
                        await Database.update_referrals(self.cache[user_id].referral_id, 1, INITIAL_REFERRAL_TOKENS)
                else:
                    if isinstance(event, CallbackQuery):
                        await event.answer(text=texts['not_subscribed'], show_alert=True)
                    return
        else:
            texts = translations_cache.cache[event.from_user.language_code if event.from_user.language_code == "ru" else "en"]
            if isinstance(event, CallbackQuery):
                await event.message.edit_text(
                    text=texts['lang_selector'],
                    reply_markup=await InlineKeyboard.select_lang(),
                    disable_web_page_preview=True)

            else:
                await event.answer(
                    text=texts['lang_selector'],
                    reply_markup=await InlineKeyboard.select_lang(),
                    disable_web_page_preview=True)
            return
        return await handler(event, data)
