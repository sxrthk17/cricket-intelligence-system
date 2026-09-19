## make python touch data through our own code.

import pandas as pd
import numpy as np
import logging

df = pd.read_csv("datasets/real_cleaned_deliveries.csv")

def total_runs(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = ['batsman', 'batsman_runs']

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain 'batsman' and 'batsman_runs' columns."
        )

    result = df.groupby('batsman')['batsman_runs'].sum().reset_index()


    return result

def high_scorer(df, N=1): ## Updating function such that N = 1 then validate N so it is a positive integer only

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = ['batsman', 'batsman_runs'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'batsman' and 'batsman_runs' columns.")
    
    if isinstance(N, bool) or not isinstance(N, int) or N <= 0:
        raise ValueError("N must be a Positive integer onlyy!")
    batsman_and_runs = df.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).reset_index()

    batsman_and_runs = batsman_and_runs.rename(columns={'batsman_runs': 'total_runs'})
    batsman_and_runs = batsman_and_runs.head(N)
    return batsman_and_runs



def is_legal_delivery(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")
    
    req_cols = ['wide_runs', 'noball_runs'] 
    if not all(col in df.columns for col in req_cols):
            raise ValueError("The DataFrame must contain 'wide_runs' and 'noball_runs' columns.")


    legal_delivery = (df['wide_runs'] == 0) & (df['noball_runs'] == 0)
    return legal_delivery ## acting like a boolean mask here !

def total_legal_balls(df):

    if not isinstance(df, pd.DataFrame):
                raise ValueError("The passed argument must be a pandas DataFrame.")
    
    legal_delivery = is_legal_delivery(df)
    legal_delivery_count = legal_delivery.sum()
    return legal_delivery_count

def legal_balls_by_bowler(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")
    
    req_cols = ['bowler', 'ball'] 

    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'bowler' and 'ball' columns.")
    
    legal_delivery = is_legal_delivery(df)
    legal_delivery_df = df[legal_delivery]
    bowled_balls= legal_delivery_df.groupby('bowler')['ball'].count().reset_index()

    return bowled_balls

def balls_faced_by_batsman(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")
    req_cols = ['batsman', 'ball'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'batsman' and 'ball' columns.")

    legal_delivery = is_legal_delivery(df)
    legal_delivery_df = df[legal_delivery]
    faced_balls = legal_delivery_df.groupby('batsman')['ball'].count().reset_index()

    return faced_balls

def boundary_percentage(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = ['batsman', 'batsman_runs'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'batsman' and 'batsman_runs' columns.")


    total_batsman_runs = total_runs(df)
    total_batsman_runs.columns = ['batsman', 'total_runs']

    total_fours = df[df['batsman_runs'] == 4].groupby('batsman')['batsman_runs'].count().reset_index()
    total_fours.columns = ['batsman', 'total_fours']

    total_sixes = df[df['batsman_runs'] == 6].groupby('batsman')['batsman_runs'].count().reset_index()
    total_sixes.columns = ['batsman', 'total_sixes']

    boundary_df = total_batsman_runs.merge(total_fours, on='batsman', how='left')
    boundary_df = boundary_df.merge(total_sixes, on='batsman', how='left')

    boundary_df['total_fours'] = boundary_df['total_fours'].fillna(0)
    boundary_df['total_sixes'] = boundary_df['total_sixes'].fillna(0)

    boundary_df['boundary_runs'] = boundary_df['total_fours'] * 4 + boundary_df['total_sixes'] * 6

    safe_total_runs = boundary_df['total_runs'].replace(0, 1)

    boundary_df['boundary_percentage'] = np.where(
    boundary_df['total_runs'] == 0, 0, (boundary_df['boundary_runs'] / safe_total_runs) * 100)
    

    balls_faced = balls_faced_by_batsman(df)

    boundary_df =boundary_df.merge(balls_faced, on='batsman', how='left').rename(columns={'ball':'balls_faced'}) ## we use rename
    boundary_df = boundary_df.sort_values(by='boundary_percentage', ascending=False).reset_index(drop=True)
    return boundary_df[['batsman','total_runs','boundary_runs','boundary_percentage', 'balls_faced']]

def boundary_count(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = ['batsman', 'batsman_runs']

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain 'batsman' and 'batsman_runs' columns."
        )

    total_fours = (
        df[df['batsman_runs'] == 4]
        .groupby('batsman')['batsman_runs']
        .count()
        .reset_index()
    )

    total_fours.columns = ['batsman', 'total_fours']

    total_sixes = (
        df[df['batsman_runs'] == 6]
        .groupby('batsman')['batsman_runs']
        .count()
        .reset_index()
    )

    total_sixes.columns = ['batsman', 'total_sixes']

    boundary_df = total_fours.merge(
        total_sixes,
        on='batsman',
        how='outer'
    )

    boundary_df['total_fours'] = boundary_df['total_fours'].fillna(0)
    boundary_df['total_sixes'] = boundary_df['total_sixes'].fillna(0)

    boundary_df['boundary_count'] = (
        boundary_df['total_fours'] +
        boundary_df['total_sixes']
    )

    boundary_df = (
        boundary_df
        .sort_values(by='boundary_count', ascending=False)
        .reset_index(drop=True)
    )

    return boundary_df[
        ['batsman', 'total_fours', 'total_sixes', 'boundary_count']
    ]


def scoring_composition(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = ['batsman', 'batsman_runs']

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain 'batsman' and 'batsman_runs' columns."
        )

    batsman_runs = (
        df.groupby('batsman')['batsman_runs']
        .sum()
        .reset_index()
    )

    batsman_runs.columns = ['batsman', 'total_runs']

    total_ones = (
        df[df['batsman_runs'] == 1]
        .groupby('batsman')['batsman_runs']
        .count()
        .reset_index()
    )
    total_ones.columns = ['batsman', 'total_ones']

    total_doubles = (
        df[df['batsman_runs'] == 2]
        .groupby('batsman')['batsman_runs']
        .count()
        .reset_index()
    )
    total_doubles.columns = ['batsman', 'total_doubles']

    total_triples = (
        df[df['batsman_runs'] == 3]
        .groupby('batsman')['batsman_runs']
        .count()
        .reset_index()
    )
    total_triples.columns = ['batsman', 'total_triples']

    total_fours = (
        df[df['batsman_runs'] == 4]
        .groupby('batsman')['batsman_runs']
        .count()
        .reset_index()
    )
    total_fours.columns = ['batsman', 'total_fours']

    total_fives = (
        df[df['batsman_runs'] == 5]
        .groupby('batsman')['batsman_runs']
        .count()
        .reset_index()
    )
    total_fives.columns = ['batsman', 'total_fives']

    total_sixes = (
        df[df['batsman_runs'] == 6]
        .groupby('batsman')['batsman_runs']
        .count()
        .reset_index()
    )
    total_sixes.columns = ['batsman', 'total_sixes']

    score_composition_df = batsman_runs.merge(
        total_ones,
        on='batsman',
        how='left'
    )

    score_composition_df = score_composition_df.merge(
        total_doubles,
        on='batsman',
        how='left'
    )

    score_composition_df = score_composition_df.merge(
        total_triples,
        on='batsman',
        how='left'
    )

    score_composition_df = score_composition_df.merge(
        total_fours,
        on='batsman',
        how='left'
    )

    score_composition_df = score_composition_df.merge(
        total_fives,
        on='batsman',
        how='left'
    )

    score_composition_df = score_composition_df.merge(
        total_sixes,
        on='batsman',
        how='left'
    )

    count_columns = [
        'total_ones',
        'total_doubles',
        'total_triples',
        'total_fours',
        'total_fives',
        'total_sixes'
    ]

    score_composition_df[count_columns] = (
        score_composition_df[count_columns].fillna(0)
    )

    score_composition_df['single_runs'] = (
        score_composition_df['total_ones'] * 1
    )

    score_composition_df['double_runs'] = (
        score_composition_df['total_doubles'] * 2
    )

    score_composition_df['triple_runs'] = (
        score_composition_df['total_triples'] * 3
    )

    score_composition_df['four_runs'] = (
        score_composition_df['total_fours'] * 4
    )

    score_composition_df['five_runs'] = (
        score_composition_df['total_fives'] * 5
    )

    score_composition_df['six_runs'] = (
        score_composition_df['total_sixes'] * 6
    )

    safe_total_runs = (
        score_composition_df['total_runs'].replace(0, 1)
    )

    score_composition_df['single_run_percentage'] = (
        score_composition_df['single_runs']
        / safe_total_runs
    ) * 100

    score_composition_df['double_run_percentage'] = (
        score_composition_df['double_runs']
        / safe_total_runs
    ) * 100

    score_composition_df['triple_run_percentage'] = (
        score_composition_df['triple_runs']
        / safe_total_runs
    ) * 100

    score_composition_df['four_run_percentage'] = (
        score_composition_df['four_runs']
        / safe_total_runs
    ) * 100

    score_composition_df['five_run_percentage'] = (
        score_composition_df['five_runs']
        / safe_total_runs
    ) * 100

    score_composition_df['six_run_percentage'] = (
        score_composition_df['six_runs']
        / safe_total_runs
    ) * 100

    percentage_columns = [
        'single_run_percentage',
        'double_run_percentage',
        'triple_run_percentage',
        'four_run_percentage',
        'five_run_percentage',
        'six_run_percentage'
    ]

    score_composition_df.loc[
        score_composition_df['total_runs'] == 0,
        percentage_columns
    ] = 0

    return score_composition_df

def strike_rate(df):
    if not isinstance(df, pd.DataFrame):
                raise ValueError("The passed argument must be a pandas DataFrame.")
    
    req_cols = ['batsman', 'batsman_runs'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'batsman' and 'batsman_runs' columns.")


    totals = total_runs(df)

    balls_faced = balls_faced_by_batsman(df)

    strike_rate_df = totals.merge(balls_faced, on='batsman', how='left')
    safe_balls = strike_rate_df['ball'].replace(0, 1)
    strike_rate_df['strike_rate'] = (strike_rate_df['batsman_runs'] / safe_balls) * 100
    strike_rate_df.rename(columns={'ball': 'balls_faced', 'batsman_runs': 'total_runs'}, inplace=True)

    return strike_rate_df[['batsman', 'total_runs', 'balls_faced', 'strike_rate']]

def batting_average(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    
    req_cols = ['dismissal_kind', 'player_dismissed', 'batsman', 'batsman_runs'] 
    if not all(col in df.columns for col in req_cols):
            raise ValueError("The DataFrame must contain 'dismissal_kind', 'player_dismissed', 'batsman' and 'batsman_runs' columns.")
    player_dismissal_count = [
        'caught',
        'bowled',
        'run out',
        'lbw',
        'stumped',
        'caught and bowled',
        'hit wicket',
        'obstructing the field'
    ]

    legal_dismissals = df[
        df['dismissal_kind'].isin(player_dismissal_count)
    ]

    total_dismissals = (
        legal_dismissals
        .groupby('player_dismissed')['dismissal_kind']
        .count()
        .reset_index()
    )

    total_dismissals.columns = ['batsman', 'total_dismissals']

    batting_avg_df = (
        total_runs(df)
        .merge(total_dismissals, on='batsman', how='left')
    )

    batting_avg_df['total_dismissals'] = (
        batting_avg_df['total_dismissals'].fillna(0)
    )

    batting_avg_df['batting_average'] = (
        batting_avg_df['batsman_runs']
        / batting_avg_df['total_dismissals']
    )

    batting_avg_df.loc[
        batting_avg_df['total_dismissals'] == 0,
        'batting_average'
    ] = np.nan

    batting_avg_df = batting_avg_df.rename(
        columns={'batsman_runs': 'total_runs'}
    )

    return batting_avg_df[
        ['batsman', 'total_runs', 'total_dismissals', 'batting_average']
    ]

def wickets_by_bowler(df):

    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
        
    req_cols = ['bowler', 'dismissal_kind'] 
    if not all(col in df.columns for col in req_cols):
                raise ValueError("The DataFrame must contain 'bowler' and 'dismissal_kind' columns.")

    bowler_credited_wickets_filter =[
            'caught',
            'bowled',
            'lbw',
            'stumped',
            'caught and bowled',
            'hit wicket'
        ]

    bowler_credited_wickets = df[
            df['dismissal_kind'].isin(bowler_credited_wickets_filter)
        ]

    bowler_wickets = bowler_credited_wickets.groupby('bowler')['dismissal_kind'].count().reset_index()
    bowler_wickets = bowler_wickets.rename(columns={'dismissal_kind':"total_wickets"})
    return bowler_wickets

def runs_conceded_by_bowler(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
        
    req_cols = ['batsman_runs','wide_runs','noball_runs'] 
    if not all(col in df.columns for col in req_cols):
                raise ValueError("The DataFrame must contain 'batsman_runs','wide_runs' and 'noball_runs' columns.")
    
    runs_conceded = df.groupby('bowler')[['batsman_runs', 'wide_runs', 'noball_runs']].sum().reset_index()
    runs_conceded['runs_conceded'] = runs_conceded['batsman_runs'] + runs_conceded['wide_runs'] + runs_conceded['noball_runs']


    return runs_conceded[['bowler', 'runs_conceded']]

def overs_from_legal_balls(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")
        
    req_cols = ['bowler', 'ball'] 
    if not all(col in df.columns for col in req_cols):
            raise ValueError("The DataFrame must contain 'bowler' and 'ball' columns.")
    legal_delivery = is_legal_delivery(df)

    legal_ball_df = df[legal_delivery]

    legal_ball_df = legal_ball_df.groupby('bowler')['ball'].count().reset_index()
    legal_ball_df.columns = ['bowler','total_legal_balls']

    legal_ball_df['full_overs'] = legal_ball_df['total_legal_balls'] // 6
    legal_ball_df['remaining_balls'] = legal_ball_df['total_legal_balls'] % 6


    return legal_ball_df

def economy_rate(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    
    runs_conceded_df = runs_conceded_by_bowler(df)
    legal_balls_df = overs_from_legal_balls(df)

    economy_rate_df = runs_conceded_df.merge(legal_balls_df, on='bowler', how='left')

    safe_legal_balls = (economy_rate_df['total_legal_balls'].replace(0, 1))

    economy_rate_df['economy_rate'] = (economy_rate_df['runs_conceded'] * 6) / safe_legal_balls

    

    return economy_rate_df[['bowler', 'runs_conceded', 'total_legal_balls', 'economy_rate']]

def bowling_average(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    wickets_taken = wickets_by_bowler(df)

    runs_conceded = runs_conceded_by_bowler(df)

    bowling_avg_df = runs_conceded.merge(wickets_taken, on='bowler', how='left')

    safe_wickets = bowling_avg_df['total_wickets'].replace(0,np.nan)

    bowling_avg_df['bowling_average'] = bowling_avg_df['runs_conceded'] / safe_wickets


    return bowling_avg_df

def total_dismissals_by_batsman(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = ['dismissal_kind', 'player_dismissed']

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain 'dismissal_kind' and 'player_dismissed' columns."
        )

    player_dismissal_count = [
        'caught',
        'bowled',
        'run out',
        'lbw',
        'stumped',
        'caught and bowled',
        'hit wicket',
        'obstructing the field'
    ]

    legal_dismissals = df[
        df['dismissal_kind'].isin(player_dismissal_count)
    ]

    total_dismissals = (
        legal_dismissals
        .groupby('player_dismissed')['dismissal_kind']
        .count()
        .reset_index()
    )

    total_dismissals.columns = [
        'batsman',
        'total_dismissals'
    ]

    return total_dismissals

def bowling_strike_rate(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    legal_balls_df = legal_balls_by_bowler(df)

    bowler_wkts_df = wickets_by_bowler(df)

    bowling_sr_df = legal_balls_df.merge(bowler_wkts_df, on='bowler', how='left')

    safe_wickets = bowling_sr_df['total_wickets'].replace(0, np.nan)
    bowling_sr_df = bowling_sr_df.rename(columns={"ball":"total_legal_balls"})

    bowling_sr_df['bowling_strike_rate'] = bowling_sr_df['total_legal_balls'] / safe_wickets

    return bowling_sr_df

def dot_balls_by_bowler(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    ## add here
    req_cols = ['bowler', 'ball','batsman_runs', 'bye_runs', 'legbye_runs'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain the required columns.")
    dot_balls_filter = (is_legal_delivery(df)) & (df['batsman_runs'] == 0) & (df['bye_runs'] == 0) & (df['legbye_runs'] == 0)

    dot_balls_df = df[dot_balls_filter]
    dot_balls = dot_balls_df.groupby('bowler')['ball'].count().reset_index()
    dot_balls = dot_balls.rename(columns={'ball':'dot_balls'})

    return dot_balls

def dot_ball_percentage_by_bowler(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    dot_balls_df = dot_balls_by_bowler(df)

    legal_ball_df = legal_balls_by_bowler(df)

    dot_ball_percentage_by_bowler_df = dot_balls_df.merge(legal_ball_df, on='bowler', how='left')
    dot_ball_percentage_by_bowler_df = dot_ball_percentage_by_bowler_df.rename(columns={'ball':'total_legal_balls'})

    safe_legal_balls = dot_ball_percentage_by_bowler_df['total_legal_balls'].replace(0, np.nan)

    dot_ball_percentage_by_bowler_df['dot_ball_percentage'] = (
         dot_ball_percentage_by_bowler_df['dot_balls'] / safe_legal_balls) * 100

    

    return dot_ball_percentage_by_bowler_df

def four_runs_conceded_by_bowler(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
## add here
    req_cols = ['bowler', 'batsman_runs'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'bowler' and 'batsman_runs' columns.")
    four_conceded= df[df['batsman_runs']==4]

    four_conceded_df = four_conceded.groupby('bowler')['batsman_runs'].count().reset_index()

    four_conceded_df = four_conceded_df.rename(
    columns={'batsman_runs': 'four_count'})

    four_conceded_df['four_runs_conceded'] = four_conceded_df['four_count'] * 4

    return four_conceded_df[['bowler', 'four_runs_conceded']]

def six_runs_conceded_by_bowler(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
## add here
    req_cols = ['bowler', 'batsman_runs'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'bowler' and 'batsman_runs' columns.")
    
    six_conceded= df[df['batsman_runs']==6]

    six_conceded_df = six_conceded.groupby('bowler')['batsman_runs'].count().reset_index()

    six_conceded_df = six_conceded_df.rename(
    columns={'batsman_runs': 'six_count'})

    six_conceded_df['six_runs_conceded'] = six_conceded_df['six_count'] * 6

    return six_conceded_df[['bowler', 'six_runs_conceded']]

def wides_by_bowler(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    ## add here
    req_cols = ['bowler', 'wide_runs'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'wide_runs' columns.")
    wide_balls_df = df[df['wide_runs'] > 0]

    wide_balls_count = wide_balls_df.groupby('bowler')['wide_runs'].count().reset_index()

    wide_balls_count = wide_balls_count.rename(columns={'wide_runs':'wide_balls'})

    return wide_balls_count

def no_ball_by_bowler(df): 
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    #add here
    req_cols = ['bowler', 'noball_runs'] 
    if not all(col in df.columns for col in req_cols):
        raise ValueError("The DataFrame must contain 'noball_runs' columns.")
    no_balls_df = df[df['noball_runs'] > 0]

    no_ball_count = no_balls_df.groupby('bowler')['noball_runs'].count().reset_index()

    no_ball_count = no_ball_count.rename(columns={'noball_runs':'noball_count'})

    return no_ball_count

def bowler_profile(df):
    if not isinstance(df, pd.DataFrame):
            raise ValueError("The passed argument must be a pandas DataFrame.")
    
    legal_balls = legal_balls_by_bowler(df).rename(
        columns={'ball': 'total_legal_balls'})[['bowler', 'total_legal_balls']]

    overs = overs_from_legal_balls(df)[
        ['bowler', 'full_overs', 'remaining_balls']
    ]

    runs_conceded = runs_conceded_by_bowler(df)[
        ['bowler', 'runs_conceded']
    ]

    total_wickets = wickets_by_bowler(df).rename(
        columns={'dismissal_kind': 'total_wickets'}
    )[[
        'bowler', 'total_wickets'
    ]]

    economy_ = economy_rate(df)[
        ['bowler', 'economy_rate']
    ]

    bowling_avg = bowling_average(df)[
        ['bowler', 'bowling_average']
    ]

    bowl_strike_rate = bowling_strike_rate(df)[
        ['bowler', 'bowling_strike_rate']
    ]

    dot_balls = dot_balls_by_bowler(df)[
        ['bowler', 'dot_balls']
    ]

    dot_balls_percentage = dot_ball_percentage_by_bowler(df)[
        ['bowler', 'dot_ball_percentage']
    ]

    four_runs_conceded = four_runs_conceded_by_bowler(df)[
        ['bowler', 'four_runs_conceded']
    ]

    six_runs_conceded = six_runs_conceded_by_bowler(df)[
        ['bowler', 'six_runs_conceded']
    ]

    wide_balls = wides_by_bowler(df)[
        ['bowler', 'wide_balls']
    ]

    noballs = no_ball_by_bowler(df)[
        ['bowler', 'noball_count']
    ]

    profile = legal_balls

    profile = profile.merge(overs, on='bowler', how='left')
    profile = profile.merge(runs_conceded, on='bowler', how='left')
    profile = profile.merge(total_wickets, on='bowler', how='left')
    profile = profile.merge(economy_, on='bowler', how='left')
    profile = profile.merge(bowling_avg, on='bowler', how='left')
    profile = profile.merge(bowl_strike_rate, on='bowler', how='left')
    profile = profile.merge(dot_balls, on='bowler', how='left')
    profile = profile.merge(dot_balls_percentage, on='bowler', how='left')
    profile = profile.merge(four_runs_conceded, on='bowler', how='left')
    profile = profile.merge(six_runs_conceded, on='bowler', how='left')
    profile = profile.merge(wide_balls, on='bowler', how='left')
    profile = profile.merge(noballs, on='bowler', how='left')

    count_columns = [
    'dot_balls',
    'four_runs_conceded',
    'six_runs_conceded',
    'wide_balls',
    'noball_count'
    ]
    profile[count_columns] = profile[count_columns].fillna(0)

    return profile





def batsman_profile(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("the passed argument must be a pandas DataFrame")

    total_runs_batsman = total_runs(df).rename(columns={'batsman_runs':'total_runs'})[['batsman', 'total_runs']]

    balls_faced = balls_faced_by_batsman(df).rename(columns={'ball':'faced_balls'})[['batsman', 'faced_balls']]

    sr_df = strike_rate(df)[['batsman', 'strike_rate']]

    dismissal_df = total_dismissals_by_batsman(df)[['batsman', 'total_dismissals']]

    avg_df = batting_average(df)[['batsman', 'batting_average']]

    boundary_runs_percents = boundary_percentage(df)[['batsman', 'boundary_runs', 'boundary_percentage']]

    scoring_comp = scoring_composition(df)[[
    'batsman',
    'single_runs',
    'double_runs',
    'triple_runs',
    'four_runs',
    'six_runs',
    'single_run_percentage',
    'double_run_percentage',
    'triple_run_percentage',
    'four_run_percentage',
    'six_run_percentage']]

    ## let us merge baby

    profile = total_runs_batsman

    profile = profile.merge(balls_faced, on='batsman', how='left')
    profile = profile.merge(sr_df, on='batsman',how='left')
    profile = profile.merge(dismissal_df, on='batsman', how='left')
    profile = profile.merge(avg_df, on='batsman', how='left')
    profile = profile.merge(boundary_runs_percents, on='batsman', how='left')
    profile =profile.merge(scoring_comp, on='batsman', how='left')

    return profile




# ============================================================
# MATCH LAYERS
# ============================================================

def innings_total_runs(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = [
        'match_id',
        'inning',
        'batting_team',
        'total_runs'
    ]

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain "
            "'match_id', 'inning', 'batting_team', 'total_runs' columns."
        )

    inning_runs_df = (
        df.groupby(
            ['match_id', 'inning', 'batting_team']
        )['total_runs']
        .sum()
        .reset_index()
    )

    return inning_runs_df


def team_wickets_lost(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = [
        'match_id',
        'inning',
        'batting_team',
        'player_dismissed'
    ]

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain "
            "'match_id', 'inning', 'batting_team', "
            "'player_dismissed' columns."
        )

    team_wkts_df = (
        df[df['player_dismissed'] != 'not out']
        .groupby(
            ['match_id', 'inning', 'batting_team']
        )['player_dismissed']
        .count()
        .reset_index()
    )

    team_wkts_df = team_wkts_df.rename(
        columns={'player_dismissed': 'wickets_lost'}
    )

    return team_wkts_df


def team_run_rate(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = [
        'match_id',
        'inning',
        'batting_team',
        'ball',
        'total_runs'
    ]

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain "
            "'match_id', 'inning', 'batting_team', "
            "'ball', 'total_runs' columns."
        )

    legal_ball_filter = is_legal_delivery(df)

    legal_delivery_df = df[legal_ball_filter]

    legal_ball_count_per_inning = (
        legal_delivery_df
        .groupby(
            ['match_id', 'inning', 'batting_team']
        )['ball']
        .count()
        .reset_index()
    )

    team_run_df = innings_total_runs(df)

    run_rate_df = legal_ball_count_per_inning.merge(
        team_run_df,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    safe_legal_balls = run_rate_df['ball'].replace(0, np.nan)

    run_rate_df['run_rate'] = (
        run_rate_df['total_runs'] * 6
    ) / safe_legal_balls

    run_rate_df = run_rate_df.rename(
        columns={'ball': 'legal_balls'}
    )

    return run_rate_df


def team_boundary_runs(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = [
        'match_id',
        'inning',
        'batting_team',
        'batsman_runs'
    ]

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain "
            "'match_id', 'inning', 'batting_team', "
            "'batsman_runs' columns."
        )

    fours = (
        df[df['batsman_runs'] == 4]
        .groupby(
            ['match_id', 'inning', 'batting_team']
        )['batsman_runs']
        .count()
        .reset_index()
    )

    six = (
        df[df['batsman_runs'] == 6]
        .groupby(
            ['match_id', 'inning', 'batting_team']
        )['batsman_runs']
        .count()
        .reset_index()
    )

    fours.columns = [
        'match_id',
        'inning',
        'batting_team',
        'total_fours'
    ]

    six.columns = [
        'match_id',
        'inning',
        'batting_team',
        'total_sixes'
    ]

    boundary_runs = fours.merge(
        six,
        on=['match_id', 'inning', 'batting_team'],
        how='outer'
    )

    boundary_runs['total_fours'] = (
        boundary_runs['total_fours'].fillna(0)
    )

    boundary_runs['total_sixes'] = (
        boundary_runs['total_sixes'].fillna(0)
    )

    boundary_runs['boundary_runs'] = (
        boundary_runs['total_fours'] * 4
        + boundary_runs['total_sixes'] * 6
    )

    return boundary_runs


def team_boundary_percentage(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = [
        'match_id',
        'inning',
        'batting_team',
        'total_runs'
    ]

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain "
            "'match_id', 'inning', 'batting_team', "
            "'total_runs' columns."
        )

    boundary_runs = team_boundary_runs(df)

    team_total_runs = innings_total_runs(df)

    boundary_prcnt_df = team_total_runs.merge(
        boundary_runs,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    # No fours/sixes means zero boundary runs
    boundary_prcnt_df['boundary_runs'] = (
        boundary_prcnt_df['boundary_runs'].fillna(0)
    )

    safe_total_runs = (
        boundary_prcnt_df['total_runs'].replace(0, np.nan)
    )

    boundary_prcnt_df['boundary_percentage'] = (
        boundary_prcnt_df['boundary_runs']
        / safe_total_runs
    ) * 100

    return boundary_prcnt_df


def powerplay_runs(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = [
        'match_id',
        'inning',
        'batting_team',
        'total_runs',
        'over'
    ]

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain "
            "'match_id', 'inning', 'batting_team', "
            "'total_runs', 'over' columns."
        )

    powerplay_df = df[df['over'] < 6]

    powerplay_df = (
        powerplay_df
        .groupby(
            ['match_id', 'inning', 'batting_team']
        )['total_runs']
        .sum()
        .reset_index()
    )

    return powerplay_df


def middle_over_runs(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = [
        'match_id',
        'inning',
        'batting_team',
        'total_runs',
        'over'
    ]

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain "
            "'match_id', 'inning', 'batting_team', "
            "'total_runs', 'over' columns."
        )

    middle_over_runs_df = df[
        (df['over'] >= 6) &
        (df['over'] < 15)
    ]

    middle_over_runs_df = (
        middle_over_runs_df
        .groupby(
            ['match_id', 'inning', 'batting_team']
        )['total_runs']
        .sum()
        .reset_index()
    )

    return middle_over_runs_df


def death_overs(df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed argument must be a pandas DataFrame.")

    req_cols = [
        'match_id',
        'inning',
        'batting_team',
        'total_runs',
        'over'
    ]

    if not all(col in df.columns for col in req_cols):
        raise ValueError(
            "The DataFrame must contain "
            "'match_id', 'inning', 'batting_team', "
            "'total_runs', 'over' columns."
        )

    death_overs_df = df[df['over'] >= 15]

    death_overs_df = (
        death_overs_df
        .groupby(
            ['match_id', 'inning', 'batting_team']
        )['total_runs']
        .sum()
        .reset_index()
    )

    return death_overs_df


# MATCH LEVEL STATISTICS

match_df = pd.read_csv("datasets/cleaned_matches.csv")


def match_result(match_df):

    if not isinstance(match_df, pd.DataFrame):
        raise ValueError(
            "The match DataFrame must be a pandas DataFrame."
        )

    req_cols = ['id', 'winner']

    if not all(col in match_df.columns for col in req_cols):
        raise ValueError(
            "The match DataFrame must contain "
            "'id' and 'winner' columns."
        )

    return match_df[['id', 'winner']]


def win_margin(match_df):

    if not isinstance(match_df, pd.DataFrame):
        raise ValueError(
            "The match DataFrame must be a pandas DataFrame."
        )

    req_cols = [
        'id',
        'winner',
        'win_by_runs',
        'win_by_wickets'
    ]

    if not all(col in match_df.columns for col in req_cols):
        raise ValueError(
            "The match DataFrame must contain "
            "'id', 'winner', 'win_by_runs', "
            "'win_by_wickets' columns."
        )

    win_margin_df = match_df[
        ['id', 'winner', 'win_by_runs', 'win_by_wickets']
    ]

    return win_margin_df


def chasing_performance(df, match_df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            "The deliveries DataFrame must be a pandas DataFrame."
        )

    if not isinstance(match_df, pd.DataFrame):
        raise ValueError(
            "The match DataFrame must be a pandas DataFrame."
        )

    delivery_cols = [
        'inning',
        'match_id',
        'batting_team'
    ]

    if not all(col in df.columns for col in delivery_cols):
        raise ValueError(
            "The deliveries DataFrame must contain "
            "'inning', 'match_id', 'batting_team' columns."
        )

    match_cols = ['id', 'winner']

    if not all(col in match_df.columns for col in match_cols):
        raise ValueError(
            "The match DataFrame must contain "
            "'id' and 'winner' columns."
        )

    second_inning = (
        df[df['inning'] == 2][
            ['match_id', 'batting_team']
        ]
        .drop_duplicates()
    )

    result = match_result(match_df)

    chasing_df = second_inning.merge(
        result,
        left_on='match_id',
        right_on='id',
        how='left'
    )

    chasing_df['won'] = (
        chasing_df['batting_team']
        == chasing_df['winner']
    )

    return chasing_df


def defending_performance(df, match_df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            "The deliveries DataFrame must be a pandas DataFrame."
        )

    if not isinstance(match_df, pd.DataFrame):
        raise ValueError(
            "The match DataFrame must be a pandas DataFrame."
        )

    delivery_cols = [
        'inning',
        'match_id',
        'batting_team'
    ]

    if not all(col in df.columns for col in delivery_cols):
        raise ValueError(
            "The deliveries DataFrame must contain "
            "'inning', 'match_id', 'batting_team' columns."
        )

    match_cols = ['id', 'winner']

    if not all(col in match_df.columns for col in match_cols):
        raise ValueError(
            "The match DataFrame must contain "
            "'id' and 'winner' columns."
        )

    first_inning = (
        df[df['inning'] == 1][
            ['match_id', 'batting_team']
        ]
        .drop_duplicates()
    )

    result = match_result(match_df)

    defending_df = first_inning.merge(
        result,
        left_on='match_id',
        right_on='id',
        how='left'
    )

    defending_df['won'] = (
        defending_df['batting_team']
        == defending_df['winner']
    )

    return defending_df


def chasing_summary(df, match_df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            "The deliveries DataFrame must be a pandas DataFrame."
        )

    if not isinstance(match_df, pd.DataFrame):
        raise ValueError(
            "The match DataFrame must be a pandas DataFrame."
        )

    chasing_df = chasing_performance(df, match_df)

    summary = (
        chasing_df
        .groupby('batting_team')
        .agg(
            matches_chased=('match_id', 'count'),
            matches_won=('won', 'sum')
        )
        .reset_index()
    )

    summary['matches_lost'] = (
        summary['matches_chased']
        - summary['matches_won']
    )

    summary['win_percentage'] = (
        summary['matches_won']
        / summary['matches_chased']
    ) * 100

    return summary


def defending_summary(df, match_df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            "The deliveries DataFrame must be a pandas DataFrame."
        )

    if not isinstance(match_df, pd.DataFrame):
        raise ValueError(
            "The match DataFrame must be a pandas DataFrame."
        )

    defending_df = defending_performance(df, match_df)

    summary = (
        defending_df
        .groupby('batting_team')
        .agg(
            matches_defended=('match_id', 'count'),
            matches_won=('won', 'sum')
        )
        .reset_index()
    )

    summary['matches_lost'] = (
        summary['matches_defended']
        - summary['matches_won']
    )

    summary['win_percentage'] = (
        summary['matches_won']
        / summary['matches_defended']
    ) * 100

    return summary


# ============================================================
# TEAM PROFILE
# ============================================================

def team_profile(df, match_df):

    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            "The deliveries DataFrame must be a pandas DataFrame."
        )

    if not isinstance(match_df, pd.DataFrame):
        raise ValueError(
            "The match DataFrame must be a pandas DataFrame."
        )

    inning_run = innings_total_runs(df)[[
        'match_id',
        'inning',
        'batting_team',
        'total_runs'
    ]]

    wkt_lost_df = team_wickets_lost(df)[[
        'match_id',
        'inning',
        'batting_team',
        'wickets_lost'
    ]]

    run_rate_df = team_run_rate(df)[[
        'match_id',
        'inning',
        'batting_team',
        'run_rate'
    ]]

    team_boundary_runs_df = team_boundary_runs(df)[[
        'match_id',
        'inning',
        'batting_team',
        'boundary_runs'
    ]]

    team_boundary_percentage_df = team_boundary_percentage(df)[[
        'match_id',
        'inning',
        'batting_team',
        'boundary_percentage'
    ]]

    powerplay_runs_df = powerplay_runs(df)[[
        'match_id',
        'inning',
        'batting_team',
        'total_runs'
    ]].rename(
        columns={'total_runs': 'powerplay_runs'}
    )

    middle_over_runs_df = middle_over_runs(df)[[
        'match_id',
        'inning',
        'batting_team',
        'total_runs'
    ]].rename(
        columns={'total_runs': 'middle_over_runs'}
    )

    death_overs_df = death_overs(df)[[
        'match_id',
        'inning',
        'batting_team',
        'total_runs'
    ]].rename(
        columns={'total_runs': 'death_overs_runs'}
    )

    profile = inning_run.merge(
        wkt_lost_df,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    profile = profile.merge(
        run_rate_df,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    profile = profile.merge(
        team_boundary_runs_df,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    profile = profile.merge(
        team_boundary_percentage_df,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    profile = profile.merge(
        powerplay_runs_df,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    profile = profile.merge(
        middle_over_runs_df,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    profile = profile.merge(
        death_overs_df,
        on=['match_id', 'inning', 'batting_team'],
        how='left'
    )

    return profile

