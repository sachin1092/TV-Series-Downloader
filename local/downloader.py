import io
import json
import os
import shutil
import re
import requests
from os.path import expanduser

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from dbupload import dbconn
from subprocess import call
from py.config import ConfigReader

completed = {}


def start_download():

    global completed

    home = expanduser("~")
    call(["mkdir", home + "/Series-Downloads"])

    downloads = json.loads(requests.get("http://series-downloader.appspot.com/getDownloadList?action=list").content)
    print downloads

    for fold in downloads["list"]:

        completed[fold] = False

        my_fold = fold.replace("%20", " ")
        call(["mkdir", home + "/Series-Downloads/" + my_fold])
        files = json.loads(requests.get(
            "http://series-downloader.appspot.com/getDownloadList?action=getFiles&dir=" + fold).content)
        print files
        for fl in files["file_list"]:
            print "http://series-downloader.appspot.com/getDownloadList?action=getURL&dir=" + fold + "&file=" + fl
            url = json.loads(requests.get(
                "http://series-downloader.appspot.com/getDownloadList?action=getURL&dir="
                + fold + "&file=" + fl).content)["url"]
            print url
            call(["wget", "-c", "-O", home + "/Series-Downloads/" + my_fold + "/" + fl, url])
            print requests.get("http://series-downloader.appspot.com/getDownloadList?action=del&dir="
                               + fold + "&file=" + fl).content

        print requests.get("http://series-downloader.appspot.com/getDownloadList?action=delFold&dir="
                           + fold).content
        merge_ranges(my_fold, m_path=home + "/Series-Downloads/" + my_fold)
        completed[fold] = True


def merge_ranges(file_name, m_path=""):

    final_file = io.BytesIO("")
    if not re.search('part_', str(os.listdir(m_path))):
        return
    for f in range(len(os.listdir(m_path))):
        shutil.copyfileobj(open(m_path + "/" + file_name.replace(" ", "_").lower() + "part_" + str(f), "r"), final_file,
                           65536)
    final_file.seek(0, os.SEEK_END)
    print "file " + file_name + ".mp4 saved with size ", final_file.tell()
    final_file.seek(0)
    fl = open(m_path + "/" + file_name + ".mp4", "wb")
    fl.write(final_file.read())
    fl.close()
    for f in range(len(os.listdir(m_path)) - 1):
        os.remove(m_path + "/" + file_name.replace(" ", "_").lower() + "part_" + str(f))


def start_downloader():
    global completed
    first = True
    while (False in completed.values()) or first:
        print "Completed:", completed
        first = False
        try:
            start_download()
        except:
            print "Error occurred, trying again"

if __name__ == "__main__":
    start_downloader()