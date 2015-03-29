__author__ = 'sachin'

base_url = 'http://www.watchfree.to'

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
import m_requests
from logger import write_to_requester_log
from py.config import ConfigReader

__author__ = 'sachin'

import traceback


def extract_episode_info(season, ep, url, skip_urls=None, quality='[DVD]'):
	write_to_requester_log(url, False)
	video_request = m_requests.get(url)

	video_page = html.fromstring(video_request.text)
	number_of_urls = re.findall('</table>', video_request.text)
	video_urls = []
	try:
	    for i in xrange(1, len(number_of_urls)):
	        vid_xpath = '/html/body/div[2]/div[2]/div[4]/div[3]/table[%d]/tbody/tr/td[2]/strong/a' % i
	        vid_quality = video_page.xpath(
	            '/html/body/div[2]/div[2]/div[4]/div[3]/table[%d]/tbody/tr/td[1]/div' % i)[0].text
	        if vid_quality != quality:
	            continue
	        video_urls.append(video_page.xpath(vid_xpath)[0].values()[0])
	except:
		if not len(video_urls):
			import traceback
			traceback.print_exc()
	for vid_url in video_urls:
	    if skip_urls and vid_url in skip_urls:
	        continue
	    write_to_requester_log("\n\n\n", False)
	    write_to_requester_log("-" * 50, False)
	    write_to_requester_log('requesting ' + base_url + vid_url, False)
	    try:
	        download_json = json.loads(requests.get('http://my-youtube-dl.appspot.com/api/info?url='
	                                                + base_url + vid_url + '&flatten=True').text)
	        if download_json.get('videos') is not None:
	            return {'title': download_json.get('videos')[0].get('title'),
	                    'download_url': download_json.get('videos')[0].get('url'),
	                    'url': vid_url, 'ext': download_json.get('videos')[0].get('ext')}
	    except Exception, e:
	        write_to_requester_log(e.message, False)
	return {'error': 'No videos found'}


if __name__ == '__main__':
	season = raw_input("Enter one piece season to download: ")
	episode = raw_input("Enter one piece episode to download: ")
	write_to_requester_log(extract_episode_info(season, episode))
