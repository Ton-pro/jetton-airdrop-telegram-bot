from sqlalchemy import Column, BigInteger, Integer, String, sql, Float, Boolean
from database.db_gino import TimedBaseModel
from config import INITIAL_BALANCE


class User(TimedBaseModel):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    referral_id = Column(BigInteger, default=None)
    level_1 = Column(Integer, default=0)
    level_2 = Column(Integer, default=0)
    balance = Column(Float, default=INITIAL_BALANCE)
    wallet = Column(String, default=None)
    wallet_provider = Column(String, default=None)
    wallet_verif = Column(Integer, default=0)
    lang = Column(String, default='')
    isSubscribe = Column(Boolean, default=False)

    query: sql.select
