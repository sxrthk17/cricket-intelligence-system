from analytics.analytics_engine import *
import pandas as pd
import numpy as np

df = pd.read_csv('datasets/real_cleaned_deliveries.csv')

match_df = pd.read_csv(r'datasets\cleaned_matches.csv')

# =======================================================
# TEST 40: team_profile()
# =======================================================

result = team_profile(df, match_df)

print(result.head())
print(result.columns)

assert isinstance(result, pd.DataFrame)

expected_columns = [
    'match_id',
    'inning',
    'batting_team',
    'total_runs',
    'wickets_lost',
    'run_rate',
    'boundary_runs',
    'boundary_percentage',
    'powerplay_runs',
    'middle_over_runs',
    'death_overs_runs'
]

assert list(result.columns) == expected_columns

print("PASS: output structure")


# -------------------------------------------------------
# Check intended grain
# -------------------------------------------------------

assert not result.duplicated(
    ['match_id', 'inning', 'batting_team']
).any()

print("PASS: one row per match-innings-team")


# -------------------------------------------------------
# Columns must be unique
# -------------------------------------------------------

assert result.columns.is_unique

print("PASS: columns are unique")


# -------------------------------------------------------
# Independent calculation for one row
# -------------------------------------------------------

row = result.iloc[0]

group_df = df[
    (df['match_id'] == row['match_id']) &
    (df['inning'] == row['inning']) &
    (df['batting_team'] == row['batting_team'])
]

expected_total_runs = group_df['total_runs'].sum()

expected_wickets = group_df[
    group_df['player_dismissed'] != 'not out'
]['player_dismissed'].count()

expected_legal_balls = group_df[
    (group_df['wide_runs'] == 0) &
    (group_df['noball_runs'] == 0)
]['ball'].count()

expected_run_rate = (
    expected_total_runs * 6
) / expected_legal_balls

expected_fours = (
    group_df['batsman_runs'] == 4
).sum()

expected_sixes = (
    group_df['batsman_runs'] == 6
).sum()

expected_boundary_runs = (
    expected_fours * 4 +
    expected_sixes * 6
)

if expected_total_runs == 0:
    expected_boundary_percentage = np.nan
else:
    expected_boundary_percentage = (
        expected_boundary_runs /
        expected_total_runs
    ) * 100

expected_powerplay_runs = group_df[
    group_df['over'] < 6
]['total_runs'].sum()

expected_middle_over_runs = group_df[
    (group_df['over'] >= 6) &
    (group_df['over'] < 15)
]['total_runs'].sum()

expected_death_runs = group_df[
    group_df['over'] >= 15
]['total_runs'].sum()


print("Match ID:", row['match_id'])
print("Inning:", row['inning'])
print("Batting team:", row['batting_team'])

print("Expected total runs:", expected_total_runs)
print("Actual total runs:", row['total_runs'])

print("Expected wickets lost:", expected_wickets)
print("Actual wickets lost:", row['wickets_lost'])

print("Expected run rate:", expected_run_rate)
print("Actual run rate:", row['run_rate'])

print("Expected boundary runs:", expected_boundary_runs)
print("Actual boundary runs:", row['boundary_runs'])

print(
    "Expected boundary percentage:",
    expected_boundary_percentage
)

print(
    "Actual boundary percentage:",
    row['boundary_percentage']
)

print(
    "Expected powerplay runs:",
    expected_powerplay_runs
)

print(
    "Actual powerplay runs:",
    row['powerplay_runs']
)

print(
    "Expected middle-over runs:",
    expected_middle_over_runs
)

print(
    "Actual middle-over runs:",
    row['middle_over_runs']
)

print(
    "Expected death-over runs:",
    expected_death_runs
)

print(
    "Actual death-over runs:",
    row['death_overs_runs']
)


assert row['total_runs'] == expected_total_runs

assert (
    row['wickets_lost'] == expected_wickets
    or (
        pd.isna(row['wickets_lost']) and
        expected_wickets == 0
    )
)

assert np.isclose(
    row['run_rate'],
    expected_run_rate
)

assert row['boundary_runs'] == expected_boundary_runs

if np.isnan(expected_boundary_percentage):
    assert pd.isna(row['boundary_percentage'])
