import sys
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyTwilio(ServerHeraldNotifyBase):
    """Class for sending SMS notifications via Twilio API"""

    def validate_config(self):
        """Verify that all required config settings are present"""

        ServerHeraldNotifyBase.validate_config(self)

        # Twilio requires an Account SID, a token, a from, and a to phone
        # number
        if not self.config_has('twilio'):
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
            if not self.config_has('twilio', field):
                print message
                sys.exit(1)

    def notify(self, context):
        """Send SMS notification"""
        url = ('https://api.twilio.com/2010-04-01/Accounts'
               '/%s/SMS/Messages.json' %
               self.config('twilio', 'accountsid'))
        data = {'From': self.config('twilio', 'from'),
                'To': self.config('twilio', 'to'),
                'Body': self.render_template('sms', context)}

        response = requests.post(url, data=data,
                                 auth=(self.config('twilio',
                                                   'accountsid'),
                                       self.config('twilio', 'token')))

        if response.status_code not in [200, 201]:
            print 'Twilio API Error: (%d) %s' % (response.status_code,
                                                 response.text)
