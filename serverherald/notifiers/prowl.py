import sys
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyProwl(ServerHeraldNotifyBase):
    """Class for sending push notifications via Prowl API"""

    def validate_config(self):
        ServerHeraldNotifyBase.validate_config(self)

        # Prowl requires an API key
        prowlconfig = self.config.get('prowl')
        if not prowlconfig:
            print ('`prowl` notification type requires a Prowl API key to be '
                   'specified in the config file.')
            sys.exit(1)

        if not prowlconfig.get('apikey'):
            print 'Prowl requires an API key in the config file'
            sys.exit(1)

    def get_message(self, context):
        template = self.template_env.get_template('prowl')
        return template.render(context)

    def notify(self, context):
        message = self.get_message(context)
        url = 'https://api.prowlapp.com/publicapi/add'
        r = requests.post(url,
                          data={'apikey': self.config['prowl'].get('apikey'),
                                'priority':
                                self.config['prowl'].get('priority', 0),
                                'application': 'Server Herald',
                                'event': 'New Server',
                                'description': message})
        if r.status_code != 200:
            print 'Prowl API Error: (%d) %s' % (r.status_code, r.text)
