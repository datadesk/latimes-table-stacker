import os
import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Syncs the build directory with the Amazon S3 bucket defined in settings.py"
    
    def handle(self, *args, **kwds):
        cmd = "s3cmd sync --delete-removed --acl-public %s/ s3://%s"
        subprocess.call(cmd % (settings.BUILD_DIR, settings.AWS_BUCKET_NAME),
            shell=True)
