from table_stacker.models import Table
from bakery.views import BuildableDetailView, BuildableListView


class TableListView(BuildableListView):
    """
    A list of all tables.
    """
    queryset = Table.live.all()


class TableDetailView(BuildableDetailView):
    """
    All about one table.
    """
    queryset = Table.live.all()
    
    def get_context_data(self, **kwargs):
        context = super(TableDetailView, self).get_context_data(**kwargs)
        context.update({
            'size_choices': [1,2,3,4],
            'table': context['object'].get_tablefu(),
        })
        return context
