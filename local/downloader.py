import re

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from subprocess import call
import json
from os.path import expanduser
from local import unzip
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

        unzip.unzip(home + "/Series-Downloads/" + my_fold + ".zip")

        write_to_downloader_log("Deleting the remote folder")
        delete_resp = requests.get("http://series-downloader.appspot.com/getDownloadList?action=delFold&dir="
                                   + fold).content
        write_to_downloader_log(delete_resp)

        if re.search("Dropbox", delete_resp):
            write_to_downloader_log("Error occurred while deleting so trying again.")
            delete_resp = requests.get("http://series-downloader.appspot.com/getDownloadList?action=delFold&dir="
                                       + fold).content
            write_to_downloader_log(delete_resp)



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

    write_to_downloader_log("\n\n" + ("*" * 20))
    write_to_downloader_log("\nProcess finished, exiting....\n")
    write_to_downloader_log(("*" * 20) + "\n\n")


if __name__ == "__main__":
    start_downloader()