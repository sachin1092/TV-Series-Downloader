
if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from subprocess import call
import io
import json
import os
import shutil
import re
from os.path import expanduser

import requests

from logger import write_to_downloader_log

completed = {}


def start_download():
    global completed

    home = expanduser("~")
    call(["mkdir", home + "/Series-Downloads"])

    downloads = json.loads(requests.get("http://series-downloader.appspot.com/getDownloadList?action=list").content)
    write_to_downloader_log(downloads)

    for fold in downloads["list"]:

        completed[fold] = False

        my_fold = fold.replace("%20", " ")
        call(["mkdir", home + "/Series-Downloads/" + my_fold])
        url = json.loads(requests.get(
            "http://series-downloader.appspot.com/getDownloadList?action=getDirURL&dir=" + fold).content)["url"]
        write_to_downloader_log(url)
        call(["wget", "-c", "-O", home + "/Series-Downloads/" + my_fold + ".zip", url])
        write_to_downloader_log(requests.get("http://series-downloader.appspot.com/getDownloadList?action=delFold&dir="
                                             + fold).content)
        completed[fold] = True


def start_downloader():
    global completed
    first = True
    while (False in completed.values()) or first:
        write_to_downloader_log("Completed: " + str(completed))
        first = False
        try:
            start_download()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            write_to_downloader_log("Error occurred, trying again")


if __name__ == "__main__":
    start_downloader()