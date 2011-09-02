import os
import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    
    def handle(self, *args, **kwds):
        """
        Start a runserver that serves the contents of your build directory.
        """
        cmd = "s3cmd sync --delete-removed --acl-public %s/ s3://%s"
        subprocess.call(cmd % (settings.BUILD_DIR, settings.AWS_BUCKET_NAME),
            shell=True)
