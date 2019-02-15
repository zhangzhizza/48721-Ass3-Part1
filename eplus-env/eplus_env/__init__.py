from gym.envs.registration import register
import os
import fileinput


FD = os.path.dirname(os.path.realpath(__file__));

register(
    id='IW-right-time-v1',
    entry_point='eplus_env.envs:EplusEnv',
    kwargs={'eplus_path':FD + '/envs/EnergyPlus-8-3-0/',
            'weather_path':FD + '/envs/weather/pittsburgh_TMY3.epw',
            'bcvtb_path':FD + '/envs/bcvtb/',
            'variable_path':FD + '/envs/eplus_models/iw_v97/learning/cfg/tmy3Weather.cfg',
            'idf_path':FD + '/envs/eplus_models/iw_v97/learning/idf/tmy3Weather.idf',
            'env_name': 'IW-tmy3Weather-v9706',
            'incl_forecast': False,
            'forecastRandMode': 'normal',
            'forecastRandStd': 0.15,
            'forecastSource': 'tmy3',
            'forecastFilePath': None,
            'forecast_hour': 12,
            'act_repeat': 1});