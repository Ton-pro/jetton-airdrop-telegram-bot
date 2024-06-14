from sqlalchemy import Column, BigInteger, Float, String, ARRAY, sql, Integer
from database.db_gino import TimedBaseModel


class Airdrop(TimedBaseModel):
    __tablename__ = 'airdrops'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    start_date = Column(String, nullable=False)
    end_date = Column(String, default=None)
    amount = Column(Float)
    max_count_users = Column(Integer, nullable=False)
    users_got = Column(ARRAY(Integer), default=[])
    jetton_wallet = Column(String, default=None)
    jetton_name = Column(String, default=None)

    query: sql.select
