import sys
import json
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyNexmo(ServerHeraldNotifyBase):
    """Class for sending SMS notifications via Nexmo API"""

    def validate_config(self):
        ServerHeraldNotifyBase.validate_config(self)

        # Nexmo requires an API key, API secret, a from and a to phone
        # number
        nconfig = self.config.get('nexmo')
        if not nconfig:
            print ('`nexmo` notification type requires a nexmo API key, API '
                   'secret, a recipient and a sending phone number to be '
                   'specified in the config file.')
            sys.exit(1)

        required_fields = {
            'apikey': 'nexmo requires an API key in the config file',
            'apisecret': 'nexmo requires an API secret in the config file',
            'from': ('nexmo requires a sending name or number in the config'
                     'file'),
            'to': 'nexmo requires a recipient phone number in the config file'}

        for field, message in required_fields.iteritems():
            if not nconfig.get(field):
                print message
                sys.exit(1)

    def notify(self, context):
        url = 'https://rest.nexmo.com/sms/json'
        data = {'api_key': self.config['nexmo'].get('apikey'),
                'api_secret': self.config['nexmo'].get('apisecret'),
                'from': self.config['nexmo'].get('from'),
                'to': self.config['nexmo'].get('to'),
                'text': self.render_template('sms', context)}

        r = requests.post(url, data=data)

        if r.status_code != 200:
            print 'nexmo API Error: (%d) %s' % (r.status_code, r.text)
        else:
            """Nexmo API returns 200 for application errors too"""
            for message in r.json()['messages']:
                if message['status'] != "0":
                    print 'nexmo API Error: %s' % message['error-text']
