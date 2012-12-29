import requests

from serverherald.methods.mail import RSNGCSNotifyEmail


class RSNGCSNotifyMailgun(RSNGCSNotifyEmail):
    """Class for sending email notifications via Mailgun API"""

    def validate_config(self):
        RSNGCSNotifyEmail.validate_config(self)

        # Mailgun requires a domain name and API key
        mgconfig = self.config.get('mailgun')
        if not mgconfig:
            print '`mailgun` notification type requires a Mailgun domain and' \
                  ' API key to be specified in the config file.'
            sys.exit(1)

        if not mgconfig.get('domain'):
            print 'Mailgun requires a domain name in the config file.'
            sys.exit(1)

        if not mgconfig.get('apikey'):
            print 'Mailgun requires an API key in the config file'
            sys.exit(1)

    def notify(self, context):
        if self.silent:
            return

        message = self.get_message(context)
        url = 'https://api.mailgun.net/v2/%s/messages' % \
            self.config['mailgun'].get('domain')
        r = requests.post(url,
                          auth=('api', self.config['mailgun'].get('apikey')),
                          data={'from': self.config['email']['from'],
                                'to': self.get_recipients(),
                                'subject': self.get_subject(),
                                'text': message})
        if r.status_code != 200:
            print 'Mailgun API Error: (%d) %s' % (r.status_code, r.text)
