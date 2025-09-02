from ag_draftking_utils.util import time_function
import pandas as pd
import numpy as np
import time
import os

INCL_CURR_SUFFIX = 'incl_curr'


def get_trailing_window_incl_current_column_names(trail_window_cols):
    return [f'{col}{INCL_CURR_SUFFIX}' for col in trail_window_cols]


def fix_trailing_stats_for_benched_players(full_roster_df, trail_window_cols, groupby_cols):
    """
    NOTE: USE WITH CAUTION -- if the player actually played in the game, and the trailing window stat 
    is NOT null, then this will cause leakage. generally this is designed to be used in tandom with 
    the create_trailing_games_features function.

    When we get the trailing stats data we excluded players that were benched/inactive on a given date.
    These players happened to not play, but they should have accurate trailing stats, regardless because
    we might think they should play in the simulation.
    This method takes the last trailing stat number for a given player and forward-fills it.
     
    :param full_roster_df: dataframe containing all players, regardless of whether they played or not
    - game_pk
    - grouping_columns
    - trailing window columns
    - trailing window columns incl_current
    :param trail_window_cols: List[str]: list of columns that have already calculated the trailing window for
    :param extra_cols: List[str]: list of additional columns desired to keep from the full dataframe
    :return: DataFrame (removes the incl_current_columns)
    - game_pk
    - grouping_columns
    - all trailing window stats
    - all extra columns
    """
    trail_window_incl_current_cols = get_trailing_window_incl_current_column_names(trail_window_cols)
    full_roster_df[trail_window_incl_current_cols] = full_roster_df.groupby(groupby_cols)[
        trail_window_incl_current_cols].fillna(method='ffill')
    for col, incl_curr_col in zip(trail_window_cols, trail_window_incl_current_cols):
        full_roster_df[col] = full_roster_df[col].fillna(full_roster_df[incl_curr_col])
    return full_roster_df.drop(columns=trail_window_incl_current_cols)


def remove_peeking(df, aggregate_columns, features_to_fix, ranking_column, peeking_column='date'):
    """
    When using play-by-play and trivially calculating the trailing N features, you run into situations
    where you're using trailing stats calculated from the same game (which you wouldn't know at inference)
    time. The idea here is to make the data such that you are only using the last piece of information 
    that you actually know at inference time.

    NOTE: must be pre-sorted ascending... 

    Inputs:
        df: pd.DataFrame - the data that you need to fix
        aggregate_columns: List[str] - the grouping that you are using. 
        features_to_fix: List[str] - the features which may have some peeking.
        ranking_column: str - this is how you determine the "first" observation.
        peeking_column: str - the granularity level that defines peeking.
    Outputs:
        pd.DataFrame -- the fixed dataframe
    """

    df['zzztmpRank'] = df.groupby(aggregate_columns+[peeking_column])[ranking_column].rank(method='min')

    nulls = np.full((df.shape[0], len(features_to_fix)), np.nan)
    # the idea here is to not use the trailing N at-bats for the 2nd, 3rd, ... Nth PA
    # because we don't yet know these values at the start of the game.
    df[features_to_fix] = np.where(
        (df['zzztmpRank'].to_numpy() == 1)[:, None],
        df[features_to_fix],
        nulls
    )
    # replace the now-null values with the 
    df[features_to_fix] = df.groupby(aggregate_columns)[features_to_fix].ffill()
    return df.drop(columns='zzztmpRank')


def _join_window_df_with_original_df(window_df, original_df, rename_cols, groupby_cols):
    """Helper function to be utilized for create_trailing_game_features."""
    level = len(groupby_cols)
    # this operation forces the index to return to its original value before the transform
    # so that it can be joined to the original dataframe correctly
    window_df = window_df.reset_index().set_index(f'level_{level}').drop(columns=groupby_cols)

    # the rolling stat columns are presently just named the actual stat, so rename them
    # to Trailing Window to reflect that they are trailing stats
    window_df = window_df.rename(columns=rename_cols)

    # rejoin with the original dataframe
    window_df = original_df.merge(window_df, left_index=True, right_index=True)

    assert window_df.shape[0] == original_df.shape[0]
    return window_df


def create_trailing_game_features_empirical_bayes(window_size, df, feature_columns, *rolling_window_function_args,
                                  groupby_cols=['player_id'], min_period=1, rename_cols={}, 
                                  missing_default_value=0, population_mean=0, tuning_strength=100, **rolling_window_function_kwargs):
    """
    Calculate the empirical bayes trailing game features equivalents.
    Formulation: 
    w = count / (tuning_strength + count)
    feature = individual_mean * w + (1-w) * population_mean

    The idea here is that low-sample size players get shrunk to a mean more aggressively.
    """
    
    rename_cols_ct = {key: f'{val}|count' for key, val in rename_cols.items()}

    df = create_trailing_game_features(
            window_size, df, feature_columns, groupby_cols=groupby_cols,
            rename_cols=rename_cols, rolling_window_function=np.mean, 
            missing_default_value=population_mean)

    df = create_trailing_game_features(
        window_size, df, feature_columns, groupby_cols=groupby_cols,
        rename_cols=rename_cols_ct,
        rolling_window_function=np.size, 
        missing_default_value=0)  # if missing, the count is 0

    for col in rename_cols.values():
        for suffix in ['', INCL_CURR_SUFFIX]:
            w = df[f'{col}|count{suffix}'] / (df[f'{col}|count{suffix}'] + tuning_strength)
            df[f'{col}{suffix}'] = w * df[f'{col}{suffix}'] + (1-w) * population_mean

    count_incl_curr_columns = get_trailing_window_incl_current_column_names(rename_cols_ct.values())
    count_columns = list(rename_cols_ct.values())
    # don't need the counts, so just drop them. 
    return df.drop(columns=count_incl_curr_columns+count_columns)


