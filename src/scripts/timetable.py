import asyncio
import csv

from aiohttp import ClientTimeout, ClientSession
from sqlalchemy import insert, delete
from sqlalchemy.orm import Session

from models import BusTimetable


async def get_timetable_data(db_session: Session, route_name: str, route_id: str) -> None:
    timetable_items: list[dict] = []
    for weekday in ["weekdays", "saturday", "sunday"]:
        url = ""
        try:
            url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-bus-timetable/" \
                  f"main/{route_name}/{weekday}/timetable.csv"
            timeout = ClientTimeout(total=3.0)
            async with ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    reader = csv.reader((await response.text()).splitlines())
                    for route_id, start_stop_id, departure_time in reader:
                        timetable_items.append({
                            "route_id": route_id,
                            "start_stop_id": start_stop_id,
                            "departure_time": departure_time,
                            "weekday": weekday,
                        })
        except asyncio.exceptions.TimeoutError:
            print("TimeoutError")
        except AttributeError:
            print("AttributeError", url)
    db_session.execute(delete(BusTimetable).where(BusTimetable.route_id == route_id and
                                                  BusTimetable.start_stop_id == start_stop_id))
    if timetable_items:
        insert_statement = insert(BusTimetable).values(timetable_items)
        db_session.execute(insert_statement)
    db_session.commit()
