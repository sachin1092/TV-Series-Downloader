import io
import os
from os.path import expanduser
import re
import shutil
import requests
from subprocess import call
import urllib2

url = ''
filename = ''


def download(download_url, file_name):
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


if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from logger import write_to_downloader_log

    url = 'http://89.46.103.92:8777/cfuqiv7x2e2qedz7ni2b5gdtay7g4smpvlqfdudvutlsfuchmhx4nyrwlcfa/v.mp4'
    filename = '50_shades_of_grey'

    info_url = 'http://series-downloader.appspot.com/getInfo?download_url='

    if url == '':
        url = raw_input("Enter URL to download: ")
    if filename == '':
        filename = raw_input('Enter filename:')
    r1 = requests.get(info_url + url)
    contentLength = int(r1.content)

    print "content length is: " + str(contentLength)

    start = []
    end = []

    BLOCK_SIZE = 1000 * 1000 * 5  # 5000K Bytes per block
    if contentLength > 0:
        # split the content into several parts: #BLOCK_SIZE per block.
        blockNum = contentLength / BLOCK_SIZE
        lastBlock = contentLength % BLOCK_SIZE

        for i in range(0, blockNum + 1):
            start_byte = BLOCK_SIZE * i
            end_byte = start_byte + BLOCK_SIZE - 1

            if end_byte > contentLength - 1:
                end_byte = contentLength - 1

            if start_byte < end_byte:
                start.append(start_byte)
                end.append(end_byte)

        ext = str(re.search("\.*.*(\.[a-zA-Z0-9]+)", url).group(1))
        home = expanduser("~")
        call(["mkdir", home + "/My-Downloads"])
        for i in xrange(len(start)):
            download_url = 'http://series-downloader.appspot.com/downloads?filename=' + filename \
                           + '&download_url=' + url + '&start=' + str(start[i]) + '&end=' + str(end[i])
            # call(["wget", "-c", "-O", home + "/My-Downloads/" + filename + ext + '.' + str(i), download_url])
            download(download_url+'3434', home + "/My-Downloads/" + filename + ext + '.' + str(i))

        merge(len(start), str(filename+ext), str(home + '/My-Downloads'))



