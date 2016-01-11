from flask import Flask
from google.appengine.ext import ndb

app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


class Coffee(ndb.Model):
    name = ndb.StringProperty()
    roaster = ndb.StringProperty()
    description = ndb.StringProperty()
    date_added = ndb.DateTimeProperty(auto_now_add=True)
    date_removed = ndb.DateTimeProperty()

    @classmethod
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)



@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World! this is jin'


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
