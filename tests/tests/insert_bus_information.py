import asyncio

from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models import BusRoute, BusStop


async def initialize_bus_data(db_session: Session):
    await insert_bus_stop(db_session)
    await insert_bus_route(db_session)


async def insert_bus_stop(db_session: Session):
    keywords = ["경기테크노파크", "한양대", "한국생산기술연구원", "성안길입구", "신안산대학교",
                "새솔고", "상록수역", "수원역", "강남역우리은행", "본오동", "한라비발디1차", "푸르지오6차후문",
                "선부동차고지", "안산역", "경인합섬앞", "오목천차고지"]
    tasks = [fetch_bus_stop(db_session, keyword) for keyword in keywords]
    await asyncio.gather(*tasks)
    db_session.commit()


async def fetch_bus_stop(db_session: Session, keyword: str):
    url = f"http://openapi.gbis.go.kr/ws/rest/busstationservice?serviceKey=1234567890&keyword={keyword}"
    stop_list: list[dict] = []
    timeout = ClientTimeout(total=3.0)
    try:
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), features="xml")
                station_list = soup.find("response").find("msgBody").find_all("busStationList")
                for station in station_list:
                    stop_list.append(dict(
                        stop_id=station.find("stationId").text,
                        stop_name=station.find("stationName").text,
                        district_code=station.find("districtCd").text,
                        mobile_number=station.find("mobileNo").text,
                        region_name=station.find("regionName").text,
                        latitude=station.find("x").text,
                        longitude=station.find("y").text,
                    ))
                insert_statement = insert(BusStop).values(stop_list)
                insert_statement = insert_statement.on_conflict_do_update(
                    index_elements=["stop_id"],
                    set_=dict(
                        stop_name=insert_statement.excluded.stop_name,
                        district_code=insert_statement.excluded.district_code,
                        mobile_number=insert_statement.excluded.mobile_number,
                        region_name=insert_statement.excluded.region_name,
                        latitude=insert_statement.excluded.latitude,
                        longitude=insert_statement.excluded.longitude,
                    ),
                )
                db_session.execute(insert_statement)
                db_session.commit()
    except asyncio.exceptions.TimeoutError:
        print("TimeoutError", url)
    except AttributeError:
        print("AttributeError", url)


async def insert_bus_route(db_session: Session):
    routes = ["10-1", "62", "3100", "3101", "3102", "110", "707", "909"]
    tasks = [fetch_bus_route_list(db_session, route) for route in routes]
    await asyncio.gather(*tasks)
    db_session.commit()


async def fetch_bus_route_list(db_session: Session, keyword: str):
    url = f"http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey=1234567890&keyword={keyword}"
    route_list: list[str] = []
    timeout = ClientTimeout(total=3.0)
    try:
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), features="xml")
                route_search_list = soup.find("response").find("msgBody").find_all("busRouteList")
                for route in route_search_list:
                    if "안산" in route.find("regionName").text:
                        route_list.append(route.find("routeId").text)
                tasks = [insert_bus_route_item(db_session, route_id) for route_id in route_list]
                await asyncio.gather(*tasks)
    except asyncio.exceptions.TimeoutError:
        print("TimeoutError", url)
    except AttributeError:
        print("AttributeError", url)


async def insert_bus_route_item(db_session: Session, route_id: str):
    url = f"http://openapi.gbis.go.kr/ws/rest/busrouteservice/info" \
          f"?serviceKey=1234567890&routeId={route_id}"
    route_list: list[dict] = []
    timeout = ClientTimeout(total=3.0)
    try:
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), features="xml")
                route_search_item = soup.find("response").find("msgBody").find("busRouteInfoItem")
                if route_search_item is None:
                    return
                route_list.append(dict(
                    company_id=route_search_item.find("companyId").text,
                    company_name=route_search_item.find("companyName").text,
                    company_telephone=route_search_item.find("companyTel").text,
                    district_code=route_search_item.find("districtCd").text,
                    up_first_time=f"{route_search_item.find('upFirstTime').text}+09:00",
                    up_last_time=f"{route_search_item.find('upLastTime').text}+09:00",
                    down_first_time=f"{route_search_item.find('downFirstTime').text}+09:00",
                    down_last_time=f"{route_search_item.find('downLastTime').text}+09:00",
                    start_stop_id=route_search_item.find("startStationId").text,
                    end_stop_id=route_search_item.find("endStationId").text,
                    route_id=route_search_item.find("routeId").text,
                    route_name=route_search_item.find("routeName").text,
                    route_type_code=route_search_item.find("routeTypeCd").text,
                    route_type_name=route_search_item.find("routeTypeName").text,
                ))
                insert_statement = insert(BusRoute).values(route_list)
                insert_statement = insert_statement.on_conflict_do_update(
                    index_elements=["route_id"],
                    set_=dict(
                        company_id=insert_statement.excluded.company_id,
                        company_name=insert_statement.excluded.company_name,
                        company_telephone=insert_statement.excluded.company_telephone,
                        district_code=insert_statement.excluded.district_code,
                        up_first_time=insert_statement.excluded.up_first_time,
                        up_last_time=insert_statement.excluded.up_last_time,
                        down_first_time=insert_statement.excluded.down_first_time,
                        down_last_time=insert_statement.excluded.down_last_time,
                        start_stop_id=insert_statement.excluded.start_stop_id,
                        end_stop_id=insert_statement.excluded.end_stop_id,
                        route_name=insert_statement.excluded.route_name,
                        route_type_code=insert_statement.excluded.route_type_code,
                        route_type_name=insert_statement.excluded.route_type_name,
                    ),
                )
                db_session.execute(insert_statement)
                db_session.commit()
    except asyncio.exceptions.TimeoutError:
        print("TimeoutError", url)
    except AttributeError:
        print("AttributeError", url)