else:
    assert np.isclose(
        row['boundary_percentage'],
        expected_boundary_percentage
    )

assert row['powerplay_runs'] == expected_powerplay_runs
assert row['middle_over_runs'] == expected_middle_over_runs
assert row['death_overs_runs'] == expected_death_runs

print("PASS: independent team-profile calculation")


# -------------------------------------------------------
# Cross-check against component functions
# -------------------------------------------------------

expected_df = innings_total_runs(df)[[
    'match_id',
    'inning',
    'batting_team',
    'total_runs'
]]

wickets_df = team_wickets_lost(df)[[
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

boundary_runs_df = team_boundary_runs(df)[[
    'match_id',
    'inning',
    'batting_team',
    'boundary_runs'
]]

boundary_percentage_df = team_boundary_percentage(df)[[
    'match_id',
    'inning',
    'batting_team',
    'boundary_percentage'
]]

powerplay_df = powerplay_runs(df)[[
    'match_id',
    'inning',
    'batting_team',
    'total_runs'
]].rename(
    columns={'total_runs': 'powerplay_runs'}
)

middle_df = middle_over_runs(df)[[
    'match_id',
    'inning',
    'batting_team',
    'total_runs'
]].rename(
    columns={'total_runs': 'middle_over_runs'}
)

death_df = death_overs(df)[[
    'match_id',
    'inning',
    'batting_team',
    'total_runs'
]].rename(
    columns={'total_runs': 'death_overs_runs'}
)


expected_df = expected_df.merge(
    wickets_df,
    on=['match_id', 'inning', 'batting_team'],
    how='left'
)

expected_df = expected_df.merge(
    run_rate_df,
    on=['match_id', 'inning', 'batting_team'],
    how='left'
)

expected_df = expected_df.merge(
    boundary_runs_df,
    on=['match_id', 'inning', 'batting_team'],
    how='left'
)

expected_df = expected_df.merge(
    boundary_percentage_df,
    on=['match_id', 'inning', 'batting_team'],
    how='left'
)

expected_df = expected_df.merge(
    powerplay_df,
    on=['match_id', 'inning', 'batting_team'],
    how='left'
)

expected_df = expected_df.merge(
    middle_df,
    on=['match_id', 'inning', 'batting_team'],
    how='left'
)

expected_df = expected_df.merge(
    death_df,
    on=['match_id', 'inning', 'batting_team'],
    how='left'
)


expected_df = expected_df[
    expected_columns
]

expected_df = expected_df.sort_values(
    ['match_id', 'inning', 'batting_team']
).reset_index(drop=True)

actual_df = result.sort_values(
    ['match_id', 'inning', 'batting_team']
).reset_index(drop=True)


pd.testing.assert_frame_equal(
    actual_df,
    expected_df
)

print("PASS: cross-function consistency")


# -------------------------------------------------------
# Non-negative checks
# -------------------------------------------------------

assert (result['total_runs'] >= 0).all()

assert (
    result['wickets_lost'].dropna() >= 0
).all()

assert (result['run_rate'] >= 0).all()

assert (
    result['boundary_runs'].dropna() >= 0
).all()

assert (
    result['powerplay_runs'].dropna() >= 0
).all()

assert (
    result['middle_over_runs'].dropna() >= 0
).all()

assert (
    result['death_overs_runs'].dropna() >= 0
).all()

print("PASS: non-negative team metrics")


# -------------------------------------------------------
# Boundary percentage range
# -------------------------------------------------------

valid_boundary_percentage = (
    result['boundary_percentage'].dropna()
)

assert valid_boundary_percentage.between(
    0,
    100
).all()

print("PASS: boundary percentage range")


# -------------------------------------------------------
# Validation: bad deliveries input
# -------------------------------------------------------

try:
    team_profile("hello", match_df)
except ValueError as e:
    print("PASS:", e)
else:
    print("FAIL: bad deliveries input was accepted")


# -------------------------------------------------------
# Validation: bad match input
# -------------------------------------------------------

try:
    team_profile(df, "hello")
except ValueError as e:
    print("PASS:", e)
else:
    print("FAIL: bad match input was accepted")