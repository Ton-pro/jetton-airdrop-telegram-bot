from sqlalchemy import Column, BigInteger, Integer, String, sql, Float, ARRAY, Boolean
from database.db_gino import TimedBaseModel


class Channel(TimedBaseModel):
    __tablename__ = 'channels'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String)
    title = Column(String)
    channel_id = Column(BigInteger, default=0)
    type = Column(String)

    query: sql.select