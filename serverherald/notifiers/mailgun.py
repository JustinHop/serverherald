import sys
import requests

from serverherald.notifiers.mail import ServerHeraldNotifyEmail


class ServerHeraldNotifyMailgun(ServerHeraldNotifyEmail):
    """Class for sending email notifications via Mailgun API"""

    def validate_config(self):
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
        url = ('https://api.mailgun.net/v2/%s/messages' %
               self.config['mailgun'].get('domain'))
        r = requests.post(url,
                          auth=('api', self.config['mailgun'].get('apikey')),
                          data={'from': self.config['email']['from'],
                                'to': self.get_recipients(),
                                'subject': self.get_subject(),
                                'text': self.render_template('message',
                                                             context)})
        if r.status_code != 200:
            print 'Mailgun API Error: (%d) %s' % (r.status_code, r.text)
