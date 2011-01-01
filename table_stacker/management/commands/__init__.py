import os
import yaml
import getpass
from django.conf import settings
from optparse import make_option


def auth_func():
    """
    Quickie method for logging in to the remote api. From GAE docs.
    """
    return raw_input('Username:'), getpass.getpass('Password:')


def get_app_id():
    """
    Retrieves the id of the current app.
    """
    path = os.path.join(settings.ROOT_PATH, 'app.yaml')
    yaml_data = yaml.load(open(path))
    return yaml_data['application']


# Command-line options common to our custom commands
custom_options = (
    make_option(
        "--host",
        action="store",
        dest="host",
        default=None,
        help="specify the host to update, defaults to <app_id>.appspot.com"
    ),
)
