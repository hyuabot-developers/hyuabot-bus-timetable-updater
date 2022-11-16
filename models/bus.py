from sqlalchemy import PrimaryKeyConstraint, Column
from sqlalchemy.sql import sqltypes

from models import BaseModel


class BusRoute(BaseModel):
    __tablename__ = "bus_route"
    company_id = Column(sqltypes.Integer, nullable=False)
    company_name = Column(sqltypes.String(30), nullable=False)
    company_telephone = Column(sqltypes.String(15), nullable=False)
    district_code = Column(sqltypes.Integer, nullable=False)
    up_first_time = Column(sqltypes.Time, nullable=False)
    up_last_time = Column(sqltypes.Time, nullable=False)
    down_first_time = Column(sqltypes.Time, nullable=False)
    down_last_time = Column(sqltypes.Time, nullable=False)
    start_stop_id = Column(sqltypes.Integer, nullable=False)
    end_stop_id = Column(sqltypes.Integer, nullable=False)
    route_name = Column(sqltypes.String(30), nullable=False)
    route_type_code = Column(sqltypes.String(10), nullable=False)
    route_type_name = Column(sqltypes.String(10), nullable=False)
    route_id = Column(sqltypes.Integer, nullable=False, primary_key=True)


class BusTimetable(BaseModel):
    __tablename__ = "bus_timetable"
    __table_args__ = (PrimaryKeyConstraint("route_id", "start_stop_id", "departure_time"),)
    route_id = Column(sqltypes.Integer, nullable=False)
    start_stop_id = Column(sqltypes.Integer, nullable=False)
    departure_time = Column(sqltypes.Time, nullable=False)
    weekday = Column(sqltypes.String, nullable=False)
