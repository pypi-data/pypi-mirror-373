from atikin_utils import now, parse_iso, humanize_timedelta
from datetime import timedelta

def test_now_and_parse():
    n = now()
    assert n is not None

    d = parse_iso("2020-01-01")
    assert d.year == 2020

def test_humanize():
    assert humanize_timedelta(timedelta(seconds=45)).endswith("seconds")
    assert humanize_timedelta(timedelta(days=2)).endswith("days")
