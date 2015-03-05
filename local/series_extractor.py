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
import m_requests
import requests
from time import sleep
from logger import write_to_requester_log

__author__ = 'sachin'

import traceback

def extract_episode_info(series, season, ep):

    base_url = 'http://watch-tv-series.to'

    write_to_requester_log("\n")
    write_to_requester_log("-" * 40)

    write_to_requester_log("Will request download of " + series + " Season " + str(season) + " Episode " + str(ep))
    episode_page = m_requests.get("http://watch-tv-series.to/episode/"
                                  + series + "_s" + str(season) + "_e" + str(ep) + ".html")
    write_to_requester_log("Requesting URL http://watch-tv-series.to/episode/"
                           + series + "_s" + str(season) + "_e" + str(ep) + ".html")

    sleep(1)
    episode_tree = html.fromstring(episode_page.text)
    number_of_urls = re.findall('</tr>', episode_page.text)
    print "number of urls are %d" % len(number_of_urls)
    for i in xrange(2, len(number_of_urls)):
        try:
            xpath = '//*[@id="myTable"]/tbody/tr[%d]/td[2]/a' % i
            video_url = base_url + episode_tree.xpath(xpath)[0].values()[1]
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

            try:

                download_resp = json.loads(requests.get(
                    'http://my-youtube-dl.appspot.com/api/info?url=' + gorilla_url + '&flatten=True').text)
                if download_resp.get('videos') is not None:
                    return {'title': download_resp.get('videos')[0].get('title'), 
                        'download_url': download_resp.get('videos')[0].get('url'),
                        'url': gorilla_url}
            except:
                traceback.print_exc()
    return {'error': 'no vid found'}

if __name__ == '__main__':
    series = raw_input("Enter series name to download: ")
    season = raw_input("Enter season to download: ")
    episode = raw_input("Enter episode to download: ")
    write_to_requester_log(extract_episode_info(series, season, episode))