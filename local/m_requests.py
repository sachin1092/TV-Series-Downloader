import requests

__author__ = 'sachin'


def get(url, cookies=None):
    if cookies:
        return requests.get("http://series-downloader.appspot.com/getURLResponse?url=" + url, cookies=cookies)
    return requests.get("http://series-downloader.appspot.com/getURLResponse?url=" + url)