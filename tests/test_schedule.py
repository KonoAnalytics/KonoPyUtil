import os

import pandas as pd
import pytest

import KonoPyUtil
from KonoPyUtil.soccer.schedule import schedule_event

WORKBOOK = os.path.join(
    os.path.dirname(KonoPyUtil.__file__), "data", "Challenge_19th_Annual_Presidents_Day_Invitational.xlsx"
)

pytestmark = pytest.mark.skipif(not os.path.exists(WORKBOOK), reason="schedule workbook not present")


@pytest.fixture(scope="module")
def schedule():
    # schedule_event prints the sheet names; keep test output clean
    import contextlib
    import io

    with contextlib.redirect_stdout(io.StringIO()):
        return schedule_event(WORKBOOK, seed=42)


def test_returns_games_fields_and_availability(schedule):
    assert isinstance(schedule, tuple)
    assert len(schedule) == 3
    assert all(isinstance(df, pd.DataFrame) for df in schedule)


def test_output_shapes_match_reference(schedule):
    games, fields, availability = schedule
    assert games.shape == (150, 16)
    assert fields.shape == (16, 4)
    assert availability.shape == (32, 7)


def test_same_seed_gives_identical_games(schedule):
    import contextlib
    import io

    with contextlib.redirect_stdout(io.StringIO()):
        again = schedule_event(WORKBOOK, seed=42)
    pd.testing.assert_frame_equal(schedule[0], again[0])


def test_field_ids_are_sequential(schedule):
    fields = schedule[1]
    assert list(fields["field_id"]) == list(range(1, len(fields) + 1))
