import sqlalchemy
from data.db_session import SqlAlchemyBase


class DH(SqlAlchemyBase):
    __tablename__ = 'deliveryhours'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    hours = sqlalchemy.Column(sqlalchemy.String, nullable=True)
