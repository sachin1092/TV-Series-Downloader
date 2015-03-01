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

def extract_movie_info(movie, skip_urls=None):
    movie = movie.replace(" ", "+")
    base_url = 'http://www.watchfree.to'
    search_url = '/?keyword=%s&search_section=1'
    url = base_url + search_url % movie
    write_to_requester_log(url)
    search_request = requests.get(url)
    search_page = html.fromstring(search_request.text)
    result = search_page.xpath('/html/body/div/div[2]/div[3]/a')[0].values()
    video_request = requests.get(base_url + result[0])
    video_page = html.fromstring(video_request.text)
    number_of_urls = re.findall('</table>', video_request.text)
    video_urls = []
    try:
        for i in xrange(1, len(number_of_urls)):
            vid_xpath = '/html/body/div[2]/div[2]/div[5]/div[3]/table[%d]/tbody/tr/td[2]/strong/a' % i
            video_urls.append(video_page.xpath(vid_xpath)[0].values()[0])
    except:
        traceback.print_exc()
    for vid_url in video_urls:
        if skip_urls and vid_url in skip_urls:
            continue
        write_to_requester_log("\n\n\n")
        write_to_requester_log("-"*50)
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
    movie = raw_input("Enter movie to download: ")
    write_to_requester_log(extract_movie_info(movie))