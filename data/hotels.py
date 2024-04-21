import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Hotel(SqlAlchemyBase):
    __tablename__ = 'hotels'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    geocode = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    countryCode = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    
    def __repr__(self):
        return f'<Hotel> {self.id} {self.name} {self.geocode} {self.countryCode}'