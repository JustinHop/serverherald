import sys
import json
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyTwilio(ServerHeraldNotifyBase):
    """Class for sending SMS notifications via Twilio API"""

    def validate_config(self):
        ServerHeraldNotifyBase.validate_config(self)

        # Twilio requires an Account SID, a token, a from, and a to phone
        # number
        tconfig = self.config.get('twilio')
        if not tconfig:
            print ('`twilio` notification type requires a Twilio Account SID'
                   ', a token, a recipient and a sending phone number to be '
                   'specified in the config file.')
            sys.exit(1)

        required_fields = {
            'accountsid': 'Twilio requires an Account SID in the config file',
            'token': 'Twilio requires a token in the config file',
            'from': ('Twilio requires a sending phone number in the config '
                     'file'),
            'to': ('Twilio requires a recipient phone number in the config '
                   'file')}

        for field, message in required_fields.iteritems():
            if not tconfig.get(field):
                print message
                sys.exit(1)

    def notify(self, context):
        url = ('https://api.twilio.com/2010-04-01/Accounts'
               '/%s/SMS/Messages.json' %
               self.config['twilio'].get('accountsid'))
        data = {'From': self.config['twilio'].get('from'),
                'To': self.config['twilio'].get('to'),
                'Body': self.render_template('sms', context)}

        r = requests.post(url,
                          auth=(self.config['twilio'].get('accountsid'),
                                self.config['twilio'].get('token')),
                          data=data)

        if r.status_code not in [200, 201]:
            print 'Twilio API Error: (%d) %s' % (r.status_code, r.text)
