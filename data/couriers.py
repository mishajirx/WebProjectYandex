import sqlalchemy
from data.db_session import SqlAlchemyBase


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    maxw = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    currentw = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    earnings = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    last_delivery_t = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')
    last_assign_time = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')
    last_pack_cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
