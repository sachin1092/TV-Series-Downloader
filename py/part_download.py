import io
import json
import logging
import os
import shutil
import re
import requests
from google.appengine.ext import deferred
import webapp2
from config import ConfigReader

# author: me@sachinshinde.com
from dbupload import DropboxConnection


def part_download(url, start=[], end=[], index=0, filename="testFile", size=0):

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
        status = {'status': 'completed', 'url': url, 'size': size,
                  'ext': str(re.search("\.*.*(\.[a-zA-Z0-9]+)", url).group(1))}
        # "{'status': 'completed', 'url': " + url + ", 'size':"
        #              + str(size) + ", 'ext': " + str(re.search("\.*.*(\.[a-zA-Z0-9]+)", url).group(1)) + "}"
        write_status(json.dumps(status), filename)
        return

    logging.info('thread %s is running' % index)
    try:
        partial_download(url=url, start=start, end=end, index=index, filename=filename)
    except:
        logging.info('thread %s failed, running again' % index)
        deferred.defer(
            part_download, url=url,
            start=start, end=end, index=index, filename=filename, size=size)
    else:
        status = {'status': 'in progress', 'url': url, 'size': size, 'last_block': index,
                  'ext': str(re.search("\.*.*(\.[a-zA-Z0-9]+)", url).group(1))}
        # "{'status': 'in progress', 'url': " + url + ", 'size': "
        #              + str(size) + ", 'last_block': " + str(index) + ", 'ext': "
        #              + str(re.search("\.*.*(\.[a-zA-Z0-9]+)", url).group(1)) + "}"
        write_status(json.dumps(status), filename)
        index += 1
        deferred.defer(
            part_download, url=url,
            start=start, end=end, index=index, filename=filename, size=size)


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