import json
from os.path import expanduser
import traceback
import requests

if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from py.config import ConfigReader
from one_piece_extractor import extract_episode_info
from logger import write_to_requester_log
from local import direct_download, subtitle_downloader
# base_url = 'http://www.watchfree.to/tv-6d1c-One-Piece-JP-tv-show-online-free-putlocker.html/season-%s-episode-%s'
base_url = 'http://www.watchfree.to/tv-2984a3-Steins-Gate-tv-show-online-free-putlocker.html/season-%s-episode-%s'

def check():
    # import pdb
    # pdb.set_trace()
    config = ConfigReader()
    one_piece_list = config.get_one_piece_list()
    update_list = one_piece_list
    last_season = one_piece_list.get('season')
    last_episode = one_piece_list.get('episode')
    write_to_requester_log(
            "Last Episode Downloaded of one piece is S" + str(last_season) + "E" + str(last_episode))
    # for episode in one_piece_list:
    #     print episode
    print "\n\n"

    season = int(last_season)
    episode = int(last_episode)

    all_downloaded = False

    while not all_downloaded:
        urls_used = []
        url = base_url % (season, episode + 1)
        r = requests.get(url)
        if r.text == 'File not found.':
            all_downloaded = True
            return
        episode += 1
        done = False

        while not done:

            if len(urls_used) > 40:
                done = True

            print "-" * 20
            print "Extracting url for season %d episode %d" % (season, episode)
            episode_info = extract_episode_info(season, episode, skip_urls=urls_used)
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
                direct_download.divide_n_download(title, download_url, ext, 'My-Downloads/Series-Downloads/' + title)
            except:
                print "\n\n\nError:"
                print '*' * 50
                traceback.print_exc()
                print '*' * 50
                done = False
            else:
                done = True
                update_list.update({'season': season, 'episode': episode})
                config = ConfigReader().get_settings_parser()
                config.set('Series', 'one_piece', json.dumps(update_list))
                with open('downloader.ini', 'wb') as configfile:
                    config.write(configfile)
                subtitle_downloader.download_sub(title, expanduser("~") +
                                                 '/My-Downloads/Series-Downloads/' + title, title)


if __name__ == '__main__':
    check()