import webapp2

from py.urls import url_patterns


app = webapp2.WSGIApplication(url_patterns, debug=True)