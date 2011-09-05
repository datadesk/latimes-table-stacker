# Table biz
import yaml
from table_fu import TableFu
from django.db import models
from managers import TableLiveManager, TableManager, TagManager


class Table(models.Model):
    """
    Ready-to-serve CSV data.
    """
    # The source
    csv_name = models.CharField(max_length=100)
    # The config
    yaml_name = models.CharField(max_length=100)
    yaml_data = models.TextField(blank=True)
    # The goodies
    title = models.CharField(max_length=500)
    slug = models.SlugField()
    kicker = models.CharField(max_length=500, blank=True)
    byline = models.CharField(max_length=500, blank=True)
    publication_date = models.DateField()
    description = models.TextField(blank=True)
    legend = models.CharField(max_length=500, blank=True)
    footer = models.TextField(blank=True)
    sources = models.TextField(blank=True)
    credits = models.TextField(blank=True)
    show_download_links = models.BooleanField(default=True)
    # The meta
    tags = models.ManyToManyField('Tag', blank=True)
    is_published = models.BooleanField()
    show_in_feeds = models.BooleanField(default=True)
    objects = TableManager()
    live = TableLiveManager()
    
    class Meta:
        ordering = ("-publication_date",)
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return u'/%s/' % self.slug
    
    def get_csv_url(self):
        return u'/api/%s.csv' % self.slug
    
    def get_xls_url(self):
        return u'/api/%s.xls' % self.slug
    
    def get_json_url(self):
        return u'/api/%s.json' % self.slug
    
    def get_share_url(self):
        """
        The link we can use for share buttons.
        """
        return self.get_absolute_url()
    
    def get_tablefu_opts(self):
        return yaml.load(self.yaml_data).get('column_options', {})
    
    def get_tablefu(self):
        """
        Trick the data out with TableFu.
        """
        import os
        import csv
        from django.conf import settings
        from django.utils import simplejson
        path = os.path.join(settings.CSV_DIR, self.csv_name)
        data = open(path, 'r')
        return TableFu(data, **self.get_tablefu_opts())
    
    def get_rendered_tag_list(self, html=True, conjunction='and'):
        """
        Return a rendered list of tags.
        
        By default a HTML link list that's ready for the table detail page.
        """
        from django.utils.text import get_text_list
        tag_list = list(self.tags.all())
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
        tag_list = list(self.tags.all())
        tag_list.sort(key=lambda x: x.title)
        return ", ".join([i.title.lower() for i in tag_list])


class Tag(models.Model):
    """
    A descriptive label connected to a table.
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    objects = TagManager()
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return u'/tag/%s/page/1/' % self.slug

