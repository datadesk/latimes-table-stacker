from models import Table
from bakery.views import BuildableListView


class LatestTablesFeed(BuildableListView):
    build_path = 'feeds/latest.xml'
    template_name = 'table_stacker/feeds/latest.xml'
    queryset = Table.live.all()[:10]
