import sys
import json
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyWebhook(ServerHeraldNotifyBase):
    """Class for sending notifications as a HTTP(S) POST to a specified URL"""

    def validate_config(self):
        """Verify that all required config settings are present"""

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
        """Send HTTP(S) notification"""
        url = self.config_get('webhook', 'url')
        response = requests.post(url,
                                 data=json.dumps(
                                     self.render_template('webhook',
                                                          context)))
        if response.status_code != 200:
            print 'Webhook Error: (%d) %s' % (response.status_code,
                                              response.text)
