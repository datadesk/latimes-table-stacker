from tasks.views import *
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

url_list = [
    ('/_/table/update-similar/', UpdateSimilarTables),
]

application = webapp.WSGIApplication(url_list, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

