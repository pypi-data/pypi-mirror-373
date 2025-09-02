import numpy as np

def probability_to_american_odds(p):
    """
    Gets the fair-market American odds given a probablity
    """
    if p > 0.5:
        return 100 * p / (p-1)
    else:
        return 100/p - 100


def calculate_expected_value_vectorized(df, model_probability_col, price_col='price', bet_size=100, 
        expected_value_col='expected_value'):
    """
    :param df: DataFrame containing the model probability and prices
    :param price_col: str: column-name that contains the american odds.
    :param model_probability_col: str: column-name that contains the model probability 
    :param bet_size: float: the amount you are wagering per bet
    :param expected_value_col: str: the column-name that stores the new expected value term.

    Returns:
    - dataframe with an additional column "expected_value_col"
    """
    df['zzz_dummy'] = 1
    df['zzz_payout_if_won'] = american_odds_to_payout_vectorized(
        df, bet_size=bet_size, price_col=price_col, won_bet_col='zzz_dummy')
    df[expected_value_col] = (
        df[model_probability_col] * df['zzz_payout_if_won'] + 
        (1-df[model_probability_col]) * (-bet_size)
    )
    df = df.drop(columns=['zzz_dummy', 'zzz_payout_if_won'])
    return df


def probability_to_american_odds_vectorized(df, p_col):
    """
    Gets the fair-market American odds given a probablity
    """
    return np.where(
        df[p_col] > 0.5,
        100 * df[p_col] / (df[p_col] - 1),
        100/df[p_col] - 100
    )


def american_odds_to_breakeven_probability(ml):
    """
    Takes in the American Odds and returns the breakeven 
    probability necessary to win a bet
    :param ml - int: the moneyline (-100, -200, +110, +100, etc)
    """
    assert ml >= 100 or ml <= -100
    if ml < 0:
        return -ml / (-ml + 100)
    return 100 / (100 + ml)


def convert_given_odds_to_commision_free_odds_vectorized(df, price_col='price', commission=0.03):
    normal_payout = american_odds_to_payout_given_win_vectorized(df, price_col=price_col, bet_size=100)
    modified_payout = normal_payout * (1-commission)
    return np.where(
        modified_payout < 100,
        -100 * 100 / modified_payout,
        modified_payout
    )


def american_odds_to_payout_given_win_vectorized(df, price_col='price', bet_size=100):
    return np.where(
        df[price_col] < 0, 
        (100 / (-df[price_col])) * bet_size,
        bet_size * df[price_col] / 100
    )


def american_odds_to_payout(american_odds, did_win_bet, bet_size=100):
    """
    Determines the payout of the bet based on the win/loss and the odds.

    :param american_odds - int: the moneyline (-100, -200, +110, +100, etc)
    :param did_win_bet - bool: whether or not the bet pays-out
    :param bet_size - float: amount bet on the game
    """
    if not did_win_bet:
        return -bet_size
    if american_odds < 0:
        return (100/(-american_odds)) * bet_size
    else:
        return bet_size * american_odds/100


def american_odds_to_payout_vectorized(df, bet_size=100, price_col='price', won_bet_col='won_bet'):
    return np.where(
        df[won_bet_col].isna(),
        0,
        np.where(
            df[won_bet_col],
            np.where(
                df[price_col] < 0, 
                (100 / (-df[price_col])) * bet_size,
                bet_size*df[price_col] / 100
            ),
            -bet_size
        )
    )


def american_odds_to_breakeven_probability_vectorized(df, price_col='price'):
    odds = df[price_col]
    # Calculate the breakeven probability in a vectorized way
    return np.where(odds < 0, -odds / (-odds + 100), 100 / (100 + odds))