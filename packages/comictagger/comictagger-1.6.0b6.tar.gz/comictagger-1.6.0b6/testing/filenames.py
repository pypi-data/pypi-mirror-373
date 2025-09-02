"""
format is
(
    "filename",
    "reason or unique case",
    {
        "expected": "Dictionary of properties extracted from filename",
    },
    bool(xfail: expected failure on the old parser)
)
"""

from __future__ import annotations

import datetime
import functools
import importlib.resources
import os
import pathlib
from contextlib import nullcontext as does_not_raise
from typing import NamedTuple

import pytest

xfail = functools.partial(pytest.mark.xfail, strict=True)

hash_removed = functools.partial(xfail, reason="hash removed")
original_parser = functools.partial(xfail, reason="original_parser")

datadir = importlib.resources.files(__package__).joinpath("data")
cbz_path = datadir.joinpath("Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz")


class HXFail(NamedTuple):
    with_hash: pytest.MarkDecorator | tuple[pytest.Mark]
    without_hash: pytest.MarkDecorator | tuple[pytest.Mark]


class ParserXFail(NamedTuple):
    """If the filename is expected to fail for a parser"""

    """
    Expected to fail with the original parser

    first item is with a `#` in front of the issue number second item is without
    """
    original: HXFail

    """
    Expected to fail with the complicated parser

    first item is with a `#` in front of the issue number second item is without
    """
    complicated: HXFail


def PXFail(
    original: None | pytest.MarkDecorator | tuple[pytest.MarkDecorator | None, pytest.MarkDecorator | None] | HXFail,
    complicated: None | pytest.MarkDecorator | tuple[pytest.MarkDecorator | None, pytest.MarkDecorator | None] | HXFail,
) -> ParserXFail:
    if isinstance(original, tuple):
        with_hash, without_hash = original
        original = HXFail(with_hash or tuple(), without_hash or tuple())
    if original is None:
        original = HXFail(tuple(), tuple())
    if isinstance(original, pytest.MarkDecorator):
        original = HXFail(original, original)

    if isinstance(complicated, tuple):
        with_hash, without_hash = complicated
        complicated = HXFail(with_hash or tuple(), without_hash or tuple())
    if complicated is None:
        complicated = HXFail(tuple(), tuple())
    if isinstance(complicated, pytest.MarkDecorator):
        complicated = HXFail(complicated, complicated)

    return ParserXFail(original, complicated)


class Rename(NamedTuple):
    format: str
    move: bool
    move_only: bool
    smart_cleanup: bool
    platform: str
    expected: str
    exception: Exception | does_not_raise
    warnings: list[str]


class Name(NamedTuple):
    filename: str
    """comment explaning what is being tested"""
    comment: str
    expected: dict
    xfail: ParserXFail


