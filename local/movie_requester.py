import json
import traceback

if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from py.config import ConfigReader
from movie_extractor import extract_movie_info
from logger import write_to_requester_log
from local import direct_download, subtitle_downloader


def check():
    config = ConfigReader()
    movies_list = config.get_movies_list()
    update_list = movies_list
    print movies_list
    for movie in movies_list:
        urls_used = []
        done = False
        print "\n\n"
        while not done:

            if len(urls_used) > 40:
                done = True

            print "-" * 20
            print "Extracting url for movie %s" % movie
            movie_info = extract_movie_info(movie)
            if "error" in movie_info.keys():
                write_to_requester_log(movie_info.get("error"), True)
                done = True
                continue
            title = movie_info.get('title')
            download_url = movie_info.get('download_url')
            urls_used.append(movie_info.get('url'))
            ext = movie_info.get('ext')

            print title
            print download_url
            print urls_used
            print ext

            try:
                direct_download.divide_n_download(title, download_url, ext, 'My-Downloads/Movie-Downloads/' + title)
            except:
                print "\n\n\nError:"
                print '*' * 50
                traceback.print_exc()
                print '*' * 50
                done = False
            else:
                subtitle_downloader.download_sub(title,
                                                 'My-Downloads/Movie-Downloads/' + title, title)
                done = True
                update_list.remove(movie)
                config = ConfigReader().get_settings_parser()
                config.set('Movies', 'list', json.dumps(update_list))
                with open('downloader.ini', 'wb') as configfile:
                    config.write(configfile)


if __name__ == '__main__':
    check()