import io
import logging
import os
import shutil
import requests
from google.appengine.ext import deferred
import webapp2
from config import ConfigReader

# author: me@sachinshinde.com
from dbupload import DropboxConnection


def part_download(url, start=[], end=[], index=0, filename="testFile"):

    from google.appengine.api import urlfetch
    urlfetch.set_default_fetch_deadline(60)

    if int(webapp2.get_request().headers.get('X-Appengine-Taskretrycount')) > 5:
        logging.debug(
            'Part Download failed, maximum number of tries exceeded.')
        raise deferred.PermanentTaskFailure

    logging.info("Inside task")
    logging.info(url)
    logging.info(str(start))
    logging.info(str(end))
    logging.info(str(index))

    if index == len(start):
        logging.info("Completed... yay!")
        write_status("completed", filename)
        return
        # merge_ranges(filename, files)
    elif index == 0:
        write_status("in progress", filename)

    logging.info('thread %s is running' % index)
    try:
        partial_download(url=url, start=start, end=end, index=index, filename=filename)
    except:
        logging.info('thread %s failed, running again' % index)
        deferred.defer(
            part_download, url=url,
            start=start, end=end, index=index, filename=filename)
    else:
        index += 1
        deferred.defer(
            part_download, url=url,
            start=start, end=end, index=index, filename=filename)


def partial_download(url, start=[], end=[], index=0, filename="testFile"):
    logging.info(url)
    r1 = requests.get(url,
                      headers={"Range": "bytes=%s-%s" % (start[index], end[index])})

    logging.info("Status Code: %s" % r1.status_code)
    logging.info(" for index: %d" % index)

    config_reader = ConfigReader()

    email = config_reader.get_dropbox_email()
    password = config_reader.get_dropbox_password()

    # Create the connection
    conn = DropboxConnection(email, password)

    # Upload the file
    conn.upload_file_f(io.BytesIO(r1.content), "/downloads/"+filename, filename + "_part_" + str(index))

    logging.info(conn.get_dir_list("/downloads/"+filename))


def merge_ranges(fileName, files):
    global final_file
    final_file = io.BytesIO("")
    for f in files.values():
        shutil.copyfileobj(f, final_file, 65536)

    final_file.seek(0, os.SEEK_END)
    print "final file size", final_file.tell()
    # final_file.seek(0)
    # file = open(fileName, "wb")
    # file.write(final_file.read())
    # file.close()


def write_status(msg, filename):
    logging.info(msg)

    config_reader = ConfigReader()

    email = config_reader.get_dropbox_email()
    password = config_reader.get_dropbox_password()

    # Create the connection
    conn = DropboxConnection(email, password)

    conn.delete_file("/downloads/"+filename, "status.txt")

    # Upload the file
    conn.upload_file_f(io.BytesIO(msg), "/downloads/"+filename, "status.txt")

    logging.info(conn.get_dir_list("/downloads/"+filename))