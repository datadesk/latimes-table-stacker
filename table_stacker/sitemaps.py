from models import Table
from bakery.views import BuildableListView


class SitemapView(BuildableListView):
    """
    A list of all tables in a Sitemap ready for Google.
    """
    build_path = 'sitemap.xml'
    template_name = 'sitemap.xml'
    queryset = Table.live.all()
    
    def render_to_response(self, context):
        return super(SitemapView, self).render_to_response(
            context,
            content_type='text/xml'
        )
