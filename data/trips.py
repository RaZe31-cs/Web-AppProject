import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Trip(SqlAlchemyBase):
    __tablename__ = 'trips'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    city_from = sqlalchemy.Column(sqlalchemy.String)
    city_to = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    transport_id = sqlalchemy.Column(sqlalchemy.Integer)
    hotel_id = sqlalchemy.Column(sqlalchemy.Integer)
    list_of_routes = sqlalchemy.Column(sqlalchemy.String)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')


    def __repr__(self):
        return f'<Trip> {self.id} {self.city_from}-{self.city_to} {self.date}'
