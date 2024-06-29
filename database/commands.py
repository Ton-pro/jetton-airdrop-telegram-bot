from config import logger, users_cache, INITIAL_REFERRAL_TOKENS, SECOND_LEVEL_REFERRAL_TOKENS, CHANNELS_LIST, AIRDROP_START_DATE, AIRDROP_END_DATE, AIRDROP_AMOUNT, AIRDROP_MAX_COUNT_USERS, AIRDROP_JETTON_WALLET, AIRDROP_JETTON_NAME
from .db_gino import db, on_startup
from .schemas.user import User
from .schemas.airdrop import Airdrop
from .schemas.channel import Channel
from utils import get_chat_info

class Database:
    @classmethod
    async def db_init(cls):
        await on_startup()
        # await db.gino.drop_all()
        await db.gino.create_all()
        channels = await cls.get_channels()
        if len(channels) == 0:
            await cls.insert_channels()
        airdrops = await cls.get_airdrops()
        if len(airdrops) == 0:
            await cls.insert_airdrops()

        if db:
            logger.info("Database was connected")
        else:
            logger.error("Database was not connected")
            exit(1)

    @classmethod
    async def get_user(cls, user_id: int):
        return await User.query.where(User.user_id == user_id).gino.first()

    @classmethod
    async def update_referrals(cls, user_id: int, level: int, tokens: int):
        user = await cls.get_user(user_id)
        logger.error(user_id)
        if level == 1:
            await User.update.values(level_1=user.level_1 + 1, balance=user.balance + tokens).where(
                User.user_id == user_id).gino.status()

        elif level == 2:
            await User.update.values(level_2=user.level_2 + 1, balance=user.balance + tokens).where(
                User.user_id == user_id).gino.status()

        user = await cls.get_user(user_id)
        users_cache.update_user(user)

        if user.referral_id and level == 1:
            await cls.update_referrals(user.referral_id, 2, SECOND_LEVEL_REFERRAL_TOKENS)

    @classmethod
    async def insert_user(cls, user_id: int, referral_id: int):
        data = await cls.get_user(user_id)
        if data is None:
            if referral_id:
                user = await User(user_id=user_id, referral_id=referral_id).create()
            else:
                user = await User(user_id=user_id).create()
            return user
        return data

    @classmethod
    async def update_lang(cls, user_id: int, lang: str):
        await User.update.values(lang=lang).where(User.user_id == user_id).gino.status()

    @classmethod
    async def update_subscription_status(cls, user_id: int):
        await User.update.values(isSubscribe=True).where(User.user_id == user_id).gino.status()

    @classmethod
    async def update_wallet(cls, user_id: int, wallet: str | None, wallet_verif: int, wallet_provider: str | None):
        await User.update.values(wallet=wallet, wallet_verif=wallet_verif, wallet_provider=wallet_provider).where(
            User.user_id == user_id).gino.status()
        user = await cls.get_user(user_id)
        users_cache.update_user(user)

    @classmethod
    async def get_airdrops(cls):
        return await Airdrop.query.gino.all()

    @classmethod
    async def insert_airdrops(cls):
        await Airdrop(start_date=AIRDROP_START_DATE, end_date=AIRDROP_END_DATE, amount=AIRDROP_AMOUNT, max_count_users=AIRDROP_MAX_COUNT_USERS, jetton_wallet=AIRDROP_JETTON_WALLET, jetton_name=AIRDROP_JETTON_NAME).create()

    @classmethod
    async def update_users_airdrop(cls, airdrop_id: int, users: list[int]):
        await Airdrop.update.values(users_got=users).where(Airdrop.id == airdrop_id).gino.status()

    @classmethod
    async def update_balance(cls, user_id: int, amount: int | float):
        await User.update.values(balance=amount).where(User.user_id == user_id).gino.status()

    @classmethod
    async def get_channels(cls):
        return await Channel.query.gino.all()

    @classmethod
    async def insert_channels(cls):
        for channel in CHANNELS_LIST:
            chat = await get_chat_info(channel)
            await Channel(username=channel, title=chat.title, type=chat.type, channel_id=chat.id).create()