def create_trailing_game_features(window_size, df, features, *rolling_window_function_args,
                                  groupby_cols=['player_id'], min_period=1,
                                  rename_cols={}, rolling_window_function=np.mean, missing_default_value=-999,
                                  enable_missing_data_check=True,
                                  **rolling_window_function_kwargs):
    """
    Inputs:
        features: List[str]: list of desired features to get window on (i.e. PTS_PAINT, SPD, SCREEN_AST_PTS, etc.)
        window_size: int: do you want trailing 5 games, trailing 10 games, etc...
        df: pd.DataFrame: inputs containing
            - groupby_col1 
            - groupby_col2
            - groupby_colN
            - window_stats (must be numeric)
            - other_stats
        groupby_cols: List[str]: provide a list of columns to groupby
        enable_missing_data_check: bool - typically expect there to be a single missing value per grouping with 
            game-level data (so keep the default = True), but sometimes there can be multiple missing values
            per grouping (i.e. when using pitch-level data and creating stats like "swing / pitch_in_zone" because
            not every pitch is in the zone, so the denominator can be null multiple times.) 
        missing_default_value: float: For observations that are missing, automatically fill the missing values 
            with this value.
    Outputs:
        pd.DataFrame: contains
            - groupby_col1 
            - groupby_col2
            - groupby_colN
            - Trailing<window_size><window_stat>
            - window_stats
            - other_stats
    """

    # get the rolling average
    window_df = df.groupby(groupby_cols)[features] \
                  .rolling(window=window_size, min_periods=min_period).aggregate(
        rolling_window_function, *rolling_window_function_args, **rolling_window_function_kwargs
    )

    # need to shift by 1 to exclude the current game
    window_df_ex_current = window_df.groupby(groupby_cols).shift(1)

    if enable_missing_data_check:
        # check for each column that there's exactly 1 missing entry per player.
        # For some stats this will not be the case as they may not have existed
        # prior to a given year (i.e. if boxouts began getting recorded in 2017
        # then, 2015 boxout stats will show up as null)
        n_players = df.groupby(groupby_cols).head(1).shape[0]
        missing_data = window_df_ex_current[features].isna().sum()
        assert (missing_data == n_players).mean() > 0.5

    # ensure that a player's very first opportunity he has a value of "missing_default_value"..
    # This prevents peaking from occurring in the "not ex_current" columns.
    # if fillna to 0, then it creates a confound with trailing averages that are organically 0. 
    window_df_ex_current[features] = window_df_ex_current.fillna(missing_default_value)

    final = _join_window_df_with_original_df(window_df_ex_current, df, rename_cols, groupby_cols)

    # note that incl_current is used a method of handling forward-fill for OUT players, and is later discarded
    # for players that played on a given date, therefore preventing leakage.
    # For example, in the sequence for Jericho
    # Sims (1630579) for Trailing 5 BLKs on 2022-01-20, his trailing 5 game blks (ignoring games he was out)
    # is 0.2, and on 2022-01-17, his trailing 5-game-blks is 0.4. The code is setup to filter
    # out players that did not play on a date (so they do not unfairly negatively affect
    # their trailing stats), but these players still need some trailing game stat on these dates in spite of
    # them not playing, because their trailing game stats may have some implications for teammates. To
    # deal with this, the "full dataframe" is joined with the "played dataframe", and the trailing game averages
    # from the played dataframe are forward-filled onto the "full dataframe". Because of this, without
    # "incl_current", the "trailing 5 game blks" for 2022-01-20 uses the value from 2022-01-17, which is 0.4. When
    # we use "incl_current", the forward-fill is instead 0.2, because the window of games shifts from 2021-12-23 to
    # 2022-01-17, instead of 2021-12-08 to 2022-01-12.
    #
    # 2021-12-08:   1
    # 2021-12-23:   0
    # 2022-01-08:   0
    # 2022-01-10:   1
    # 2022-01-12:   0
    # 2022-01-15: out
    # 2022-01-17:   0
    # 2022-01-18: out
    # 2022-01-20: out
    rename_incl_current_cols = dict(zip(rename_cols.keys(), get_trailing_window_incl_current_column_names(
        rename_cols.values())))
    final = _join_window_df_with_original_df(window_df, final, rename_incl_current_cols,
                                            groupby_cols)
    return final