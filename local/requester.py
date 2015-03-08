import time
from os.path import expanduser

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from local import series_requester
from local import movie_requester

if __name__ == '__main__':
    f = open(expanduser('~') + '/My-Downloads/Summary.txt', 'a')
    f.write("-" * 100)
    f.write("\n")
    f.write("[" + str(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())) + "]")
    f.close()
    series_requester.check()
    movie_requester.check()
    f = open(expanduser('~') + '/My-Downloads/Summary.txt', 'a')
    f.write("\n")
    f.write("-" * 100)
    f.write("\n\n\n")
    f.close()