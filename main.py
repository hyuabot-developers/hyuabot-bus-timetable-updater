import asyncio

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from models.bus import BusRoute
from scripts.timetable import get_timetable_data
from utils.database import get_db_engine


async def main():
    connection = await get_db_engine()
    session_constructor = sessionmaker(bind=connection)
    session = session_constructor()
    if session is None:
        raise RuntimeError("Failed to get db session")

    route_query = select([BusRoute.route_name, BusRoute.route_id])
    route_list = [(route_name, route_id) for route_name, route_id in connection.execute(route_query)]
    job_list = []
    for route_name, route_id in route_list:
        if route_name in ["62", "909"]:
            continue
        job_list.append(get_timetable_data(session, route_name, route_id))
    await asyncio.gather(*job_list)
    session.close()

if __name__ == '__main__':
    asyncio.run(main())