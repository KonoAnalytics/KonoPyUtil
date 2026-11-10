import pandas as pd
import pytest

from KonoPyUtil.soccer import get_elo_match, get_elo_season, validate_elo_df

# ---- get_elo_match ----------------------------------------------------------


def test_equal_ratings_win_gives_symmetric_gain():
    assert get_elo_match(1500, 1500, 30, 1) == pytest.approx((1515, 1485))


def test_equal_ratings_tie_gives_no_change():
    assert get_elo_match(1500, 1500, 30, 0) == pytest.approx((1500, 1500))


def test_win_transfers_points_between_players():
    # ratings are conserved across a match
    new_a, new_b = get_elo_match(1500, 1600, 30, 1, mov=2)
    assert new_a + new_b == pytest.approx(3100)


def test_upset_gains_more_than_expected_win():
    favourite_win, _ = get_elo_match(1600, 1500, 30, 1)
    underdog_win, _ = get_elo_match(1500, 1600, 30, 1)
    assert underdog_win - 1500 > favourite_win - 1600


def test_margin_of_victory_increases_gain():
    small_mov, _ = get_elo_match(1500, 1500, 30, 1, mov=1)
    large_mov, _ = get_elo_match(1500, 1500, 30, 1, mov=5)
    assert large_mov > small_mov


def test_loss_for_player_a_reduces_rating():
    new_a, new_b = get_elo_match(1500, 1500, 30, -1)
    assert new_a < 1500 < new_b


# ---- validate_elo_df --------------------------------------------------------


def test_validate_accepts_good_frame(elo_games):
    result = validate_elo_df(elo_games.copy())
    assert result == {"success": True, "message": ""}


def test_validate_reports_missing_columns(elo_games):
    result = validate_elo_df(elo_games.drop(columns=["away_score"]))
    assert result["success"] is False
    assert "away_score" in result["message"]


def test_validate_rejects_non_integer_scores(elo_games):
    elo_games["home_score"] = ["x", "1", "2", "3"]
    result = validate_elo_df(elo_games)
    assert result["success"] is False
    assert "home_score" in result["message"]


def test_validate_rejects_empty_team_name(elo_games):
    elo_games.loc[1, "home_name"] = ""
    result = validate_elo_df(elo_games)
    assert result["success"] is False
    assert "home_name" in result["message"]


def test_validate_rejects_null_match_id(elo_games):
    elo_games["match"] = elo_games["match"].astype(object)
    elo_games.loc[0, "match"] = None
    result = validate_elo_df(elo_games)
    assert result["success"] is False
    assert "match" in result["message"]


# ---- get_elo_season ---------------------------------------------------------


def test_season_returns_elo_and_ranking_frames(elo_games):
    result = get_elo_season(elo_games.copy())
    assert set(result) == {"df_elo", "df_rankings"}
    assert len(result["df_elo"]) == len(elo_games)
    assert set(result["df_rankings"]["Team"]) == {"A", "B", "C"}


def test_season_ratings_are_conserved(elo_games):
    result = get_elo_season(elo_games.copy(), use_mov=True)
    assert result["df_rankings"]["Final ELO"].sum() == pytest.approx(3000)


def test_season_ranking_is_sorted_descending(elo_games):
    rankings = get_elo_season(elo_games.copy())["df_rankings"]
    assert list(rankings["Final ELO"]) == sorted(rankings["Final ELO"], reverse=True)
    assert list(rankings["Rank"]) == [1, 2, 3]


def test_season_matches_reference_values(elo_games):
    # values produced by the library on pandas 2.2 and pandas 3.1 (identical)
    rankings = get_elo_season(elo_games.copy(), use_mov=True, k=30)["df_rankings"]
    by_team = dict(zip(rankings["Team"], rankings["Final ELO"]))
    assert by_team["C"] == pytest.approx(1036.3594, abs=1e-3)
    assert by_team["B"] == pytest.approx(989.6028, abs=1e-3)
    assert by_team["A"] == pytest.approx(974.0378, abs=1e-3)


def test_season_without_mov_differs_from_with_mov(elo_games):
    with_mov = get_elo_season(elo_games.copy(), use_mov=True)["df_rankings"]
    without_mov = get_elo_season(elo_games.copy(), use_mov=False)["df_rankings"]
    assert not with_mov["Final ELO"].equals(without_mov["Final ELO"])


def test_season_accepts_integer_scores_without_error(elo_games):
    # regression: pandas>=3 raised "Invalid value ... for dtype 'int64'"
    result = get_elo_season(elo_games.copy())
    assert pd.api.types.is_float_dtype(result["df_elo"]["home_pre_elo"])
