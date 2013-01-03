import getpass
import keyring
import os
import sys
from jinja2 import Environment, PackageLoader, FileSystemLoader


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

    def config_get(self, section, key, default=None):
        """Return value that matches key in config settings.
        Reference keyring if needed.
        """
        config_section = self.config.get(section)
        if config_section.get(key, default) == 'USE_KEYRING':
            keyring_path = section + '/' + key
            keyring_value = keyring.get_password('serverherald', keyring_path)
            if keyring_value is None:
                print 'The keyring storage mechanism has been selected for ' \
                      '%s value but the keyring is empty' % keyring_path

                while 1:
                    user_value = getpass.getpass("%s: " % key)
                    print 'SECRET VALUE: |%s|' % user_value
                    if user_value != '':
                        keyring.set_password('serverherald', keyring_path, user_value)
                        break
                return user_value
        else:
            return config_section.get(key, default)

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
