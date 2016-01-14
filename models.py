from google.appengine.ext import ndb

class Coffee(ndb.Model):
    name = ndb.StringProperty()
    roaster = ndb.StringProperty()
    description = ndb.StringProperty()
    date_added = ndb.DateTimeProperty(auto_now_add=True)
    date_removed = ndb.DateTimeProperty()
    price = ndb.IntegerProperty()
    notes = ndb.StringProperty()
    region = ndb.StringProperty()
    status = ndb.StringProperty()
    product_page = ndb.StringProperty()
    size = ndb.StringProperty()
    dollar_per_size = ndb.IntegerProperty
