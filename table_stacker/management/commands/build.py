import os
import yaml
from django.conf import settings
from table_stacker.models import Table
from toolbox.FileIterator import FileIterator
from bakery.management.commands.build import Command as BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Load all YAML files into the local database
        self.stdout.write("Building database\n")
        [Table.objects.update_or_create(i) for i in self.get_all_yaml()]
        super(Command, self).handle(*args, **options)

    def get_yaml(self, yaml_name):
        """
        Retrieves the yaml file with the provided name as a Python object.
        """
        yaml_path = os.path.join(settings.YAML_DIR, yaml_name)
        try:
            yaml_data = open(yaml_path)
        except:
            raise YAMLDoesNotExistError(
                "YAML file could not be opened: %s" % yaml_name
            )
        try:
            yaml_obj = yaml.load(yaml_data)['table']
            yaml_obj['yaml_name'] = yaml_name
        except:
            raise InvalidYAMLError("YAML file is improperly formatted.")
        yaml_data.close()
        return yaml_obj

    def get_all_yaml(self):
        """
        Returns a list of all the tables configured in the YAML_DIR
        in dictionary form.
        """
        file_list = FileIterator(settings.YAML_DIR)
        yaml_list = [i for i in file_list if i.endswith('.yaml')]
        return [self.get_yaml(i) for i in yaml_list]


class YAMLDoesNotExistError(Exception):
    """
    Called when you try to open a YAML that doesn't exist.
    """
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class InvalidYAMLError(Exception):
    """
    Called when your YAML doesn't get with the program.
    """
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)
