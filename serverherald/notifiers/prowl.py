import sys
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyProwl(ServerHeraldNotifyBase):
    """Class for sending push notifications via Prowl API"""

    def validate_config(self):
        """Verify that all required config settings are present"""

        ServerHeraldNotifyBase.validate_config(self)

        # Prowl requires an API key
        if not self.config_has('prowl'):
            print ('`prowl` notification type requires a Prowl API key to be '
                   'specified in the config file.')
            sys.exit(1)

        if not self.config_has('prowl', 'apikey'):
            print 'Prowl requires an API key in the config file'
            sys.exit(1)

    def notify(self, context):
        """Send message notification"""
        url = 'https://api.prowlapp.com/publicapi/add'

        data = {'apikey': self.config('prowl', 'apikey'),
                'priority': self.config('prowl', 'priority', 0),
                'application': 'Server Herald',
                'event': 'New Server',
                'description': self.render_template('prowl', context)}

        response = requests.post(url, data=data)
        if response.status_code != 200:
            print 'Prowl API Error: (%d) %s' % (response.status_code,
                                                response.text)
