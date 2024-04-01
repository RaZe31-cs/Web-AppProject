import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Trip(SqlAlchemyBase):
    __tablename__ = 'trips'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_trip = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime)


    def __repr__(self):
        return f'<Trip> {self.id} {self.name_trip} {self.date}'
