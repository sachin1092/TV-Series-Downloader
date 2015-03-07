import io
import shutil
import urllib2

import requests

import os
from os.path import expanduser


if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from logger import write_to_downloader_log

urls = ['movies', 'movies-1', 'movies-2', 'movies-3', 'movies-4',
        'movies-5', 'movies-6', 'movies-7', 'movies-8', 'movies-9']


def download(download_url, file_name):
    print 'download_url', download_url
    print 'file_name', file_name
    u = urllib2.urlopen(download_url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        download_buffer = u.read(block_sz)
        if not download_buffer:
            break

        file_size_dl += len(download_buffer)
        f.write(download_buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status += chr(8) * (len(status) + 1)
        print status,

    f.close()


def merge(num_blocks, f_name, m_path):
    final_file = io.BytesIO("")
    for f in xrange(num_blocks):
        if os.path.isfile(m_path + "/" + f_name + '.' + str(f)):
            shutil.copyfileobj(open(m_path + "/" + f_name + '.' + str(f), "r"),
                               final_file,
                               65536)
    final_file.seek(0, os.SEEK_END)
    write_to_downloader_log("file " + f_name + " saved with size " + str(final_file.tell()))
    final_file.seek(0)
    fl = open(m_path + "/" + f_name, "wb")
    fl.write(final_file.read())
    fl.close()
    for f in range(len(os.listdir(m_path)) - 1):
        if os.path.isfile(m_path + "/" + f_name + '.' + str(f)):
            os.remove(m_path + "/" + f_name + '.' + str(f))


def divide_n_download(title, url, ext, download_folder=None):
    info_url = 'http://series-downloader.appspot.com/getInfo?download_url='
    r1 = requests.get(info_url + url)
    content_length = int(r1.content)

    print "content length is: " + str(content_length)

    start = []
    end = []

    block_size = 1000 * 1000 * 5  # 5000K Bytes per block
    if content_length > 20971520:
        # split the content into several parts: #block_size per block.
        block_num = content_length / block_size

        for i in range(0, block_num + 1):
            start_byte = block_size * i
            end_byte = start_byte + block_size - 1

            if end_byte > content_length - 1:
                end_byte = content_length - 1

            if start_byte < end_byte:
                start.append(start_byte)
                end.append(end_byte)

        home = expanduser("~")

        f_path = home + "/" + download_folder if download_folder else home

        if not os.path.exists(f_path):
            os.makedirs(f_path)

        j = 0

        for i in xrange(len(start)):
            done = False
            while not done:
                download_url = 'http://' + urls[j] + '-downloader.appspot.com/downloads?filename=' + title \
                               + '&download_url=' + url + '&start=' + str(start[i]) + '&end=' + str(end[i])
                try:
                    download(download_url, f_path + "/" + title + '.' + ext + '.' + str(i))
                except urllib2.URLError, e:
                    print e.code
                    if e.code/100 == 5:
                        j = (j + 1) % len(urls)
                        done = False
                else:
                    done = True

        merge(len(start), str(title + '.' + ext), str(f_path))
    else:
        raise Exception('Content Length is weird')













