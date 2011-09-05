from django.db import models


class TableManager(models.Manager):
    """
    A few tricks we'll use with our tables.
    """
    def live(self):
        """
        Returns only Tables that are ready to publish.
        """
        return self.filter(is_published=True, show_in_feeds=True)


class TableLiveManager(models.Manager):
    """
    Returns only Tables that are ready to publish.
    """
    def get_query_set(self):
        qs = super(TableLiveManager, self).get_query_set()
        return qs.filter(is_published=True, show_in_feeds=True)
