import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Intermediate(SqlAlchemyBase):
    __tablename__ = 'intermediate'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_trip = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("trips.id"))
    
    
    def get_trip(self):
        from .trips import Trip
        return Trip.query.get(self.id_trip)
