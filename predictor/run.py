from . import collect,\
    lls_model,\
    postprocess,\
    persistence,\
    service
import os
from datetime import datetime, timedelta

if 'LOCAL' in os.environ:
    import matplotlib
    matplotlib.use('svg')
    import matplotlib.pyplot as plt  # noqa: E402
    import json  # noqa: E402
    from scipy.stats import norm
    import numpy as np


prediction_year = os.environ.get('PREDICTION_YEAR',
                                 str(datetime.now().year))
exploratory_mode = os.environ.get('EXPLORATORY_MODE',
                                  False)


def daterange(start, end, delta_days):
    days_in_range = int(((end-start).days))
    for n in range(0, days_in_range, delta_days):
        date = start + timedelta(n)
        yield (str(date.date()), date)


def dates():
    if exploratory_mode:
        start_date = datetime(int(prediction_year), 2, 15)
        end_date = datetime(int(prediction_year), 4, 15)
        yield from daterange(start_date, end_date, 14)
    else:
        yield (prediction_year, datetime.now())


def run(year=prediction_year):
    print('Processing year {}'.format(year))

    teams = service.query_all_teams(year)

    for run_name, date in dates():
        run_teams(run_name, year, teams, date)

    if exploratory_mode:
        filename = os.path.join('output', 'hist_{}.svg'.format(prediction_year))
        plt.savefig(filename)


def run_teams(run_name, year, teams, from_date):
    teams_dict = collect.build_teams_dictionary(teams)

    games = collect.get_all_games(teams, from_date)

    print('running model on {} games'.format(len(games)))

    games_list = list(games.values())

    team_map = collect.build_team_map(games_list)

    # offensive defensive model
    l_model = lls_model.Model()

    coefficients = collect.build_offensive_defensive_coefficient_matrix(
        games_list,
        team_map)

    constants = collect.build_offensive_defensive_constants(
        games_list,
        team_map)

    l_model.train(coefficients, constants)

    od_ratings = postprocess.calculate_lss_offensive_defensive_ratings(
        team_map,
        l_model)

    teams_with_ratings = postprocess.merge_results_with_teams_dict(
        teams_dict,
        od_ratings)

    include_run_name = 'LOCAL' in os.environ
    persistence.persist(run_name, year, teams_with_ratings, include_run_name)

    service.copy_divisions(run_name, year)

    if exploratory_mode:
        (average_error_per_game,
         errors,
         unseen_game_count,
         games_sorted_by_error,
         correct_count) = postprocess.error_per_unseen_game(
            teams_with_ratings,
            games)

        persist_games_sorted_by_error(run_name, games_sorted_by_error)

        print('Average error per unseen score '
              'for {} games as of {}: {}'.format(
                    unseen_game_count,
                    from_date,
                    average_error_per_game))

        print('Games called correctly {} / {} ({}%)'.format(
            correct_count, unseen_game_count, 100 * (correct_count / unseen_game_count)))

        plt.hist(errors, bins=np.arange(30), density=True)


def persist_games_sorted_by_error(run_name, games_sorted_by_error):
    fname = os.path.join('output', run_name, 'games_sorted_by_error.json')
    with open(fname, 'w') as f:
        json.dump(games_sorted_by_error, f, indent=2)
