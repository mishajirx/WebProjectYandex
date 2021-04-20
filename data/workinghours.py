import sqlalchemy
from data.db_session import SqlAlchemyBase


class WH(SqlAlchemyBase):
    __tablename__ = 'workinghours'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('couriers.id'),
                                   nullable=True)
    hours = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sqlalchemy.orm.relation('Couriers')
