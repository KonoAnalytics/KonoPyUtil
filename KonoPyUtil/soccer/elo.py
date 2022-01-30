import math
import pandas as pd

# Constructed From:
# https://www.geeksforgeeks.org/elo-rating-algorithm/
# https://www.chess.com/forum/view/general/how-are-draws-calculated-in-the-elo-system

# Function to calculate the _probability
def _probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


def get_elo_match(rating_a, rating_b, k, d, mov=None):
    """
    Returns new ELO ratings give the result of a match
    :param rating_a: Rating for player A
    :param rating_b: Rating for player B
    :param k: Constant
    :param d: 1 = Win for rating_a, 0 = Tie, -1 = Win for rating_b
    :param mov: margin of victory. None, implies not to use margin of victory in the calculation
    :return:
    """
    probability_a = _probability(rating_b, rating_a)
    probability_b = 1 - probability_a
    if mov is None:
        k_multiplier = 1.0
    else:
        k_multiplier = math.log(abs(mov) + 1)
    if d == 1:
        # Player A won
        rating_a = rating_a + k * k_multiplier * (1 - probability_a)
        rating_b = rating_b + k * k_multiplier * (0 - probability_b)
    elif d == -1:
        # Player B won
        rating_a = rating_a + k * k_multiplier * (0 - probability_a)
        rating_b = rating_b + k * k_multiplier * (1 - probability_b)
    else:
        # Tie
        rating_a = rating_a + k * k_multiplier * (0.5 - probability_a)
        rating_b = rating_b + k * k_multiplier * (0.5 - probability_b)
    return rating_a, rating_b


def _format_game_results(df):
    df = df.set_index("match")
    df["game_time"] = pd.to_datetime(df["game_time"])
    df = df.sort_values(by="game_time")
    return df


def _get_current_elo(df, team_name):

    select_records = ((df["home_name"] == team_name) | (df["away_name"] == team_name)) & (
        pd.notnull(df["home_post_elo"])
    )
    last_record = df[select_records].tail(1)
    if len(last_record):
        if last_record["home_name"].values[0] == team_name:
            return last_record["home_post_elo"].values[0]
        else:
            return last_record["away_post_elo"].values[0]
    else:
        return 1000


def _format_ranking(df, verbose=False):
    teams = list(set(df["home_name"]) | set(df["away_name"]))
    final_rank = []
    team_name = []
    for team in teams:
        final_rank.append(_get_current_elo(df, team))
        team_name.append(team)
    final_elo_column_name = "Final ELO"
    df_final = pd.DataFrame(data={"Team": team_name, final_elo_column_name: final_rank}).sort_values(
        by="Final ELO", ascending=False
    )
    df_final["rank"] = df_final[final_elo_column_name].rank(method="min", ascending=False).astype("int")
    df_final = df_final.reset_index(drop=True)
    if verbose:
        print(df_final.to_string(index=False))
    return df_final


def get_elo_season(df, use_mov=True, K=30, verbose=False):
    """
    This runs the ELO algorithm to rank all teams in a given season or tournament.  It acceepts a dataframe of game
    results. The format of this dataframe is very particular. For an example look at the copa_rayados.2021.csv file
    in this library
    >>> from KonoPyUtil import load_dataset
    >>> df = load_dataset('copa_rayados.2021.csv')

    :param df: A dataframe of results
    :param use_mov: Use margin-of-victory -- boolean
    :param K: K factor for ELO
    :param verbose: prints ranking if True
    :return: a dictionary containing two dataframes, df_elo and df_ranking
    """
    df_results = _format_game_results(df).copy()
    df_elo = df_results.copy()
    df_elo["home_pre_elo"] = 1000
    df_elo["home_post_elo"] = None
    df_elo["away_pre_elo"] = 1000
    df_elo["away_post_elo"] = None

    for index, game in df_results.iterrows():
        if game["home_score"] > game["away_score"]:
            d = 1
        if game["home_score"] < game["away_score"]:
            d = -1
        if game["home_score"] == game["away_score"]:
            d = 0

        Ra_old = _get_current_elo(df_elo, game["home_name"])
        Rb_old = _get_current_elo(df_elo, game["away_name"])
        if use_mov:
            score_delta = game["home_score"] - game["away_score"]
        else:
            score_delta = None
        Ra_new, Rb_new = get_elo_match(Ra_old, Rb_old, K, d, score_delta)
        df_elo.loc[index, "home_pre_elo"] = Ra_old
        df_elo.loc[index, "home_post_elo"] = Ra_new
        df_elo.loc[index, "away_pre_elo"] = Rb_old
        df_elo.loc[index, "away_post_elo"] = Rb_new

    df_rankings = _format_ranking(df_elo, verbose=verbose)

    return {
        "df_elo": df_elo,
        "df_rankings": df_rankings,
    }
