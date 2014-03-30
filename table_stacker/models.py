import os
import yaml
from table_fu import TableFu
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.sites.models import Site
from managers import TableLiveManager, TableManager


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
    publication_time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    legend = models.CharField(max_length=500, blank=True)
    footer = models.TextField(blank=True)
    sources = models.TextField(blank=True)
    credits = models.TextField(blank=True)
    show_download_links = models.BooleanField(default=True)
    show_search_field = models.BooleanField(default=True)
    # The meta
    is_published = models.BooleanField()
    show_in_feeds = models.BooleanField(default=True)
    objects = TableManager()
    live = TableLiveManager()

    class Meta:
        ordering = ("-publication_date", "-publication_time")

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('table-detail', [self.slug])

    @models.permalink
    def get_csv_url(self):
        return ('table-csv', [self.slug])

    @models.permalink
    def get_xls_url(self):
        return ('table-xls', [self.slug])

    @models.permalink
    def get_json_url(self):
        return ('table-json', [self.slug])

    def get_share_url(self):
        """
        The link we can use for share buttons.
        """
        site = Site.objects.get_current()
        return 'http://%s%s' % (site.domain, self.get_absolute_url())

    def get_tablefu_opts(self):
        return yaml.load(self.yaml_data).get('column_options', {})

    def get_tablefu(self):
        """
        Trick the data out with TableFu.
        """
        path = os.path.join(settings.CSV_DIR, self.csv_name)
        data = open(path, 'r')
        return TableFu(data, **self.get_tablefu_opts())
    tablefu = property(get_tablefu)

    def get_publication_datetime(self):
        """
        Combine publication date and time where possible.
        """
        if not self.publication_time:
            return datetime(
                self.publication_date.year,
                self.publication_date.month,
                self.publication_date.day,
                0, 0, 0
            )
        else:
            return datetime.combine(
                self.publication_date,
                self.publication_time
            )
    publication_datetime = property(get_publication_datetime)
