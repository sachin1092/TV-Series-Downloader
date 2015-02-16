if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import hashlib
import os
import requests

__author__ = 'sachin'

#this hash function receives the name of the file and returns the hash code
def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()

if __name__ == "__main__":
    print "Hello"
    m_hash = get_hash("/home/sachin/Series-Downloads/Agent Carter/Season 1/agent_carter_s1e4.mp4")
    print m_hash
    m_hash = "edc1981d6459c6111fe36205b4aff6c2"
    url = "http://api.thesubdb.com/?action=search&hash=%s" % m_hash
    print url
    r = requests.get(url,
                     headers={"User-Agent": "SubDB/1.0 (Series_Downloader/0.1; https://github.com/sachin1092/TV-Series-Downloader)"})
    print r.content