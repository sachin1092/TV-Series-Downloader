import json

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from py.config import ConfigReader

config = ConfigReader().get_settings_parser()
series_list = json.loads(config.get('Series', 'list'))
print series_list
for series in series_list:
    print "Last Episode Downloaded of ", series, " is ", config.get(series, "last_episode_downloaded")
