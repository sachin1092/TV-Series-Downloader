import webapp2
from py import views

url_patterns = [
    webapp2.Route('/upload', views.UploadHandler),
    webapp2.Route('/getDownloadList', views.DownloadListHandler)]