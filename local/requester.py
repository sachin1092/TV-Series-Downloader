if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from logger import write_to_requester_log
from py.config import ConfigReader
import json
from lxml import html
import re
from time import sleep
import requests

import m_requests

base_url = 'http://watch-tv-series.to'


def check():
    config = ConfigReader().get_settings_parser()
    series_list = json.loads(config.get('Series', 'list'))
    write_to_requester_log(series_list)
    for series in series_list:

        write_to_requester_log("\n")
        write_to_requester_log("*" * 50)

        last_season = int(json.loads(config.get(series, "last_episode_downloaded")).keys()[0])
        last_episode = int(json.loads(config.get(series, "last_episode_downloaded")).values()[0])
        write_to_requester_log(
            "Last Episode Downloaded of " + series + " is S" + str(last_season) + "E" + str(last_episode))
        write_to_requester_log("Checking if new episode came")
        series_url = base_url + '/serie/' + series
        page = m_requests.get(series_url)
        tree = html.fromstring(page.text)
        episode_url = base_url + tree.xpath('//*[@id="left"]/div/ul/li[1]/a')[0].values()[0]
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
            for ep in range(0, episode + 1):
                download(series, season, ep)

        elif last_season > season:
            write_to_requester_log("Wrong config, Please check")

    write_to_requester_log("\n\n" + ("*" * 20))
    write_to_requester_log("\nProcess finished, exiting....\n")
    write_to_requester_log(("*" * 20) + "\n\n")


def download(series, season, ep):
    write_to_requester_log("\n")
    write_to_requester_log("-" * 40)

    write_to_requester_log("Will request download of " + series + " Season " + str(season) + " Episode " + str(ep))
    episode_page = m_requests.get("http://watch-tv-series.to/episode/"
                                  + series + "_s" + str(season) + "_e" + str(ep) + ".html")
    write_to_requester_log("Requesting URL http://watch-tv-series.to/episode/"
                           + series + "_s" + str(season) + "_e" + str(ep) + ".html")

    sleep(1)

    episode_tree = html.fromstring(episode_page.text)
    try:
        video_url = base_url + episode_tree.xpath('//*[@id="myTable"]/tbody/tr[2]/td[2]/a')[0].values()[1]
    except IndexError:
        write_to_requester_log("No videos for this epiosde")
    else:
        write_to_requester_log(video_url)

        sleep(1)

        video_page = m_requests.get(video_url)
        video_tree = html.fromstring(video_page.text)
        gorilla_url = \
            video_tree.xpath('/html/body/div[3]/div[2]/div/div[2]/div/div/div/div/div/div/div/a')[0].values()[0]
        write_to_requester_log(gorilla_url)

        download_resp = requests.get(
            'http://my-youtube-dl.appspot.com/api/info?url=' + gorilla_url + '&flatten=True')
        write_to_requester_log(json.loads(download_resp.text)['videos'][0]['url'])
        my_url = "http://series-downloader.appspot.com/upload?filename=" + series \
                 + "_s" + str(season) + "e" + str(ep) + "&download_url=" \
                 + json.loads(download_resp.text)['videos'][0]['url']

        if requests.get(my_url).content == "Success...I guess":
            config = ConfigReader().get_settings_parser()
            config.set(series, 'last_episode_downloaded', '{"' + str(season) + '":' + str(ep) + "}")
            with open('downloader.ini', 'wb') as configfile:
                config.write(configfile)


if __name__ == '__main__':
    check()