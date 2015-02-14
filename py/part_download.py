import io
import logging
import os
import shutil
import requests
from google.appengine.ext import deferred
import webapp2

# author: sachin.shinde@searce.com
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
        # merge_ranges(filename, files)

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

    # files[filename + "part_" + str(index)] = io.BytesIO(r1.content)
    email = "me@sachinshinde.com"  #raw_input("Enter Dropbox email address:")
    password = "dropboxpass"  #getpass("Enter Dropbox password:")

    # Create the connection
    conn = DropboxConnection(email, password)
    # try:
    # Download file from internet
    # logging.info("***starting download")
    # r = requests.get(
    #     "http://50.7.164.194:8182/ucorn5vyrcu4tqukwyalhetmlq3qo6unjderakppp3bx4c5ecz6kn22b7m/video.mp4")
    # logging.info(len(r.content))
    # import io
    #
    # f = io.BytesIO(r.content)
    # logging.info("***file downloaded")

    # Upload the file
    conn.upload_file_f(io.BytesIO(r1.content), "/"+filename, filename + "part_" + str(index))
    # print("Upload")
    # except:
    #     logging.info("Upload failed")
    # else:
    #     self.response.write("Upload successful...yay!!")
    #     logging.info("Uploaded small_test_file.txt to the root of your Dropbox")
    # files["part_%s" % index].seek(0)

    # return files


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