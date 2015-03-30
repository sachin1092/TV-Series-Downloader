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
from series_extractor import extract_episode_info
from logger import write_to_requester_log
from local import direct_download, subtitle_downloader

base_url = 'http://www.watchfree.to'

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
                if 'File not found.' in video_page.text:
                    last_season = last_season + 1
                    last_episode = 1
                    series_url = base_url + serie_url + ("/season-%s-episode-%s" % (last_season, last_episode))
                    print series, ": ", series_url
                    video_page = m_requests.get(series_url)
                    # print video_page.text
                    if 'File not found.' in video_page.text:
                        print "Nothing to be done here.\n\n"
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