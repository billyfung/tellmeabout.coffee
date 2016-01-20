from google.appengine.ext import ndb

class Coffee(ndb.Model):
    name = ndb.StringProperty()
    roaster = ndb.StringProperty()
    description = ndb.StringProperty()
    date_added = ndb.DateTimeProperty(auto_now_add=True)
    date_updated = ndb.DateTimeProperty(auto_now=True)
    date_removed = ndb.DateTimeProperty()
    price = ndb.FloatProperty()
    notes = ndb.StringProperty(repeated=True)
    region = ndb.StringProperty()
    active = ndb.BooleanProperty()
    product_page = ndb.StringProperty()
    size = ndb.StringProperty()
    image = ndb.BlobProperty(default=None)
