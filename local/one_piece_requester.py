import json
from os.path import expanduser
import traceback
import requests
import m_requests
from lxml import html

if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from py.config import ConfigReader
from one_piece_extractor import extract_episode_info
from logger import write_to_requester_log
from local import direct_download, subtitle_downloader

base_url = 'http://www.watchfree.to'
# base_url = 'http://www.watchfree.to/tv-6d1c-One-Piece-JP-tv-show-online-free-putlocker.html/season-%s-episode-%s'
# base_url = 'http://www.watchfree.to/tv-2984a3-Steins-Gate-tv-show-online-free-putlocker.html/season-%s-episode-%s'

def check():
    config = ConfigReader()
    series_list = config.get_series_list()
    for series in series_list.keys():
        try:

            all_downloaded = False

            serie_url = get_series_url(series)
            last_season = series_list[series].get('season')
            last_episode = series_list[series].get('episode')

            write_to_requester_log(
                "Last Episode Downloaded of " + series + " is S" + str(last_season) + "E" + str(last_episode))
            write_to_requester_log("Checking if new episode came")

            while not all_downloaded:
                last_episode = last_episode + 1
                series_url = base_url + serie_url + ("/season-%s-episode-%s" % (last_season, last_episode))
                print series, ": ", series_url
                video_page = m_requests.get(series_url)
                # print video_page.text
                if 'File not found.' in video_page.text:
                    last_season = last_season + 1
                    last_episode = 1
                    series_url = base_url + series_url + ("/season-%s-episode-%s" % (last_season, last_episode))
                    print series, ": ", series_url
                    video_page = m_requests.get(series_url)
                    # print video_page.text
                    if 'File not found.' in video_page.text:
                        print "Nothing to be done here."
                        all_downloaded = True

                urls_used = []
                if not all_downloaded:
                    done = False
                    while not done:

                        if len(urls_used) > 40:
                            done = True

                        print "-" * 20
                        print "Extracting url for season %d episode %d" % (last_season, last_episode)
                        episode_info = extract_episode_info(last_season, last_episode, series_url, skip_urls=urls_used)
                        if "error" in episode_info.keys():
                            write_to_requester_log(episode_info.get("error"), True)
                            done = True
                            continue
                        title = episode_info.get('title')
                        download_url = episode_info.get('download_url')
                        urls_used.append(episode_info.get('url'))
                        ext = episode_info.get('ext')

                        print title
                        print download_url
                        print urls_used
                        print ext

                        try:
                            # direct_download.divide_n_download(title, download_url, ext, 'My-Downloads/Series-Downloads/' + title)
                            direct_download.divide_n_download(series + '_s' + str(last_season) + 'e' + str(last_episode), download_url, ext, (
                                'My-Downloads/Series-Downloads/' + series.replace('_', ' ').title().strip() + '/Season %d' % last_season))
                        except:
                            print "\n\n\nError:"
                            print '*' * 50
                            traceback.print_exc()
                            print '*' * 50
                            done = False
                        else:
                            subtitle_downloader.download_sub(title, (expanduser("~") +
                                                     '/My-Downloads/Series-Downloads/'
                                                     + series.replace('_', ' ').title() + '/Season %d' % season),
                                             title)
                            done = True
                            configReader = ConfigReader()
                            config = configReader.get_settings_parser()
                            series_list = configReader.get_series_list()
                            series_list[series]['season'] = season
                            series_list[series]['episode'] = episode
                            config.set('Series', 'list', json.dumps(series_list))
                            with open('downloader.ini', 'wb') as configfile:
                                config.write(configfile)

        except:
            traceback.print_exc()
    # import pdb
    # pdb.set_trace()
    # config = ConfigReader()
    # one_piece_list = config.get_one_piece_list()
    # update_list = one_piece_list
    # last_season = one_piece_list.get('season')
    # last_episode = one_piece_list.get('episode')
    # write_to_requester_log(
    #         "Last Episode Downloaded of one piece is S" + str(last_season) + "E" + str(last_episode))
    # # for episode in one_piece_list:
    # #     print episode
    # print "\n\n"

    # season = int(last_season)
    # episode = int(last_episode)

    # all_downloaded = False

    # while not all_downloaded:
    #     urls_used = []
    #     url = base_url % (season, episode + 1)
    #     r = requests.get(url)
    #     if r.text == 'File not found.':
    #         all_downloaded = True
    #         return
    #     episode += 1
    #     done = False

    #     while not done:

    #         if len(urls_used) > 40:
    #             done = True

    #         print "-" * 20
    #         print "Extracting url for season %d episode %d" % (season, episode)
    #         episode_info = extract_episode_info(season, episode, skip_urls=urls_used)
    #         if "error" in episode_info.keys():
    #             write_to_requester_log(episode_info.get("error"), True)
    #             done = True
    #             continue
    #         title = episode_info.get('title')
    #         download_url = episode_info.get('download_url')
    #         urls_used.append(episode_info.get('url'))
    #         ext = episode_info.get('ext')

    #         print title
    #         print download_url
    #         print urls_used
    #         print ext

    #         try:
    #             direct_download.divide_n_download(title, download_url, ext, 'My-Downloads/Series-Downloads/' + title)
    #         except:
    #             print "\n\n\nError:"
    #             print '*' * 50
    #             traceback.print_exc()
    #             print '*' * 50
    #             done = False
    #         else:
    #             done = True
    #             update_list.update({'season': season, 'episode': episode})
    #             config = ConfigReader().get_settings_parser()
    #             config.set('Series', 'one_piece', json.dumps(update_list))
    #             with open('downloader.ini', 'wb') as configfile:
    #                 config.write(configfile)
    #             subtitle_downloader.download_sub(title, expanduser("~") +
    #                                              '/My-Downloads/Series-Downloads/' + title, title)


def get_series_url(name):
    name = name.replace(" ", "+")
    name = name.replace("_", "+")
    search_url = '/?keyword=%s&search_section=1'
    url = base_url + search_url % name
    write_to_requester_log(url, False)
    search_request = m_requests.get(url)
    search_page = html.fromstring(search_request.text)
    result = search_page.xpath('/html/body/div[1]/div[2]/div[2]/a')[0].values()[0]
    result = result.replace("watch", "tv")
    return result

if __name__ == '__main__':
    check()
    # config = ConfigReader()
    # series_list = config.get_series_list()
    # for series in series_list.keys():
        # try:
            # print series, ": ", get_series_url(series)
        # except:
            # import traceback
            # traceback.print_exc()
            # pass