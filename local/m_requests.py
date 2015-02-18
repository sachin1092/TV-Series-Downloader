import requests

__author__ = 'sachin'


def get(url):
    return requests.get("http://series-downloader.appspot.com/getURLResponse?url=" + url)