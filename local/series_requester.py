import json
import traceback
from os.path import expanduser
import re

if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from py.config import ConfigReader
from series_extractor import extract_episode_info
from logger import write_to_requester_log
from local import direct_download, subtitle_downloader
import m_requests
from lxml import html


def download(series, season, episode):
    urls_used = []
    done = False

    while not done:

        if len(urls_used) > 40:
            done = True

        print "-" * 20
        episode_info = extract_episode_info(series, season, episode, skip_urls=urls_used)

        if episode_info is False:
            return False

        if "error" in episode_info.keys():
            write_to_requester_log(episode_info.get("error"), True)
            done = True
            continue
        title = episode_info.get('title')
        download_url = episode_info.get('download_url')
        urls_used.append(episode_info.get('url'))
        ext = episode_info.get('ext')

        print title
        print download_url
        print urls_used
        print ext

        try:
            direct_download.divide_n_download(series + '_s' + str(season) + 'e' + str(episode), download_url, ext, (
                'My-Downloads/Series-Downloads/' + series.replace('_', ' ').title().strip() + '/Season %d' % season))
        except:
            print "\n\n\nError:"
            print '*' * 50
            traceback.print_exc()
            print '*' * 50
            done = False
        else:
            subtitle_downloader.download_sub(title, (expanduser("~") +
                                                     '/My-Downloads/Series-Downloads/'
                                                     + series.replace('_', ' ').title() + '/Season %d' % season),
                                             title)
            done = True
            configReader = ConfigReader()
            config = configReader.get_settings_parser()
            series_list = configReader.get_series_list()
            series_list[series]['season'] = season
            series_list[series]['episode'] = episode
            config.set('Series', 'list', json.dumps(series_list))
            with open('downloader.ini', 'wb') as configfile:
                config.write(configfile)
            return True


def check():
    config = ConfigReader()
    series_list = config.get_series_list()
    print series_list
    for series in series_list.keys():

        print "\n\n"

        last_season = series_list[series].get('season')
        last_episode = series_list[series].get('episode')

        write_to_requester_log(
            "Last Episode Downloaded of " + series + " is S" + str(last_season) + "E" + str(last_episode))
        write_to_requester_log("Checking if new episode came")

        series_url = 'http://watch-tv-series.to' + '/serie/' + series
        page = m_requests.get(series_url)
        tree = html.fromstring(page.text)
        episode_url = 'http://watch-tv-series.to' + tree.xpath('//*[@id="left"]/div/ul/li[1]/a')[0].values()[0]
        latest = re.search(series + '_s(\d{1,2})_e(\d{1,2})', episode_url)
        season = int(latest.group(1))
        episode = int(latest.group(2))
        if last_season == season:
            if last_episode < episode:
                for ep in range(last_episode + 1, episode + 1):
                    download(series, season, ep)

            elif last_episode > episode:
                write_to_requester_log("Wrong config, Please check")
            elif last_episode == episode:
                write_to_requester_log("No new episodes")
        elif last_season < season:
            for n_season in range(last_season, season + 1):
                if last_season == n_season:
                    for ep in range(last_episode+1, 25):
                        try:
                            if not download(series, n_season, ep):
                                break
                        except Exception:
                            break
                else:
                    for ep in range(1, episode + 1):
                        if not download(series, n_season, ep):
                            break

        elif last_season > season:
            write_to_requester_log("Wrong config, Please check")

    write_to_requester_log("\n\n")
    write_to_requester_log("*" * 20)
    write_to_requester_log("Process finished, exiting....")
    write_to_requester_log(("*" * 20) + "\n\n")


if __name__ == '__main__':
    check()