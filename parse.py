from lxml import html
import requests
import re
from time import sleep

series = raw_input("Enter the series to download: ")

series = re.sub(r'\s', '_', series)

base_url = 'http://watch-tv-series.to'
series_url = base_url + '/serie/' + series

print series_url

page = requests.get(series_url)

tree = html.fromstring(page.text)
episode_url = base_url + tree.xpath('//*[@id="left"]/div/ul/li[1]/a')[0].values()[0]
print episode_url

sleep(1)

episode_page = requests.get(episode_url)

episode_tree = html.fromstring(episode_page.text)
video_url = base_url + episode_tree.xpath('//*[@id="link_56963690"]/td[2]/a')[0].values()[1]
print video_url

sleep(1)

video_page = requests.get(video_url)
video_tree = html.fromstring(video_page.text)
gorilla_url = video_tree.xpath('/html/body/div[3]/div[2]/div/div[2]/div/div/div/div/div/div/div/a')[0].values()[0]
print gorilla_url