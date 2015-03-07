if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from local import series_requester
from local import movie_requester

if __name__ == '__main__':
    series_requester.check()
    movie_requester.check()