import string
import webapp2
# from dbupload import DropboxConnection
# import py.lib.ServiceApiConfig as SAC
# from getpass import getpass
# import requests
import logging
import httplib
import re
from google.appengine.ext import deferred

# author: sachin.shinde@searce.com
from py import part_download


def getContentLength(conn, resourceURL):
    # send "HEAD" request to get the basic information of the resourceURL
    conn.request("HEAD", resourceURL)
    r1 = conn.getresponse()
    logging.info("Status %s" % str(r1.status))
    logging.info("Reason %s" % str(r1.reason))

    #Note that you must have read the whole response before you can send a new request to the server.
    #otherwise you will meet httplib.ResponseNotReady error, even you don't need the body.
    r1.read()

    content_length = 0

    #read "accept-ranges" header to see if server supports ranges request
    accept_ranges = r1.getheader("accept-ranges")

    if accept_ranges == "bytes":
        #read "content-length" header to get the length of the content section of the HTTP message in bytes
        content_length = string.atoi(r1.getheader("content-length"))

    return content_length


class UploadHandler(webapp2.RequestHandler):

    def get(self):

        # service = SAC.createService("me@sachinshinde.com", "gDrive")
        # self.response.write(str(service.files().list().execute()))
        #
        # return
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)

        filename = self.request.GET["filename"]
        url = self.request.GET["download_url"]

        logging.info(filename)
        logging.info(url)

        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{4})(.*)|http://(\w{3}\.\w*\.\w*)(.*)", url)
        hostURL = match.group(1) if match.group(1) else match.group(3)
        resourceURL = match.group(2) if match.group(2) else match.group(4)

        hostURL = hostURL.replace(" ", "%20")
        resourceURL = resourceURL.replace(" ", "%20")

        logging.info("hosturl %s" % hostURL)
        logging.info("resourceurl %s" % resourceURL)

        conn = httplib.HTTPConnection(hostURL)
        contentLength = getContentLength(conn, resourceURL)

        logging.info(contentLength)

        start = []
        end = []

        BLOCK_SIZE = 1000 * 1000  # 1000K Bytes per block
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

            logging.info("Starting the defer..YO!!")

            deferred.defer(
                part_download.part_download, url=url,
                start=start, end=end, index=0, filename=filename)

            # email = "me@sachinshinde.com"  #raw_input("Enter Dropbox email address:")
            # password = "dropboxpass"  #getpass("Enter Dropbox password:")
            #
            # from google.appengine.api import urlfetch
            # urlfetch.set_default_fetch_deadline(60)
            #
            # # Create a little test file
            # # fh = open("small_test_file.txt","w")
            # # fh.write("Small test file")
            # # fh.close()
            #
            #
            # # Create the connection
            # conn = DropboxConnection(email, password)
            # # try:
            # # Download file from internet
            # logging.info("***starting download")
            # r = requests.get(
            #     "http://50.7.164.194:8182/ucorn5vyrcu4tqukwyalhetmlq3qo6unjderakppp3bx4c5ecz6kn22b7m/video.mp4")
            # logging.info(len(r.content))
            # import io
            #
            # f = io.BytesIO(r.content)
            # logging.info("***file downloaded")
            #
            # # Upload the file
            # conn.upload_file_f(f, "/", "test.mp3")
            # # print("Upload")
            # # except:
            # #     logging.info("Upload failed")
            # # else:
            # #     self.response.write("Upload successful...yay!!")
            # #     logging.info("Uploaded small_test_file.txt to the root of your Dropbox")
        self.response.write("Success...I guess")
