import sys
import requests

from serverherald.notifiers.mail import ServerHeraldNotifyEmail


class ServerHeraldNotifySendgrid(ServerHeraldNotifyEmail):
    """Class for sending email notifications via Sendgrid API"""

    def validate_config(self):
        """Verify that all required config settings are present"""

        ServerHeraldNotifyEmail.validate_config(self)

        # Sendgrid requires an API key and API username
        if not self.config_has('sendgrid'):
            print ('`sendgrid` notification type requires an API username'
                   ' and an API key to be specified in the config file.')
            sys.exit(1)

        if not self.config_has('sendgrid', 'apiuser'):
            print 'Sendgrid requires a domain name in the config file.'
            sys.exit(1)

        if not self.config_has('sendgrid', 'apikey'):
            print 'Sendgrid requires an API key in the config file'
            sys.exit(1)

    def notify(self, context):
        """Send email notification"""
        url = 'https://sendgrid.com/api/mail.send.json'
        data = {'api_user': self.config('sendgrid', 'apiuser'),
                'api_key': self.config('sendgrid', 'apikey'),
                'to': self.get_recipients(),
                'from': self.config('email', 'from'),
                'subject': self.get_subject(),
                'text': self.render_template('message', context)}

        response = requests.post(url, data=data)

        if response.status_code != 200:
            print 'Sendgrid API Error: (%d) %s' % (response.status_code,
                                                   response.text)
