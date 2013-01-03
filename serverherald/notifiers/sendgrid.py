import sys
import requests

from serverherald.notifiers.mail import ServerHeraldNotifyEmail


class ServerHeraldNotifySendgrid(ServerHeraldNotifyEmail):
    """Class for sending email notifications via Sendgrid API"""

    def validate_config(self):
        """Verify that all required config settings are present"""

        ServerHeraldNotifyEmail.validate_config(self)

        # Sendgrid requires an API key and API username
        sgconfig = self.config.get('sendgrid')
        if not sgconfig:
            print ('`sendgrid` notification type requires an API username'
                   ' and an API key to be specified in the config file.')
            sys.exit(1)

        if not sgconfig.get('apiuser'):
            print 'Sendgrid requires a domain name in the config file.'
            sys.exit(1)

        if not sgconfig.get('apikey'):
            print 'Sendgrid requires an API key in the config file'
            sys.exit(1)

    def notify(self, context):
        """Send email notification"""
        url = 'https://sendgrid.com/api/mail.send.json'
        data = {'api_user': self.config_get('sendgrid', 'apiuser'),
                'api_key': self.config_get('sendgrid', 'apikey'),
                'to': self.get_recipients(),
                'from': self.config_get('email', 'from'),
                'subject': self.get_subject(),
                'text': self.render_template('message', context)}

        response = requests.post(url, data=data)

        if response.status_code != 200:
            print 'Sendgrid API Error: (%d) %s' % (response.status_code,
                                                   response.text)
