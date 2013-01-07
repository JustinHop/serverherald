import os
import sys
from jinja2 import Environment, PackageLoader, FileSystemLoader

import serverherald.utils


class ServerHeraldNotifyBase(object):

    """Class for querying current cloud servers and sending
    notifications for new servers
    """

    def __init__(self, config):
        """Initialize the class by setting the path to the config file,
        checking file and directory locations and parsing the config file

        """

        self._config = config

        self.validate_config()
        self.template_env = Environment(loader=PackageLoader('serverherald',
                                        'templates'))

    def config(self, section, key=None, default=None):
        """Return the section or section/key value"""
        return serverherald.utils.config_get(self._config, section, key,
                                             default)

    def config_has(self, section, key=None):
        """Return true if the section/key pair exists"""
        return serverherald.utils.config_has(self._config, section, key)

    def validate_config(self):
        """Load the config.yaml file and validate it's contents within
        reason"""

        """
        if not self.config:
            print 'The config file is empty and must be populated'
            sys.exit(1)
        """

        accounts = self.config('accounts')
        if not accounts or not accounts.keys():
            print 'There are no accounts configured in the config file'
            sys.exit(1)

        for account, settings in accounts.iteritems():
            if 'apikey' not in settings:
                print 'Account %s does not have an API key' % account
                sys.exit(1)

    def render_template(self, templatename, context):
        """Render the template based on the data context.

        Users can override by creating ~/.serverherald/templates/templatename
        """
        template_dir = os.path.join(os.path.expanduser('~/.serverherald'),
                                    'templates')
        if os.path.isfile(os.path.join(template_dir, templatename)):
            template_env = Environment(loader=FileSystemLoader(template_dir))
            template = template_env.get_template(templatename)
            return template.render(context)
        else:
            template = self.template_env.get_template(templatename)
            return template.render(context)
