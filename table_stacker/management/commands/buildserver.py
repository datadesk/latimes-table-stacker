import urls
from django.conf import settings
from django.conf.urls.defaults import *
from django.core.management.commands import runserver


class Command(runserver.Command):
    
    def handle(self, *args, **kwds):
        """
        Start a runserver that serves the contents of your build directory.
        """
        urls.urlpatterns = patterns("toolbox.views",
        url(r"^(.*)$", "static.serve", {
            "document_root": settings.BUILD_DIR,
            'show_indexes': False,
            'default': 'index.html'
            }),
        )
        runserver.Command.handle(self, *args, **kwds)
