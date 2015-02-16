import httplib
import io
import logging
import urlparse
import mechanize
import urllib2
import re
import json
import time
import locale
import os

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from dropbox import client, rest, session


class DropboxConnection:
    """ Creates a connection to Dropbox """
    api_client = ''

    def __init__(self):
        self.login()

    def login(self):
        """ Login to Dropbox and return mechanize browser instance """

        # Fire up a browser using mechanize
        access_token = 'dEtppHemfvkAAAAAAAAT-jAdrAs4g0ogEsaegHQ32yHNa0EivIZmt7ZAgnavYOPH'
        self.api_client = client.DropboxClient(access_token)

    def upload_file(self, from_file, remote_dir, remote_file):
        """ Upload a file like object to Dropbox """
        # from_file = open(os.path.expanduser(from_path), "rb")

        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]

        encoding = locale.getdefaultlocale()[1] or 'ascii'
        full_path = (remote_dir + "/" + remote_file).decode(encoding)
        self.api_client.put_file(full_path, from_file)

    def ls(self, remote_dir):
        """ Get file info for a directory """

        dir_list = []

        """list files in current remote directory"""
        resp = self.api_client.metadata(remote_dir)

        if 'contents' in resp:
            for f in resp['contents']:
                name = os.path.basename(f['path'])
                encoding = locale.getdefaultlocale()[1] or 'ascii'
                dir_list.append(('%s\n' % name).encode(encoding))

        return dir_list

    def get_download_url(self, remote_dir, remote_file=None):
        """ Get the URL to download a file """
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]
        url = self.api_client.share(remote_dir + '/' + remote_file)['url'] if remote_file else self.api_client.share(remote_dir)['url']
        parsed = urlparse.urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        response = h.getresponse()
        if response.status/100 == 3 and response.getheader('Location'):
            return response.getheader('Location')[0:-1] + "1"
        else:
            return url

    def cat(self, remote_dir, remote_file):
        """display the contents of a file"""
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]
        f, metadata = self.api_client.get_file_and_metadata(remote_dir + "/" + remote_file)
        return f.read()

    def delete_file(self, remote_dir, remote_file=None):
        """ Delete a file"""
        if remote_file:
            self.api_client.file_delete(remote_dir + "/" + remote_file)
        else:
            self.api_client.file_delete(remote_dir)

    def delete_dir(self, remote_dir):
        """ Delete a directory """
        self.delete_file(remote_dir)