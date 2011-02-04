# GAE biz
import logging
from google.appengine.ext import db
from google.appengine.api import urlfetch

# URLs
import urllib

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
    # The result
    rendered_html = db.TextProperty(required=False)
    # The meta
    similar_tables = db.ListProperty(db.Key, default=None)
    tags = db.ListProperty(db.Key, default=None)
    is_published = db.BooleanProperty(required=True)
    
    def __unicode__(self):
        return self.title
    
    def __repr__(self):
        return '<Table: %s>' % self.title.encode("utf-8")
    
    def get_absolute_url(self):
        return u'/%s/' % self.slug
    
    def get_csv_url(self):
        return u'/csv/%s' % self.csv_name
    
    def get_xls_url(self):
        return u'/xls/%s' % self.slug
    
    def get_json_url(self):
        return u'/json/%s' % self.slug
    
    def get_share_url(self):
        """
        The link we can use for share buttons.
        """
        return 'http://spreadsheets.latimes.com%s' % self.get_absolute_url()
    
    def get_tablefu_opts(self):
        return yaml.load(self.yaml_data).get('column_options', {})
    
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
        return render_to_string('table_content.html', { 
            'object': self, 
            'table': self.get_tablefu(),
            'size_choices': [1,2,3,4],
        })
    
    def get_tag_list(self):
        """
        Return all the Tag objects connected to this object.
        """
        return db.get(self.tags)
    
    def get_rendered_tag_list(self, html=True, conjunction='and'):
        """
        Return a rendered list of tags.
        
        By default a HTML link list that's ready for the table detail page.
        """
        from django.utils.text import get_text_list
        tag_list = self.get_tag_list()
        tag_list.sort(key=lambda x: x.title)
        if html:
            tag_list = ['<a href="%s">%s</a>' % (i.get_absolute_url(), i.title)
                for i in tag_list]
        else:
            tag_list = [i.title for i in tag_list]
        return get_text_list(tag_list, conjunction)
    
    def get_html_tag_list(self):
        """
        Returns an HTML link list that's ready for the table detail page.
        """
        return self.get_rendered_tag_list(html=True, conjunction='and')
    
    def get_keywords_list(self):
        """
        Returns a list of tags that ready for the META keywords tag on
        the table_detail page.
        """
        tag_list = tag_list = self.get_tag_list()
        tag_list.sort(key=lambda x: x.title)
        return ", ".join([i.title.lower() for i in tag_list])
    
    def get_similar_tables(self):
        """
        Returns a list of Keys for the tables that share tags with this object,
        ordered by the number of similar tags.
        """
        self_key = self.key()
        related_dict = {}
        # Loop through all of the tags
        for tag in self.get_tag_list():
            # Get each table that shares this tag
            table_set = Table.all().filter('tags =', tag.key())
            # Exclude the current table
            for table in table_set:
                # Exclude this table from the list
                this_key = table.key()
                if this_key == self_key:
                    continue
                # If it's a different table, increase the related count by 1
                try:
                    related_dict[this_key] += 1
                except KeyError:
                    related_dict[this_key] = 1
        # Sort it into a list ranked by the count
        related_list = related_dict.items()
        related_list.sort(key=lambda x: x[1], reverse=True)
        # Return just the keys
        return [i[0] for i in related_list]
    
    def get_similar_tables_list(self):
        """
        Get a list of the related table objects, not keys.
        """
        return db.get(self.similar_tables)


class Tag(db.Model):
    """
    A descriptive label connected to a table.
    """
    title = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    
    def __unicode__(self):
        return self.title
    
    def __repr__(self):
        return '<Tag: %s>' % self.title.encode("utf-8")
    
    def get_absolute_url(self):
        return u'/tag/%s/page/1/' % self.slug

