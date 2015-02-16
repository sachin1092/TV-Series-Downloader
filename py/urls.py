import webapp2
from py import views

url_patterns = [
    webapp2.Route('/upload', views.UploadHandler),
    webapp2.Route('/getDownloadList', views.DownloadListHandler),
    webapp2.Route('/getURLResponse', views.ResponseHandler),
    webapp2.Route('/checkDownloads', views.DownloadChecker),
    webapp2.Route('/downloads', views.DownloadHandler),
    webapp2.Route('/getInfo', views.GetInfoHandler)]