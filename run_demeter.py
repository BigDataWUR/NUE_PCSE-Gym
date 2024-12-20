import os
import argparse
import lib_programname
import pandas as pd

from pcse_gym.utils.eval import FindOptimum
import pcse_gym.utils.defaults as defaults
from pcse_gym.initialize_envs import initialize_env

path_to_program = lib_programname.get_path_executed_script()
rootdir = path_to_program.parents[0]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--location", type=str, default='PAGV', help="String for determining location to train Demeter")
    parser.add_argument("-y", "--year", type=int, default=None, help="Single year to put demeter")
    parser.add_argument("-yr", "--years", type=tuple[int, int], default=None, help="A range of years")
    parser.add_argument("--limited", action='store_true', help="Use constraints", dest='limited')
    parser.add_argument("--init-n", type=str, default=None, dest='init_n')
    parser.add_argument("--soil", type=str, default=None)
    parser.set_defaults(limited=False)
    args = parser.parse_args()

    if args.years is None:
        assert args.year
    elif args.year in None:
        assert args.years

    random_weather = False
    if args.location == 'NL':
        eval_locations = [(52.5, 5.5)]
    elif args.location == 'PAGV':
        eval_locations = [(52.57, 5.63)]
        random_weather = True
    else:
        eval_locations = [(51.5, 5.5)]
    if args.year:
        eval_year = [args.year]
    else:
        eval_year = [1990]

    crop_features = defaults.get_default_crop_features(pcse_env=2, vision=None)
    weather_features = defaults.get_default_weather_features()
    action_features = defaults.get_default_action_features()

    env = initialize_env(crop_features=crop_features,
                         action_features=action_features,
                         costs_nitrogen=0.01,
                         years=eval_year,
                         locations=eval_locations,
                         reward='NUE',
                         pcse_env=2,
                         nitrogen_levels=9,
                         random_weather=random_weather,
                         soil=args.soil,
                         )

    start = env.sb3_env.agmt.crop_start_date
    end = env.sb3_env.agmt.crop_end_date
    weeks = int((end - start).days / 7) + 1

    optimum = FindOptimum(env, eval_year).optimize_constrained_dump(eval_year=eval_year, limited=args.limited, n_level=args.init_n)
    print(optimum)


    df = pd.DataFrame(optimum, columns=[eval_year[0]])
    if args.init_n == 'high':
        os.makedirs(os.path.join(rootdir, 'demeter_results', 'constrained_all_high_n'), exist_ok=True)
        df.to_csv(os.path.join(rootdir, 'demeter_results', 'constrained_all_high_n',
                               f"{eval_locations[0][0]}-{eval_locations[0][1]}-{eval_year[0]}.csv"))
    elif args.init_n == 'low':
        os.makedirs(os.path.join(rootdir, 'demeter_results', 'constrained_all_low_n'), exist_ok=True)
        df.to_csv(os.path.join(rootdir, 'demeter_results', 'constrained_all_low_n',
                               f"{eval_locations[0][0]}-{eval_locations[0][1]}-{eval_year[0]}.csv"))
    elif args.soil == 'fast':
        os.makedirs(os.path.join(rootdir, 'demeter_results', 'constrained_all_fast_soil'), exist_ok=True)
        df.to_csv(os.path.join(rootdir, 'demeter_results', 'constrained_all_fast_soil',
                               f"{eval_locations[0][0]}-{eval_locations[0][1]}-{eval_year[0]}.csv"))
    elif args.soil == 'slo':
        os.makedirs(os.path.join(rootdir, 'demeter_results', 'constrained_all_slow_soil'), exist_ok=True)
        df.to_csv(os.path.join(rootdir, 'demeter_results', 'constrained_all_slow_soil',
                               f"{eval_locations[0][0]}-{eval_locations[0][1]}-{eval_year[0]}.csv"))
    else:
        os.makedirs(os.path.join(rootdir, 'demeter_results', 'constrained_all_0'), exist_ok=True)
        df.to_csv(os.path.join(rootdir, 'demeter_results', 'constrained_all_0', f"{eval_locations[0][0]}-{eval_locations[0][1]}-{eval_year[0]}.csv"))
    # n_timings(env)


if __name__ == "__main__":
    main()
