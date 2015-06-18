import configparser
import json


class ConfigReader:

    settings = None

    def __init__(self):
        self.settings = configparser.ConfigParser()
        self.settings.read('downloader.ini')

    def get_dropbox_email(self):
        return self.settings.get('Dropbox', 'Email')

    def get_dropbox_password(self):
        return self.settings.get('Dropbox', 'Password')

    def get_series_list(self):
        return json.loads(self.settings.get('Series', 'list'))

    def get_settings_parser(self):
        return self.settings

    def get_movies_list(self):
        return json.loads(self.settings.get('Movies', 'list'))

    def get_one_piece_list(self):
        return json.loads(self.settings.get('Series', 'one_piece'))