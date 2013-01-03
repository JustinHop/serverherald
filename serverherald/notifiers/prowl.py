import os
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

    def notify(self, context):
        message = self.render_template('prowl', context)
        url = 'https://api.prowlapp.com/publicapi/add'
        r = requests.post(url,
                          data={'apikey': self.config['prowl'].get('apikey'),
                                'priority':
                                self.config['prowl'].get('priority', 0),
                                'application': 'Server Herald',
                                'event': 'New Server',
                                'description': self.render_template('prowl',
                                                                    context)})
        if r.status_code != 200:
            print 'Prowl API Error: (%d) %s' % (r.status_code, r.text)
