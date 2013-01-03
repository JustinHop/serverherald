import sys
import requests

from serverherald.notifiers.mail import ServerHeraldNotifyEmail


class ServerHeraldNotifyMailgun(ServerHeraldNotifyEmail):
    """Class for sending email notifications via Mailgun API"""

    def validate_config(self):
        """Verify that all required config settings are present"""

        ServerHeraldNotifyEmail.validate_config(self)

        # Mailgun requires a domain name and API key
        mgconfig = self.config.get('mailgun')
        if not mgconfig:
            print ('`mailgun` notification type requires a Mailgun domain and'
                   ' API key to be specified in the config file.')
            sys.exit(1)

        if not mgconfig.get('domain'):
            print 'Mailgun requires a domain name in the config file.'
            sys.exit(1)

        if not mgconfig.get('apikey'):
            print 'Mailgun requires an API key in the config file'
            sys.exit(1)

    def notify(self, context):
        """Send email notification"""
        url = ('https://api.mailgun.net/v2/%s/messages' %
               self.config_get('mailgun', 'domain'))
        data = {'token': app_apikey,
                'user': self.config_get('pushover', 'apikey'),
                'message': self.render_template('sms', context)}
        response = requests.post(url, data=data,
                                 auth=('api', self.config_get('mailgun',
                                       'apikey')))
        if response.status_code != 200:
            print 'Mailgun API Error: (%d) %s' % (response.status_code,
                                                  response.text)
