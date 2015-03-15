if __name__ == "__main__":
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lxml import html
import time
import traceback
from local import m_requests
import os
import zipfile
import re
import requests

__author__ = 'sachin'

base_url = "http://subscene.com"


def download_sub(file_name, f_path, new_name=None):

    try:
        if not os.path.exists(f_path):
            os.makedirs(f_path)

        print "Requesting: ", base_url + '/subtitles/release?q=' + file_name.replace(' ', '+')

        r = m_requests.get(base_url + '/subtitles/release?q=' + file_name.replace(' ', '+'),
                         cookies={"LanguageFilter": "13"})
        tree = html.fromstring(r.text)
        specific_url = tree.xpath('//*[@id="content"]/div[1]/div/div/table/tbody/tr[1]/td[1]/a')[0].values()[0]
        print specific_url
        r1 = m_requests.get(base_url + specific_url)
        specific_tree = html.fromstring(r1.text)
        download_url = specific_tree.xpath('//*[@id="downloadButton"]')[0].values()[0]
        print download_url
        import direct_download
        direct_download.download('http://series-downloader.appspot.com/downloads?filename='
                                 + file_name.replace(' ', '%20')
                                 + '&download_url='
                                 + base_url + download_url, f_path + '/' + file_name + '.zip')
        zipfile.ZipFile(f_path + '/' + file_name + '.zip').extractall(f_path)
        files = os.listdir(f_path)
        os.remove(f_path + '/' + file_name + '.zip')
        if new_name:
            for m_file in files:
                match = re.search('.srt$', m_file)
                if match and (time.time() - os.path.getctime(f_path + '/' + m_file) < 10):
                    os.rename(f_path + '/' + m_file, f_path + '/' + new_name + '.srt')
    except:
        traceback.print_exc()


if __name__ == "__main__":
    f_name = ''
    if f_name == '':
        f_name = raw_input("Enter file name to download subtitles: ")

    download_sub(f_name, '/home/sachin/My-Downloads/')