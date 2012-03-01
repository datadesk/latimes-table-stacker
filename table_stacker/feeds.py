from models import Table
from bakery.views import BuildableListView


class LatestTablesFeed(BuildableListView):
    build_path = 'feeds/latest.xml'
    template_name = 'table_stacker/feeds/latest.xml'
    queryset = Table.live.all()[:10]
    
    def render_to_response(self, context):
        return super(LatestTablesFeed, self).render_to_response(
            context,
            content_type='text/xml'
        )
