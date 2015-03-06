if __name__ == '__main__':
	from os import sys, path
	sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from py.config import ConfigReader
from movie_extractor import extract_movie_info
from logger import write_to_requester_log

def check():
	config = ConfigReader()
	movies_list = config.get_movies_list()
	print movies_list
	for movie in movies_list:
		urls_used = []
		print "\n\n"
		print "-"*20
		print "Extracting url for movie %s" % movie
		movie_info = extract_movie_info(movie)
		if "error" in movie_info.keys():
			write_to_requester_log(movie_info.get("error"), True)
			continue
		title = movie_info.get('title')
		download_url = movie_info.get('download_url')
		urls_used.append(movie_info.get('url'))

		print title
		print download_url
		print urls_used


if __name__ == '__main__':
	check()