names: tuple[Name, ...] = (
    Name(
        filename="Nickel Comics #08 [Fawcett][Aug23'1940][paper+1fiche][ibc upgraded]-c2c -RH+ML.cbz",
        comment="Run-on date and ignore following remainder (-c2c -RH+ML)",
        expected={
            "issue": "8",
            "series": "Nickel Comics",
            "title": "",
            "volume": "",
            "year": "1940",
            "remainder": "[paper+1fiche][ibc upgraded] RH+ML",
            "publisher": "Fawcett",
            "issue_count": "",
            "alternate": "",
            "archive": "cbz",
            "c2c": True,
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="De Psy #6 Bonjour l'angoisse!.cbz",
        comment="Annoying French words: `'`",
        expected={
            "issue": "6",
            "series": "De Psy",
            "title": "Bonjour l'angoisse!",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
            "archive": "cbz",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Airfiles #4 The 'Big Show'.cbz",
        comment="quoted words `'Big Show'`",
        expected={
            "issue": "4",
            "series": "Airfiles",
            "title": "The 'Big Show'",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
            "archive": "cbz",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Conceptions #1 Conceptions I.cbz",
        comment="&",
        expected={
            "issue": "1",
            "series": "Conceptions",
            "title": "Conceptions I",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
            "archive": "cbz",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Series #1 Stop it!.cbz",
        comment="trailing `!`",
        expected={
            "issue": "1",
            "series": "Series",
            "title": "Stop it!",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
            "archive": "cbz",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Drystan & Esyllt #3",
        comment="&",
        expected={
            "issue": "3",
            "series": "Drystan & Esyllt",
            "title": "",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Michel Vaillant #5 Nr. 13 aan de start",
        comment="Shortened word followed by a number: `Nr. 13`",
        expected={
            "issue": "5",
            "series": "Michel Vaillant",
            "title": "Nr. 13 aan de start",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Karl May #001 Old Shatterhand.cbr",
        comment="Month in series: `May`",
        expected={
            "archive": "cbr",
            "issue": "1",
            "series": "Karl May",
            "title": "Old Shatterhand",
            "publisher": "",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Michel Vaillant #8 De 8ste man",
        comment="Non english ordinal: `8ste`",
        expected={
            "issue": "8",
            "series": "Michel Vaillant",
            "title": "De 8ste man",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Michel Vaillant #13 Mach 1 voor Steve Warson",
        comment="number in title: `1`",
        expected={
            "issue": "13",
            "series": "Michel Vaillant",
            "title": "Mach 1 voor Steve Warson",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Michel Vaillant #19 5 Meisjes in de race",
        comment="number starting title: `5`",
        expected={
            "issue": "19",
            "series": "Michel Vaillant",
            "title": "5 Meisjes in de race",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=(None, hash_removed())),
    ),
    Name(
        filename="Michel Vaillant #34 Steve Warson gaat K.O.",
        comment="acronym: `K.O.`",
        expected={
            "issue": "34",
            "series": "Michel Vaillant",
            "title": "Steve Warson gaat K.O.",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Michel Vaillant #40 F.1 in oproer",
        comment="acronym with numbers: `F.1`",
        expected={
            "issue": "40",
            "series": "Michel Vaillant",
            "title": "F.1 in oproer",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Michel Vaillant #42 300 kmu door Parijs",
        comment="number starting title: `300`",
        expected={
            "issue": "42",
            "series": "Michel Vaillant",
            "title": "300 kmu door Parijs",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=(None, hash_removed())),
    ),
    Name(
        filename="Michel Vaillant #52 F 3000",
        comment="title ends with number: `3000`",
        expected={
            "issue": "52",
            "series": "Michel Vaillant",
            "title": "F 3000",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Michel Vaillant #66 100.000.000 $ voor Steve Warson",
        comment="number separator is . and dollarsign after number",
        expected={
            "issue": "66",
            "series": "Michel Vaillant",
            "title": "100.000.000 $ voor Steve Warson",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="batman #B01 title (DC).cbz",
        comment="protofolius_issue_number_scheme",
        expected={
            "archive": "cbz",
            "issue": "B1",
            "series": "batman",
            "title": "title",
            "publisher": "DC",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
            "format": "biography/best of",
        },
        xfail=PXFail(
            original=(None, xfail(reason="Protofolius Issue Number Scheme")),
            complicated=(None, xfail(reason="Protofolius Issue Number Scheme")),
        ),
    ),
    Name(
        filename="batman #3 title (DC).cbz",
        comment="publisher in parenthesis: `DC`",
        expected={
            "archive": "cbz",
            "issue": "3",
            "series": "batman",
            "title": "title",
            "publisher": "DC",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="batman #3 title DC.cbz",
        comment="publisher in title: DC",
        expected={
            "archive": "cbz",
            "issue": "3",
            "series": "batman",
            "title": "title DC",
            "publisher": "DC",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="batman #3 title (DC.cbz",
        comment="publisher in title unclosed parenthesis: `(DC",
        expected={
            "archive": "cbz",
            "issue": "3",
            "series": "batman",
            "title": "title",
            "publisher": "DC",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="ms. Marvel #3.cbz",
        comment="honorific `ms` and publisher in series `marvel`",
        expected={
            "archive": "cbz",
            "issue": "3",
            "series": "ms. Marvel",
            "title": "",
            "publisher": "Marvel",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Dr. Doom And The Masters Of Evil #1 (2009).cbz",
        comment="honorific in series: `Dr.`",
        expected={
            "archive": "cbz",
            "issue": "1",
            "series": "Dr. Doom And The Masters Of Evil",
            "title": "",
            "publisher": "",
            "volume": "",
            "year": "2009",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename=f"action comics #{datetime.datetime.now().year}.cbz",
        comment=f"issue number is current year (`{datetime.datetime.now().year}`)",
        expected={
            "archive": "cbz",
            "issue": f"{datetime.datetime.now().year}",
            "series": "action comics",
            "title": "",
            "publisher": "",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="action comics 1024.cbz",
        comment="issue number is 4 digits: `1024`",
        expected={
            "archive": "cbz",
            "issue": "1024",
            "series": "action comics",
            "title": "",
            "publisher": "",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Action Comics #1001 (2018).cbz",
        comment="issue number is current year (digits == 4)",
        expected={
            "archive": "cbz",
            "issue": "1001",
            "series": "Action Comics",
            "title": "",
            "publisher": "",
            "volume": "",
            "year": "2018",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="january jones #2.cbz",
        comment="month in series",
        expected={
            "archive": "cbz",
            "issue": "2",
            "series": "january jones",
            "title": "",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="#52.cbz",
        comment="issue number only",
        expected={
            "archive": "cbz",
            "issue": "52",
            "series": "52",
            "title": "",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "alternate": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="52 Monster_Island_v1_#2__repaired__c2c.cbz",
        comment="leading alternate",
        expected={
            "archive": "cbz",
            "issue": "2",
            "series": "Monster Island",
            "title": "",
            "volume": "1",
            "year": "",
            "remainder": "repaired",
            "issue_count": "",
            "alternate": "52",
            "c2c": True,
        },
        xfail=PXFail(original=xfail(reason="original parser"), complicated=None),
    ),
    Name(
        filename="Monster_Island_v1_#2__repaired__c2c.cbz",
        comment="Example from userguide",
        expected={
            "archive": "cbz",
            "issue": "2",
            "series": "Monster Island",
            "title": "",
            "volume": "1",
            "year": "",
            "remainder": "repaired",
            "issue_count": "",
            "c2c": True,
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Monster Island v1 #3 (1957) -- The Revenge Of King Klong (noads).cbz",
        comment="Example from userguide",
        expected={
            "archive": "cbz",
            "issue": "3",
            "series": "Monster Island",
            "title": "",
            "volume": "1",
            "year": "1957",
            "remainder": "The Revenge Of King Klong (noads)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Foobar-Man Annual #121 - The Wrath of Foobar-Man, Part 1 of 2.cbz",
        comment="Example from userguide",
        expected={
            "archive": "cbz",
            "issue": "121",
            "series": "Foobar-Man Annual",
            "title": "The Wrath of Foobar-Man, Part 1 of 2",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
            "annual": True,
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Plastic Man v1 #002 (1942).cbz",
        comment="Example from userguide",
        expected={
            "archive": "cbz",
            "issue": "2",
            "series": "Plastic Man",
            "title": "",
            "volume": "1",
            "year": "1942",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Blue Beetle #02.cbr",
        comment="Example from userguide",
        expected={
            "archive": "cbr",
            "issue": "2",
            "series": "Blue Beetle",
            "title": "",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Blue Beetle #½.cbr",
        comment="½",
        expected={
            "archive": "cbr",
            "issue": "½",
            "series": "Blue Beetle",
            "title": "",
            "volume": "",
            "year": "",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Monster Island vol. 2 #2.cbz",
        comment="Example from userguide",
        expected={
            "archive": "cbz",
            "issue": "2",
            "series": "Monster Island",
            "title": "",
            "volume": "2",
            "year": "",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Crazy Weird Comics #2 (of 2) (1969).rar",
        comment="Example from userguide",
        expected={
            "archive": "rar",
            "issue": "2",
            "series": "Crazy Weird Comics",
            "title": "",
            "volume": "",
            "year": "1969",
            "remainder": "",
            "issue_count": "2",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Super Strange Yarns (1957) #92 (1969).cbz",
        comment="Example from userguide",
        expected={
            "archive": "cbz",
            "issue": "92",
            "series": "Super Strange Yarns",
            "title": "",
            "volume": "1957",
            "year": "1969",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Action Spy Tales v1965 #3.cbr",
        comment="Example from userguide",
        expected={
            "archive": "cbr",
            "issue": "3",
            "series": "Action Spy Tales",
            "title": "",
            "volume": "1965",
            "year": "",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename=" X-Men-V1-#067.cbr",
        comment="hyphen separated with hyphen in series",  # only parses correctly because v1 designates the volume
        expected={
            "archive": "cbr",
            "issue": "67",
            "series": "X-Men",
            "title": "",
            "volume": "1",
            "year": "",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Amazing Spider-Man #078.BEY (2022) (Digital) (Zone-Empire).cbr",
        comment="number issue with extra",
        expected={
            "archive": "cbr",
            "issue": "78.BEY",
            "series": "Amazing Spider-Man",
            "title": "",
            "volume": "",
            "year": "2022",
            "remainder": "(Digital) (Zone-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Angel Wings #02 - Black Widow (2015) (Scanlation) (phillywilly).cbr",
        comment="title after #issue",
        expected={
            "archive": "cbr",
            "issue": "2",
            "series": "Angel Wings",
            "title": "Black Widow",
            "volume": "",
            "year": "2015",
            "remainder": "(Scanlation) (phillywilly)",
            "issue_count": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Aquaman - Green Arrow - Deep Target #01 (of 07) (2021) (digital) (Son of Ultron-Empire).cbr",
        comment="issue count",
        expected={
            "archive": "cbr",
            "issue": "1",
            "series": "Aquaman - Green Arrow - Deep Target",
            "title": "",
            "volume": "",
            "year": "2021",
            "issue_count": "7",
            "remainder": "(digital) (Son of Ultron-Empire)",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Aquaman 80th Anniversary 100-Page Super Spectacular (2021) #001 (2021) (Digital) (BlackManta-Empire).cbz",
        comment="numbers in series",
        expected={
            "archive": "cbz",
            "issue": "1",
            "series": "Aquaman 80th Anniversary 100-Page Super Spectacular",
            "title": "",
            "volume": "2021",
            "year": "2021",
            "remainder": "(Digital) (BlackManta-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Avatar - The Last Airbender - The Legend of Korra (FCBD 2021) (Digital) (mv-DCP).cbr",
        comment="FCBD date",
        expected={
            "archive": "cbr",
            "issue": "",
            "series": "Avatar - The Last Airbender - The Legend of Korra",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(Digital) (mv-DCP)",
            "issue_count": "",
            "fcbd": True,
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Avengers By Brian Michael Bendis volume 03 (2013) (Digital) (F2) (Kileko-Empire).cbz",
        comment="volume without issue",
        expected={
            "archive": "cbz",
            "issue": "3",
            "series": "Avengers By Brian Michael Bendis",
            "title": "",
            "volume": "3",
            "year": "2013",
            "remainder": "(Digital) (F2) (Kileko-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Avengers By Brian Michael Bendis v03 (2013) (Digital) (F2) (Kileko-Empire).cbz",
        comment="volume without issue: `v`",
        expected={
            "archive": "cbz",
            "issue": "3",
            "series": "Avengers By Brian Michael Bendis",
            "title": "",
            "volume": "3",
            "year": "2013",
            "remainder": "(Digital) (F2) (Kileko-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Batman '89 (2021) (Webrip) (The Last Kryptonian-DCP).cbr",
        comment="year in title without issue: `'89`",
        expected={
            "archive": "cbr",
            "issue": "",
            "series": "Batman '89",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(Webrip) (The Last Kryptonian-DCP)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Batman_-_Superman_#020_(2021)_(digital)_(NeverAngel-Empire).cbr",
        comment="underscores",
        expected={
            "archive": "cbr",
            "issue": "20",
            "series": "Batman - Superman",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(digital) (NeverAngel-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Black Widow #009 (2021) (Digital) (Zone-Empire).cbr",
        comment="standard",
        expected={
            "archive": "cbr",
            "issue": "9",
            "series": "Black Widow",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(Digital) (Zone-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Blade Runner 2029 #006 (2021) (3 covers) (digital) (Son of Ultron-Empire).cbr",
        comment="year before issue",
        expected={
            "archive": "cbr",
            "issue": "6",
            "series": "Blade Runner 2029",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(3 covers) (digital) (Son of Ultron-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Blade Runner Free Comic Book Day 2021 (2021) (digital-Empire).cbr",
        comment="FCBD year and (year)",
        expected={
            "archive": "cbr",
            "issue": "",
            "series": "Blade Runner Free Comic Book Day 2021",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(digital-Empire)",
            "issue_count": "",
            "fcbd": True,
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Bloodshot Book 03 (2020) (digital) (Son of Ultron-Empire).cbr",
        comment="book",
        expected={
            "archive": "cbr",
            "issue": "3",
            "series": "Bloodshot",
            "title": "Book 03",
            "volume": "3",
            "year": "2020",
            "remainder": "(digital) (Son of Ultron-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="book of eli #1 (2020) (digital) (Son of Ultron-Empire).cbr",
        comment="book",
        expected={
            "archive": "cbr",
            "issue": "1",
            "series": "book of eli",
            "title": "",
            "volume": "",
            "year": "2020",
            "remainder": "(digital) (Son of Ultron-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Cyberpunk 2077 - You Have My Word #02 (2021) (digital) (Son of Ultron-Empire).cbr",
        comment="title",
        expected={
            "archive": "cbr",
            "issue": "2",
            "series": "Cyberpunk 2077",
            "title": "You Have My Word",
            "volume": "",
            "year": "2021",
            "issue_count": "",
            "remainder": "(digital) (Son of Ultron-Empire)",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Elephantmen 2259 #008 - Simple Truth 03 (of 06) (2021) (digital) (Son of Ultron-Empire).cbr",
        comment="volume count",
        expected={
            "archive": "cbr",
            "issue": "8",
            "series": "Elephantmen 2259",
            "title": "Simple Truth",
            "volume": "3",
            "year": "2021",
            "volume_count": "6",
            "remainder": "(digital) (Son of Ultron-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Free Comic Book Day - Avengers.Hulk (2021) (2048px) (db).cbz",
        comment="'.' in name",
        expected={
            "archive": "cbz",
            "issue": "",
            "series": "Free Comic Book Day - Avengers Hulk",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(2048px) (db)",
            "issue_count": "",
            "fcbd": True,
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Goblin (2021) (digital) (Son of Ultron-Empire).cbr",
        comment="no-issue",
        expected={
            "archive": "cbr",
            "issue": "",
            "series": "Goblin",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(digital) (Son of Ultron-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Marvel Previews #002 (January 2022) (Digital-Empire).cbr",
        comment="(month year)",
        expected={
            "archive": "cbr",
            "issue": "2",
            "series": "Marvel Previews",
            "title": "",
            "publisher": "Marvel",
            "volume": "",
            "year": "2022",
            "remainder": "(Digital-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Marvel Two In One V1 #090  c2c (Comixbear-DCP).cbr",
        comment="volume then issue",
        expected={
            "archive": "cbr",
            "issue": "90",
            "series": "Marvel Two In One",
            "title": "",
            "publisher": "Marvel",
            "volume": "1",
            "year": "",
            "remainder": "(Comixbear-DCP)",
            "issue_count": "",
            "c2c": True,
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Star Wars - War of the Bounty Hunters - IG-88 (2021) (Digital) (Kileko-Empire).cbz",
        comment="number ends series, no-issue",
        expected={
            "archive": "cbz",
            "issue": "",
            "series": "Star Wars - War of the Bounty Hunters - IG-88",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(Digital) (Kileko-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Star Wars - War of the Bounty Hunters - IG-88 #1 (2021) (Digital) (Kileko-Empire).cbz",
        comment="number ends series",
        expected={
            "archive": "cbz",
            "issue": "1",
            "series": "Star Wars - War of the Bounty Hunters - IG-88",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(Digital) (Kileko-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="The Defenders v1 #058 (1978) (digital).cbz",
        comment="",
        expected={
            "archive": "cbz",
            "issue": "58",
            "series": "The Defenders",
            "title": "",
            "volume": "1",
            "year": "1978",
            "remainder": "(digital)",
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="The Defenders v1 Annual #01 (1976) (Digital) (Minutemen-Slayer).cbr",
        comment=" v in series",
        expected={
            "archive": "cbr",
            "issue": "1",
            "series": "The Defenders Annual",
            "title": "",
            "volume": "1",
            "year": "1976",
            "remainder": "(Digital) (Minutemen-Slayer)",
            "issue_count": "",
            "annual": True,
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="The Magic Order 2 #06 (2022) (Digital) (Zone-Empire)[__913302__].cbz",
        comment="ending id",
        expected={
            "archive": "cbz",
            "issue": "6",
            "series": "The Magic Order 2",
            "title": "",
            "volume": "",
            "year": "2022",
            "remainder": "(Digital) (Zone-Empire)[913302]",  # Don't really care about double underscores
            "issue_count": "",
        },
        xfail=PXFail(original=None, complicated=None),
    ),
    Name(
        filename="Wonder Woman #001 Wonder Woman Day Special Edition (2021) (digital-Empire).cbr",
        comment="issue separates title",
        expected={
            "archive": "cbr",
            "issue": "1",
            "series": "Wonder Woman",
            "title": "Wonder Woman Day Special Edition",
            "volume": "",
            "year": "2021",
            "remainder": "(digital-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=(None, original_parser()), complicated=None),
    ),
    Name(
        filename="Wonder Woman #49 DC Sep-Oct 1951 digital [downsized, lightened, 4 missing story pages restored] (Shadowcat-Empire).cbz",
        comment="date-range, no paren, braces",
        expected={
            "archive": "cbz",
            "issue": "49",
            "series": "Wonder Woman",
            "title": "digital",  # Don't have a way to get rid of this
            "publisher": "DC",
            "volume": "",
            "year": "1951",
            "remainder": "[downsized, lightened, 4 missing story pages restored] (Shadowcat-Empire)",
            "issue_count": "",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="X-Men, 2021-08-04 (#02) (digital) (Glorith-HD).cbz",
        comment="full-date, issue in parenthesis",
        expected={
            "archive": "cbz",
            "issue": "2",
            "series": "X-Men",
            "title": "",
            "volume": "",
            "year": "2021",
            "remainder": "(digital) (Glorith-HD)",
            "issue_count": "",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Cory Doctorow's Futuristic Tales of the Here and Now: Anda's Game #001 (2007).cbz",
        comment="title",
        expected={
            "archive": "cbz",
            "issue": "1",
            "series": "Cory Doctorow's Futuristic Tales of the Here and Now",
            "title": "Anda's Game",
            "volume": "",
            "year": "2007",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
    Name(
        filename="Cory Doctorow's Futuristic Tales of the Here and Now $1$2 3 #0.0.1 (2007).cbz",
        comment="$",
        expected={
            "archive": "cbz",
            "issue": "0.1",
            "series": "Cory Doctorow's Futuristic Tales of the Here and Now $1 $2 3",
            "title": "",
            "volume": "",
            "year": "2007",
            "remainder": "",
            "issue_count": "",
        },
        xfail=PXFail(original=original_parser(), complicated=None),
    ),
)

oldfnames = []
newfnames = []
for p in names:
    filenameinfo = dict(
        alternate="",
        annual=False,
        archive="",
        c2c=False,
        fcbd=False,
        issue="",
        issue_count="",
        publisher="",
        remainder="",
        series="",
        title="",
        volume="",
        volume_count="",
        year="",
        format="",
    )
    filenameinfo.update(p.expected)

    if "#" in p.filename:
        newfnames.append(pytest.param(p.filename, p.comment, filenameinfo.copy(), marks=p.xfail.complicated.with_hash))
        oldfnames.append(pytest.param(p.filename, p.comment, filenameinfo.copy(), marks=p.xfail.original.with_hash))

    newfnames.append(
        pytest.param(
            p.filename.replace("#", ""), p.comment, filenameinfo.copy(), marks=p.xfail.complicated.without_hash
        )
    )
    oldfnames.append(
        pytest.param(p.filename.replace("#", ""), p.comment, filenameinfo.copy(), marks=p.xfail.original.without_hash)
    )

file_renames = [
    Rename(
        format="{series} #{issue} ({year}) {credits}",
        move=True,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 (2007) Writer - Dara Naraghi, Penciller - Esteve Polls, Inker - Esteve Polls, Letterer - Neil Uyetake, Cover - Sam Kieth, Editor - Ted Adams.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} ({volume})({publisher})/{series} #{issue} ({year}){title+ - }{title}",
        move=True,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now (1)(IDW Publishing)/Cory Doctorow's Futuristic Tales of the Here and Now #001 (2007) - Anda's Game.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} ({volume})({publisher})/{series} #{issue} ({year}){title+volume}{title}",
        move=True,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now (1)(IDW Publishing)/Cory Doctorow's Futuristic Tales of the Here and Now #001 (2007)1Anda's Game.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} ({volume})({publisher})/{series} #{issue} ({year}){title+ - }{title}",
        move=True,
        move_only=False,
        smart_cleanup=False,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now (1)(IDW Publishing)/Cory Doctorow's Futuristic Tales of the Here and Now #001 (2007) - Anda's Game.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="#{issue} {series}: {price} ({year}) [{issue_id}]",
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="#001 Cory Doctorow's Futuristic Tales of the Here and Now (2007) [140529].cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="#{issue} {series}: {price} ({year}) [{issue_id}]",
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="linux",
        expected="#001 Cory Doctorow's Futuristic Tales of the Here and Now (2007) [140529].cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year}) [{issue_id}] (digital) ({price}) {price} test",
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007) [140529] (digital) test.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year}) [{issue_id}] (digital) - ({price}) - {price} test",
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007) [140529] (digital) test.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year}) [{issue_id}] {price} test",
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007) [140529] test.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year}){price+ - }{price}",
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year}) ({price!c})",  # conversion on None
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{country[0]} {price} {year}",  # Indexing a None value. This is now an invalid format users can use {country!0}
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="{country[0]} 2007.cbz",
        exception=does_not_raise(),
        warnings=[
            "You appear to be trying to get an item from a list instead of {story_arc[2]} use {story_arc!2}",
        ],
    ),
    Rename(
        format="{series!c} {price} {year}",  # Capitalize
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory doctorow's futuristic tales of the here and now 2007.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series!t} {price} {year}",  # Title Case
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow'S Futuristic Tales Of The Here And Now 2007.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series!S} {price} {year}",  # Swap Case
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="cORY dOCTOROW'S fUTURISTIC tALES OF THE hERE AND nOW 2007.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title!l} {price} {year}",  # Lowercase
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="anda's game 2007.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title!u} {price} {year}",  # Upper Case
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="ANDA'S GAME 2007.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title} {price} {year+}",  # Empty alternate value
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Anda's Game.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title} {price} {year+year!u}",  # Alternate value Upper Case
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Anda's Game YEAR.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title} {price} {year+year}",  # Alternate Value
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Anda's Game year.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title} {price-0} {year}",  # Default value
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Anda's Game 0 2007.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title} {price+0} {year}",  # Alternate Value
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Anda's Game 2007.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year}) ({price})",  # price should be none
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} {volume:02} ({year})",  # Ensure format specifier works
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game 01 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year})({price})",  # price should be none, test no  space between ')('
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year})  ({price})",  # price should be none, test double space ')  ('
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} ({year})",
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title} {web_link}",  # Ensure colon is replaced in metadata
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Anda's Game https---comicvine.gamespot.com-cory-doctorows-futuristic-tales-of-the-here-and-no-4000-140529-.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title} {web_link}",  # Ensure slashes are replaced in metadata on linux/macos
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="Linux",
        expected="Anda's Game https:--comicvine.gamespot.com-cory-doctorows-futuristic-tales-of-the-here-and-no-4000-140529-.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{title} {web_links!j}",  # Test that join forces str conversion
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="Linux",
        expected="Anda's Game https:--comicvine.gamespot.com-cory-doctorows-futuristic-tales-of-the-here-and-no-4000-140529-.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series}:{title} #{issue} ({year})",  # on windows the ':' is replaced
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now-Anda's Game #001 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series}: {title} #{issue} ({year})",  # on windows the ':' is replaced
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now - Anda's Game #001 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series}: {title} #{issue} ({year})",  # on linux the ':' is preserved
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="Linux",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now: Anda's Game #001 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{publisher}/  {series} #{issue} - {title} ({year})",  # leading whitespace is removed when moving
        move=True,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="IDW Publishing/Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{publisher}/  {series} #{issue} - {title} ({year})",  # leading whitespace is removed when only renaming
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format=r"{publisher}\  {series} #{issue} - {title} ({year})",  # backslashes separate directories
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="Linux",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #  {issue} - {title} ({year})",  # double spaces are reduced to one
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now # 001 - Anda's Game (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {locations!j} ({year})",
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - lonely cottage (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} #{issue} - {title} - {WriteR}, {EDITOR} ({year})",  # fields are case in-sensitive
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 - Anda's Game - Dara Naraghi, Ted Adams (2007).cbz",
        exception=does_not_raise(),
        warnings=[
            "Please use {credit_writer} instead of {writer}",
            "Please use {credit_editor} instead of {editor}",
        ],
    ),
    Rename(
        format="{series} v{price} #{issue} ({year})",  # Remove previous text if value is ""
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} {price} #{issue} ({year})",  # Ensure that a single space remains
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now #001 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} - {title}{price} #{issue} ({year})",  # Ensure removal before None values only impacts literal text
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now - Anda's Game #001 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} - {title} {test} #{issue} ({year})",  # Test non-existent key
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now - Anda's Game {test} #001 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} - {title} #{issue} ({year} {price})",  # Test null value in parenthesis with a non-null value
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now - Anda's Game #001 (2007).cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} - {title} #{issue} (of {price})",  # null value with literal text in parenthesis
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now - Anda's Game #001.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
    Rename(
        format="{series} - {title} {1} #{issue} ({year})",  # Test numeric key
        move=False,
        move_only=False,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now - Anda's Game {test} #001 (2007).cbz",
        exception=pytest.raises(ValueError),
        warnings=[],
    ),
    Rename(
        format="{series} - {title} #{issue} ({year})",
        move=False,
        move_only=True,
        smart_cleanup=True,
        platform="universal",
        expected="Cory Doctorow's Futuristic Tales of the Here and Now - Anda's Game #001 (2007)/cory doctorow #1.cbz",
        exception=does_not_raise(),
        warnings=[],
    ),
]

folder_names = [
    (None, lambda: pathlib.Path(str(cbz_path)).parent.absolute()),
    ("", lambda: pathlib.Path(os.getcwd())),
    ("test", lambda: (pathlib.Path(os.getcwd()) / "test")),
    (pathlib.Path(os.getcwd()) / "test", lambda: pathlib.Path(os.getcwd()) / "test"),
]
