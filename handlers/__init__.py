__all__ = ['register_handlers']

import re
from aiogram import F, Router
from aiogram.filters import Command

from .start import start, start_callback, start_lang_callback, check_group_callback
from .wallet import connect_wallet, connected_wallet, disconnect_wallet
from .claim_airdrop import claim_airdrop
from middleware import UserCacheMiddleware


async def register_handlers(router: Router):
    router.message.middleware(UserCacheMiddleware())
    router.callback_query.middleware(UserCacheMiddleware())
    router.message.register(start, Command('start'))
    router.callback_query.register(start_callback, F.data == "menu")
    router.message.register(start, Command('menu'))
    router.callback_query.register(connect_wallet, F.data == 'wallets')
    router.callback_query.register(connected_wallet, lambda query: query.data.startswith('connect:'))
    router.callback_query.register(disconnect_wallet, F.data == 'disconnect')
    router.callback_query.register(claim_airdrop, F.data == 'airdrop')
    router.callback_query.register(start_lang_callback, lambda q: re.match('^lang_[a-z]{2}$', q.data))
