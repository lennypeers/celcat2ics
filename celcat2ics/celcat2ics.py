#!/usr/bin/env python3

""" celcat is shit bro """

import json
import datetime
from typing import Optional

import requests


# pylint: disable=fixme
def fetch_celcat(
    url: str,
    group: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    """
    Fetch the json time table from the website.

    :param url: the url of the target celcat host.
    :param groups: the target group's code.
    :param start: yyyy-mm-dd formatted date
    :param end: yyyy-mm-dd formatted date
    :return: the json table.
    """
    # Default ranges
    parse_mmdd = datetime.datetime.now().strftime("-%m-%d")
    parse_yyyy = datetime.datetime.now().strftime("%Y")
    parse_yyyy_plus1 = str(int(datetime.datetime.now().strftime("%Y")) + 1)

    start = start or parse_yyyy + parse_mmdd
    end = end or parse_yyyy_plus1 + parse_mmdd

    assert start <= end, "illogic args"

    target = url + "/Home/GetCalendarData/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    data = (
        "start="
        + start
        + "&end="
        + end
        + "&federationIds%5B%5D="
        + group
        + "&calView=month"
        + "&resType=103"  # TODO view
    )
    res = requests.post(target, data=data, headers=headers)

    assert res.status_code == 200, "BRRRRUUUH"

    return json.loads(res.text)


ICS_HEADER = {
    "BEGIN": "VCALENDAR",
    "METHOD": "REQUEST",
    "PRODID": "-//ADE/version 6.0",  # Lol
    "VERSION": "2.0",
    "CALSCALE": "GREGORIAN",
}
ICS_FOOTER = {"END": "VCALENDAR"}


def json_to_ics(json_cal: list) -> list[str]:
    """
    Convert a json calendar to ics.

    :param json_cal: the celcat json format to convert
    :return: lines of the ics file
    """
    ret = []

    parse_time = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

    def ics_date(date: str):
        """clean up a date"""
        return date.replace(":", "").replace("-", "")

    def write(stuff: dict) -> None:
        """Quick write closure"""
        ret.extend([f"{key}: {val}" for key, val in stuff.items()])

    write(ICS_HEADER)

    # Calendar stuff
    # TODO: add more information to the keys instead of having a big description
    for item in json_cal:
        if item["sites"]:
            location = ", ".join(item["sites"])
        else:
            location = "No location"

        if item["modules"]:
            summary = ", ".join(item["modules"])
        else:
            summary = "No summary"

        # description processing
        description = item["description"]
        description = description.replace("\r", "")
        description = description.replace("\n", "")
        description = description.replace("<br />", "\\n")

        write(
            {
                "BEGIN": "VEVENT",
                "CREATED": "19700101T000000Z",
                "DTSTAMP": parse_time,
                "DTSTART": ics_date(item["start"]),
                "DTEND": ics_date(item["end"]),
                "SUMMARY": summary,
                "LOCATION": location,
                "DESCRIPTION": description,
                "LAST-MODIFIED": parse_time,
                # TODO: add uid
                # "UID": None,
                # TODO: sequence seed
                # "SEQUENCE": "VCALENDAR",
                "END": "VEVENT",
            }
        )
        cool = description.split(r"\n")
        print(cool, end="\n\n")

    write(ICS_FOOTER)

    return ret

# vim: set ts=4 sts=4 sw=4 et :
