__author__ = 'sachin'

base_url = 'http://www.watchfree.to'
# search_url = '/tv-6d1c-One-Piece-JP-tv-show-online-free-putlocker.html/season-%s-episode-%s'
search_url = '/tv-2a31b4-Dragon-Ball-Super-tv-show-online-free-putlocker.html/season-%s-episode-%s'

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

__author__ = 'sachin'

import traceback


def extract_episode_info(season, ep, skip_urls=None, quality='[DVD]'):
	# import pdb
	# pdb.set_trace()
	url = base_url + search_url % (season, ep)
	write_to_requester_log(url, False)
	# search_request = m_requests.get(url)
	# search_page = html.fromstring(search_request.text)
	# result = search_page.xpath('/html/body/div[1]/div[2]/div[2]/a')[0].values()
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


def get_series_url(name):
	name = name.replace(" ", "+")
	base_url = 'http://www.watchfree.to'
	search_url = '/?keyword=%s&search_section=1'
	url = base_url + search_url % name
	write_to_requester_log(url, False)
	search_request = m_requests.get(url)
	search_page = html.fromstring(search_request.text)
	result = search_page.xpath('/html/body/div[1]/div[2]/div[2]/a')[0].values()[0]
	return result

if __name__ == '__main__':
	# season = raw_input("Enter one piece season to download: ")
	# episode = raw_input("Enter one piece episode to download: ")
	# write_to_requester_log(extract_episode_info(season, episode))
	name = raw_input("Enter name of the series to download")
	print get_series_url(name)
