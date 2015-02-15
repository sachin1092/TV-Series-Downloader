import webapp2
from py import views

url_patterns = [
    webapp2.Route('/upload', views.UploadHandler)]