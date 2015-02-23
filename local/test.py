__author__ = 'sachin'

if __name__ == '__main__':
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import m_requests

    r = m_requests.get(
        "http://subscene.com" + '/subtitles/release?q=' + 'Fifty%20Shades%20of%20Grey%202015%20HC%20WEBRip%20x264-RARBG',
        headers={"LanguageFilter": "13"})
    print r.content