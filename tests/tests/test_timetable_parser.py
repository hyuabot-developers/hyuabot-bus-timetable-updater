from scripts.timetable import parse_timetable_csv


def test_parse_timetable_csv_adds_timezone_and_weekday():
    result = parse_timetable_csv(
        "216000068,216000358,05:30\n216000068,216000358,06:00\n",
        "weekdays",
    )

    assert result == [
        {
            "route_id": "216000068",
            "start_stop_id": "216000358",
            "departure_time": "05:30 +09:00",
            "weekday": "weekdays",
        },
        {
            "route_id": "216000068",
            "start_stop_id": "216000358",
            "departure_time": "06:00 +09:00",
            "weekday": "weekdays",
        },
    ]
