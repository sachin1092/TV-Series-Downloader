import logging
import os
import string
import time

if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lxml import html
import requests
from logger import write_to_requester_log

__author__ = 'sachin'

#
# def extractor(index):
#     # print "Requesting: " + "http://urgrove.com/?s=" + movie
#     # movie_search = requests.get("http://urgrove.com/?s=" + movie)
#     # movie_search_tree = html.fromstring(movie_search.text)
#     # try:
#     # print movie_search_tree.xpath('//*[@id="content"]/div[1]/div[2]/a')[0].values()
#     # except IndexError:
#     # write_to_requester_log("No videos for this epiosde")
#
#
#     ses = lt.session()
#     ses.listen_on(6881, 6891)
#     params = {
#         'save_path': os.getcwd(),
#         'storage_mode': lt.storage_mode_t(2),
#         'paused': False,
#         'auto_managed': True,
#         'duplicate_is_error': True}
#     link = "magnet:?xt=urn:btih:56169D27E03749D8288A899D9C6A123EC57AC7EE&dn=" \
#            "ccleaner+5+03+5128+incl+business+technician+professional+" \
#            "edition+crack+atom&tr=udp%3A%2F%2Fcoppersurfer.tk%3A6969%2Fannounce&tr=" \
#            "udp%3A%2F%2Fopen.demonii.com%3A1337"
#     handle = lt.add_magnet_uri(ses, link, params)
#     ses.start_dht()
#
#     print 'downloading metadata...'
#     while not handle.has_metadata():
#         time.sleep(1)
#
#     print dir(handle)
#     print "File priorities"
#     file_priorities = handle.file_priorities()
#     print file_priorities
#     file_priority = [0 for n in range(len(file_priorities))]
#     file_priority[index] = 1
#     print handle.prioritize_files(file_priority)
#     print handle.file_priorities()
#     print "piece priorities"
#     print handle.piece_priorities()
#     file_piece_count = len(filter(lambda x: x == 1, handle.piece_priorities()))
#     print "File " + str(index) + " has " + str(file_piece_count) + " pieces."
#     print handle.save_path()
#     # print handle.prioritize_pieces({1: 0})
#     # print handle.piece_priorities()
#     #
#     #
#
#     # print 'got metadata, starting torrent download...'
#     # while handle.status().state != lt.torrent_status.seeding:
#     # s = handle.status()
#     #     state_str = ['queued', 'checking', 'downloading metadata',
#     #                  'downloading', 'finished', 'seeding', 'allocating']
#     #     print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s %d.3' % \
#     #           (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
#     #            s.num_peers, state_str[s.state], s.total_download / 1000000)
#     #     time.sleep(5)
#
#
# def download(handle):
#     while handle.status().state != lt.torrent_status.seeding:
#         s = handle.status()
#         state_str = ['queued', 'checking', 'downloading metadata',
#                      'downloading', 'finished', 'seeding', 'allocating']
#         print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s %d.3' % \
#               (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
#                s.num_peers, state_str[s.state], s.total_download / 1000000)
#         time.sleep(5)


def extract_movie_info(movie):
    base_url = 'http://www.watchfree.to'
    search_url = '/?keyword=%s&search_section=1'
    url = base_url + search_url % movie
    print url
    search_request = requests.get(url)
    search_page = html.fromstring(search_request.text)
    result = search_page.xpath('/html/body/div/div[2]/div[3]/a')[0].values()
    print result
    video_request = requests.get(base_url + result[0])
    video_page = html.fromstring(video_request.text)
    print video_page.xpath('/html/body/div[2]/div[2]/div[5]/div[3]')[0].values()



if __name__ == '__main__':
    movie = raw_input("Enter movie to download: ")
    movie = movie.replace(" ", "+")
    extract_movie_info(movie)


