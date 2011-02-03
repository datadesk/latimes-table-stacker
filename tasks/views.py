import logging
from google.appengine.ext import db
from table_stacker.models import Table
from google.appengine.ext import webapp


def get_key_or_none(request):
    """
    Gets the key param from the db, or returns None.
    """
    # Is the key is in the GET params?
    key = request.get('key', None)
    if not key:
        return None
    # Is the key is valid?
    try:
        key = db.Key(key)
    except:
        return None
    # Is the key in the database?
    obj = db.get(key)
    if not obj:
        return None
    # If all of the above are yes...
    return obj


class UpdateSimilarTables(webapp.RequestHandler):
    """
    Update the similarity lists for all tables that share tags with the
    submitted key.
    """
    def get(self):
        # Check if the key exists as an object in the db
        obj = get_key_or_none(self.request)
        # If it does...
        if obj:
            # ..update connected docs
            obj.similar_tables = obj.get_similar_tables()
            obj.put()
            # And then grab them all
            similar_tables = db.get(obj.similar_tables)
        # Otherwise just grab the ones currently linked to them
        else:
            key = db.Key(self.request.get('key', None))
            similar_tables = Table.all().filter("similar_tables =", key)
        # Then loop through and update all of them.
        for obj in similar_tables:
            obj.similar_tables = obj.get_similar_tables()
            logging.debug("Updated similar documents for %s" % obj)
            obj.put()
        # Close out
        self.response.out.write('OK')








