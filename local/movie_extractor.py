import logging
import os
import string
import time

if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lxml import html
import requests
from logger import write_to_requester_log

__author__ = 'sachin'

import traceback

def get_redirected_url(url):
    req = requests.get(url)
    return req.url


def extract_movie_info(movie):
    base_url = 'http://www.watchfree.to'
    search_url = '/?keyword=%s&search_section=1'
    url = base_url + search_url % movie
    print url
    search_request = requests.get(url)
    search_page = html.fromstring(search_request.text)
    result = search_page.xpath('/html/body/div/div[2]/div[3]/a')[0].values()
    print result
    video_request = requests.get(base_url + result[0])
    video_page = html.fromstring(video_request.text)
    import re
    number_of_urls = re.findall('</table>', video_request.text)
    print len(number_of_urls)
    video_urls = []
    try:
        for i in xrange(1, len(number_of_urls)):
            print i
            vid_xpath = '/html/body/div[2]/div[2]/div[5]/div[3]/table[%d]/tbody/tr/td[2]/strong/a' % i
            video_urls.append(video_page.xpath(vid_xpath)[0].values()[0])
    except:
        traceback.print_exc()
    print video_urls
    for vid_url in video_urls:
        print "*"*50
        print "\n\n\n"
        print 'requesting', base_url + vid_url
        # try:
        #     print get_redirected_url(base_url + vid_url)
        # except:
        #     traceback.print_exc()
        print requests.get(
            'http://my-youtube-dl.appspot.com/api/info?url=' + base_url + vid_url + '&flatten=True').text



if __name__ == '__main__':
    movie = raw_input("Enter movie to download: ")
    movie = movie.replace(" ", "+")
    extract_movie_info(movie)


