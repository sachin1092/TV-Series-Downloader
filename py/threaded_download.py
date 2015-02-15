import httplib
import os
import string
import time
import shutil
from threading import *
import io
import requests


doneCount = 0  # counter to count the finished thread number
files = {}
final_file = None

# start of download thead class


class HttpPartialDownloadThread(Thread):
    def __init__(self, hostURL, resourceURL, startByte, endByte, threadIndex):
        Thread.__init__(self)
        self.hostURL = hostURL
        self.resourceURL = resourceURL
        self.startByte = startByte
        self.endByte = endByte
        self.threadIndex = threadIndex
        self.done = False

    def run(self):
        print 'thread %s is running' % self.threadIndex
        try:
            self.partialDownload()
        except:
            print 'thread %s failed, running again' % self.threadIndex
            self.partialDownload()
        return

    def partialDownload(self):
        global doneCount, files
        # conn = httplib.HTTPConnection(self.hostURL)
        # conn.request("GET", self.resourceURL, headers={"Range": "bytes=%s-%s" % (self.startByte, self.endByte)})
        # r1 = conn.getresponse()
        print "http://" + self.hostURL + self.resourceURL
        r1 = requests.get("http://" + self.hostURL + self.resourceURL,
                          headers={"Range": "bytes=%s-%s" % (self.startByte, self.endByte)})

        print r1.status_code

        # file = open("part_%s" % self.threadIndex, "wb")
        # file.write(r1.read())
        # file.close()
        files["part_%s" % self.threadIndex] = io.BytesIO(r1.content)
        files["part_%s" % self.threadIndex].seek(0)

        self.done = True

        doneCount += 1

        # conn.close()
        return

# end of class

def mergeRanges(fileName, partialFileCount):
    global final_file
    final_file = io.BytesIO("")
    for f in files.values():
        shutil.copyfileobj(f, final_file, 65536)

    final_file.seek(0, os.SEEK_END)
    print "final file size", final_file.tell()
    final_file.seek(0)
    file = open(fileName, "wb")
    file.write(final_file.read())
    file.close()


def getContentLength(conn, resourceURL):
    #send "HEAD" request to get the basic information of the resourceURL
    conn.request("HEAD", resourceURL)
    r1 = conn.getresponse()
    print r1.status, r1.reason

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


def getRangeFileTest():
    url = "http://www.songspk320z.us/songoftheday/%5BSongs.PK%5D%20Sham%20Bhi%20Khub%20Hai%20-%20Karz%20(2002).mp3"
    import re
    match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{4})(.*)|http://(\w{3}\.\w*\.\w*)(.*)", url)
    hostURL = match.group(0) if match.group(0) else match.group(2)
    resourceURL = match.group(1) if match.group(1) else match.group(3)
    conn = httplib.HTTPConnection(hostURL)
    contentLength = getContentLength(conn, resourceURL)
    print contentLength
    partial_file_count = 0

    BLOCK_SIZE = 1000 * 100  #100K Bytes per block
    if contentLength > 0:
        #split the content into several parts: #BLOCK_SIZE per block.
        blockNum = contentLength / BLOCK_SIZE
        lastBlock = contentLength % BLOCK_SIZE
        partial_file_count = 0

        for i in range(0, blockNum + 1):
            start_byte = BLOCK_SIZE * i
            end_byte = start_byte + BLOCK_SIZE - 1

            if end_byte > contentLength - 1:
                end_byte = contentLength - 1

            if start_byte < end_byte:
                download_thread = HttpPartialDownloadThread(hostURL, resourceURL, start_byte, end_byte, i)
                download_thread.start()

                partial_file_count += 1

    #TODO: change it to event driven

    while doneCount < partial_file_count:
        print "waiting all threads terminated"
        time.sleep(1)

    #print doneCount,partial_file_count
    print 'Now merge them to one file'

    mergeRanges("test.mp3", partial_file_count)


if __name__ == '__main__':
    getRangeFileTest()