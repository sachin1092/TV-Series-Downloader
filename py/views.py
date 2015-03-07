import io
import json
import requests
import string
import webapp2
import logging
import httplib
import re
from google.appengine.ext import deferred

# author: me@sachinshinde.com
from dbupload import DropboxConnection
from py import part_download
from py.config import ConfigReader
# from py.check_downloads import initiate_download


def getContentLength(conn, resourceURL):
    # send "HEAD" request to get the basic information of the resourceURL
    conn.request("HEAD", resourceURL)
    r1 = conn.getresponse()
    logging.info("Status %s" % str(r1.status))
    logging.info("Reason %s" % str(r1.reason))

    # Note that you must have read the whole response before you can send a new request to the server.
    # otherwise you will meet httplib.ResponseNotReady error, even you don't need the body.
    r1.read()

    content_length = 0

    # read "accept-ranges" header to see if server supports ranges request
    accept_ranges = r1.getheader("accept-ranges")

    if accept_ranges == "bytes":
        # read "content-length" header to get the length of the content section of the HTTP message in bytes
        content_length = string.atoi(r1.getheader("content-length"))

    return content_length


class UploadHandler(webapp2.RequestHandler):
    def get(self):

        from google.appengine.api import urlfetch

        urlfetch.set_default_fetch_deadline(60)

        filename = self.request.GET["filename"]
        url = self.request.GET["download_url"]

        logging.info(filename)
        logging.info(url)

        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{4})(.*)|http://(\w{0,5}\.\w*\.\w*:\d{4})(.*)", url)
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

            status = {'status': 'in progress', 'url': url, 'size': contentLength, 'last_block': -1,
                      'filename': filename,
                      'ext': str(re.search("\.*.*(\.[a-zA-Z0-9]+)", url).group(1))}

            conn = part_download.login()

            part_download.write_status(json.dumps(status), filename, conn)
            logging.info("Starting the defer..YO!!")

            deferred.defer(
                part_download.part_download, url=url,
                start=start, end=end, index=0, filename=filename, size=contentLength)

        self.response.write("Success...I guess")


class DownloadListHandler(webapp2.RequestHandler):
    def get(self):

        action = self.request.GET["action"]

        config_reader = ConfigReader()
        email = config_reader.get_dropbox_email()
        password = config_reader.get_dropbox_password()

        # Create the connection
        conn = DropboxConnection(email, password)

        downloads = {}

        if action == "list":
            downloads["list"] = []
            dirs = conn.ls("/downloads")
            for dr in dirs.keys():
                dr_no_space = dr.replace(" ", "%20")
                if json.loads(conn.get_file_data("/downloads/" + dr_no_space, "status.txt"))['status'] == "completed":
                    downloads["list"].append(dr_no_space)
        elif action == "getFiles":
            downloads["file_list"] = []
            dr_no_space = str(self.request.GET["dir"]).replace(" ", "%20")
            try:
                fls = conn.ls("/downloads/" + dr_no_space)
            except:
                fls = conn.ls("/downloads/" + dr_no_space)
            logging.info(str(fls))
            for fl in fls.keys():
                if fl != "status.txt":
                    downloads["file_list"].append(fl)
        elif action == "getURL":
            dr_no_space = str(self.request.GET["dir"]).replace(" ", "%20")
            fl = str(self.request.GET["file"]).replace(" ", "%20")
            try:
                downloads["url"] = (conn.get_public_download_url("/downloads/" + dr_no_space + "/", fl))
            except:
                downloads["url"] = (conn.get_public_download_url("/downloads/" + dr_no_space + "/", fl))
        elif action == "getDirURL":
            dr_no_space = str(self.request.GET["dir"]).replace(" ", "%20")
            try:
                downloads["url"] = (conn.get_public_download_url_dir("/downloads/" + dr_no_space + "/"))
            except:
                downloads["url"] = (conn.get_public_download_url_dir("/downloads/" + dr_no_space + "/"))
        elif action == "del":
            dr_no_space = str(self.request.GET["dir"]).replace(" ", "%20")
            fl = str(self.request.GET["file"]).replace(" ", "%20")
            try:
                conn.delete_file("/downloads/" + dr_no_space + "/", fl)
            except:
                conn.delete_file("/downloads/" + dr_no_space + "/", fl)
            self.response.write("Deleted " + fl + " from Dropbox")
            return
        elif action == "delFold":
            dr_no_space = str(self.request.GET["dir"]).replace(" ", "%20")
            conn.delete_dir("/downloads/" + dr_no_space)
            self.response.write("Deleted " + dr_no_space + " from Dropbox")
            return

        self.response.write(json.dumps(downloads))


class ResponseHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.GET["url"]
        if self.request.cookies and self.request.headers:
            self.response.write(requests.get(url, cookies=self.request.cookies, headers=self.request.headers).content)
        elif self.request.cookies:
            self.response.write(requests.get(url, cookies=self.request.cookies).content)
        elif self.request.headers:
            self.response.write(requests.get(url, headers=self.request.headers).content)
        self.response.write(requests.get(url).content)


class DownloadChecker(webapp2.RequestHandler):
    def get(self):
        logging.info("Running downloader checker cron")
        from google.appengine.api import urlfetch

        urlfetch.set_default_fetch_deadline(60)

        config_reader = ConfigReader()
        email = config_reader.get_dropbox_email()
        password = config_reader.get_dropbox_password()

        # Create the connection
        conn = DropboxConnection(email, password)
        dirs = conn.ls("/downloads")
        for dr in dirs.keys():
            dr_no_space = dr.replace(" ", "%20")
            stat_file = conn.get_file_data("/downloads/" + dr_no_space, "status.txt")
            logging.info(stat_file)
            status = json.loads(stat_file)
            if status['status'] != "completed":
                url = status['url']
                size = status['size']
                index = status['last_block']
                filename = status['filename']
                start = []
                end = []
                BLOCK_SIZE = 1000 * 1000 * 5  # 2000K Bytes per block
                if size > 0:
                    # split the content into several parts: #BLOCK_SIZE per block.
                    blockNum = size / BLOCK_SIZE
                    lastBlock = size % BLOCK_SIZE

                    for i in range(0, blockNum + 1):
                        start_byte = BLOCK_SIZE * i
                        end_byte = start_byte + BLOCK_SIZE - 1

                        if end_byte > size - 1:
                            end_byte = size - 1

                        if start_byte < end_byte:
                            start.append(start_byte)
                            end.append(end_byte)

                    deferred.defer(
                        part_download.part_download, url=url,
                        start=start, end=end, index=index, filename=filename, size=size)
                logging.info("resuming...")
                logging.info(str(status))

        self.response.write("Successfully started cron")


class DownloadHandler(webapp2.RequestHandler):
    def get(self):
        from google.appengine.api import urlfetch

        urlfetch.set_default_fetch_deadline(60)

        filename = self.request.GET["filename"]
        url = self.request.GET["download_url"]
        start = self.request.GET.get("start")
        end = self.request.GET.get("end")

        # logging.info(filename)
        logging.info(url)
        if start and end:
            r1 = requests.get(url,
                              headers={"Range": "bytes=%s-%s" % (start, end)})
        else:
            r1 = requests.get(url)

        logging.info("Status Code: %s" % r1.status_code)

        self.response.headers['Content-Type'] = 'application/octet-stream'
        self.response.headers['Content-Disposition'] = str('attachment; filename=' + str(filename))
        self.response.out.write(r1.content)


class GetInfoHandler(webapp2.RequestHandler):
    def get(self):
        from google.appengine.api import urlfetch
        from urlparse import urlparse

        urlfetch.set_default_fetch_deadline(60)
        url = self.request.GET["download_url"]
        o = urlparse(url)
        # match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{4})(.*)|http://(\w{0,5}\.\w*\.\w*:\d{4})(.*)", url)
        hostURL = o.netloc  # match.group(1) if match.group(1) else match.group(3)
        resourceURL = o.path  # match.group(2) if match.group(2) else match.group(4)

        hostURL = hostURL.replace(" ", "%20")
        resourceURL = resourceURL.replace(" ", "%20")

        logging.info("hosturl %s" % hostURL)
        logging.info("resourceurl %s" % resourceURL)

        conn = httplib.HTTPConnection(hostURL)
        contentLength = getContentLength(conn, resourceURL)
        self.response.write(contentLength)