import asyncio
import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from models import BaseModel, BusRoute, BusTimetable
from scripts.timetable import get_timetable_data
from tests.insert_bus_information import initialize_bus_data
from utils.database import get_db_engine


class TestFetchTimetableData:
    connection: Engine | None = None
    session_constructor = None
    session: Session | None = None

    @classmethod
    def setup_class(cls):
        cls.connection = get_db_engine()
        cls.session_constructor = sessionmaker(bind=cls.connection)
        # Database session check
        cls.session = cls.session_constructor()
        assert cls.session is not None
        # Migration schema check
        BaseModel.metadata.create_all(cls.connection)
        # Insert initial data
        asyncio.run(initialize_bus_data(cls.session))
        cls.session.commit()
        cls.session.close()

    @pytest.mark.asyncio
    async def test_fetch_realtime_data(self):
        connection = get_db_engine()
        session_constructor = sessionmaker(bind=connection)
        # Database session check
        session = session_constructor()
        # Get list to fetch
        route_query = select(BusRoute.route_name, BusRoute.route_id)
        route_list = [(route_name, route_id) for route_name, route_id in session.execute(route_query)]
        job_list = []
        for route_name, route_id in route_list:
            if route_name in ["62", "9090"]:
                continue
            job_list.append(get_timetable_data(session, route_name, route_id))
        await asyncio.gather(*job_list)

        # Check if the data is inserted
        timetable_list = session.query(BusTimetable).all()
        for timetable_item in timetable_list:  # type: BusTimetable
            assert type(timetable_item.route_id) == int
            assert type(timetable_item.start_stop_id) == int
            assert type(timetable_item.departure_time) == datetime.time
            assert type(timetable_item.weekday) == str
