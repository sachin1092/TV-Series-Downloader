import requests

__author__ = 'sachin'


def get(url, cookies=None, headers=None):
    if cookies and headers:
        return requests.get("http://series-downloader.appspot.com/getURLResponse?url=" + url, cookies=cookies, headers=headers)
    elif cookies:
        return requests.get("http://series-downloader.appspot.com/getURLResponse?url=" + url, cookies=cookies)
    elif headers:
        return requests.get("http://series-downloader.appspot.com/getURLResponse?url=" + url, headers=headers)
    return requests.get("http://series-downloader.appspot.com/getURLResponse?url=" + url)