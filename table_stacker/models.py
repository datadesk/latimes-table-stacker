# GAE biz
import logging
from google.appengine.ext import db

# Table biz
import yaml
import cStringIO
from table_fu import TableFu


class Table(db.Model):
    """
    Ready-to-serve CSV data.
    """
    # The source
    csv_name = db.StringProperty(required=True)
    csv_data = db.TextProperty(required=True)
    # The config
    yaml_name = db.StringProperty(required=True)
    yaml_data = db.TextProperty(required=True)
    # The goodies
    title = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    byline = db.StringProperty(required=False)
    publication_date = db.DateProperty(required=True)
    description = db.TextProperty(required=False)
    footer = db.TextProperty(required=False)
    sources = db.TextProperty(required=False)
    credits = db.TextProperty(required=False)
    # Meta
    tags = db.StringListProperty(required=True)
    is_published = db.BooleanProperty(required=True)
    
    def __unicode__(self):
        return self.title
    
    def __repr__(self):
        return '<Table: %s>' % self.title.encode("utf-8")
    
    def get_absolute_url(self):
        return u'/%s/' % self.slug
    
    def get_csv_url(self):
        return u'/csv/%s' % self.csv_name

    def get_tablefu_opts(self):
        return yaml.load(self.yaml_data)['column_options']
    
    def get_tablefu(self):
        """
        Trick the data out with TableFu.
        """
        from django.utils import simplejson
        csv = simplejson.loads(unicode(self.csv_data))
        return TableFu(csv, **self.get_tablefu_opts())
    
    def get_rendered_html(self):
        """
        Create the rendered HTML for this table.
        """
        from django.conf import settings
        from django.template.loader import render_to_string
        return render_to_string('table.html', { 
            'object': self, 
            'table': self.get_tablefu(),
            'size_choices': [1,2,3,4],
            'MEDIA_URL': settings.MEDIA_URL,
        })
    
