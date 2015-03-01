import logging
import os
import string
import time
import json
import re

if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lxml import html
import requests
from logger import write_to_requester_log

__author__ = 'sachin'

import traceback

def extract_episode_info(series, season, ep, skip_urls=None):

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
    for vid_url in video_urls:
        if skip_urls and vid_url in skip_urls:
            continue
        write_to_requester_log("*"*50)
        write_to_requester_log("\n\n\n")
        write_to_requester_log('requesting ' + base_url + vid_url)
        try:
            downld_json = json.loads(requests.get('http://my-youtube-dl.appspot.com/api/info?url=' 
                + base_url + vid_url + '&flatten=True').text)
            if downld_json.get('videos') is not None:
                return {'title': downld_json.get('videos')[0].get('title'), 
                    'download_url': downld_json.get('videos')[0].get('url'),
                    'url': vid_url}
        except:
            traceback.print_exc()
    return {'error': 'no vid found'}

if __name__ == '__main__':
    episode = raw_input("Enter episode to download: ")
    write_to_requester_log(extract_episode_info(episode))