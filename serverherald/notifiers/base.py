import sys
from jinja2 import Environment, PackageLoader


class ServerHeraldNotifyBase(object):

    """Class for querying current cloud servers and sending
    notifications for new servers
    """

    def __init__(self, config):
        """Initialize the class by setting the path to the config file,
        checking file and directory locations and parsing the config file

        """

        self.config = config

        self.validate_config()
        self.template_env = Environment(loader=PackageLoader('serverherald',
                                        'templates'))

    def validate_config(self):
        """Load the config.yaml file and validate it's contents within
        reason"""

        if not self.config:
            print 'The config file is empty and must be populated'
            sys.exit(1)

        accounts = self.config.get('accounts')
        if not accounts or not accounts.keys():
            print 'There are no accounts configured in the config file'
            sys.exit(1)

        for account, settings in accounts.iteritems():
            if 'apikey' not in settings:
                print 'Account %s does not have an API key' % account
                sys.exit(1)
