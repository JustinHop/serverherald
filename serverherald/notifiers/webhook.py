import sys
import json
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyWebhook(ServerHeraldNotifyBase):
    """Class for sending notifications as a HTTP(S) POST to a specified URL"""

    def validate_config(self):
        ServerHeraldNotifyBase.validate_config(self)

        # Webhook requires a URL
        webhook = self.config.get('webhook')
        if not webhook:
            print ('`webhook` notification type requires a URL to be '
                   'specified in the config file.')
            sys.exit(1)

        if not webhook.get('url'):
            print 'Webhook requires a URL in the config file'
            sys.exit(1)

    def notify(self, context):
        url = self.config['webhook'].get('url')
        r = requests.post(url,
                          data=json.dumps(self.render_template('webhook',
                                                               context)))
        if r.status_code != 200:
            print 'Webhook Error: (%d) %s' % (r.status_code, r.text)
