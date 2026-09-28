import asyncio
import csv

from aiohttp import ClientTimeout, ClientSession
from sqlalchemy import insert, delete
from sqlalchemy.orm import Session

from models import BusTimetable


def parse_timetable_csv(contents: str, weekday: str) -> list[dict[str, str]]:
    return [
        {
            "route_id": route_id,
            "start_stop_id": start_stop_id,
            "departure_time": f"{departure_time} +09:00",
            "weekday": weekday,
        }
        for route_id, start_stop_id, departure_time in csv.reader(contents.splitlines())
    ]


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
                    timetable_items.extend(parse_timetable_csv(await response.text(), weekday))
        except asyncio.exceptions.TimeoutError:
            print("TimeoutError")
        except AttributeError:
            print("AttributeError", url)
    db_session.execute(delete(BusTimetable).where(BusTimetable.route_id == route_id))
    if timetable_items:
        insert_statement = insert(BusTimetable).values(timetable_items)
        db_session.execute(insert_statement)
    db_session.commit()
