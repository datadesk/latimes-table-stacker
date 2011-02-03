from datetime import datetime
from table_stacker.models import Table
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist


class LatestTables(Feed):
    title = "Recent spreadsheets from the Los Angeles Times"
    link = "http://spreadsheets.latimes.com"
    description = "The latest spreadsheets from the Los Angeles Times."
    title_template = "feeds/table_title.html"
    description_template = "feeds/table_description.html"

    def items(self):
        return Table.all().filter("is_published =", True).order("-publication_date")[:10]

    def item_pubdate(self, item):
        return datetime(*(item.publication_date.timetuple()[:6]))
