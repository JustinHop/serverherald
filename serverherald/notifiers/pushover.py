import sys
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyPushover(ServerHeraldNotifyBase):
    """Class for sending push notifications via Pushover API"""

    def validate_config(self):
        """Verify that all required config settings are present"""

        ServerHeraldNotifyBase.validate_config(self)

        # Pushover requires an API key
        if not self.config_has('pushover'):
            print ('`pushover` notification type requires a Pushover API '
                   'key to be specified in the config file.')
            sys.exit(1)

        if not self.config_has('pushover', 'apikey'):
            print 'Pushover requires an API key in the config file'
            sys.exit(1)

    def notify(self, context):
        """Send message notification"""
        app_apikey = 'oPlGyPwBxgd5EicP1qocGV6bYi5RgF'
        url = 'https://api.pushover.net/1/messages.json'
        data = {'token': app_apikey,
                'user': self.config('pushover', 'apikey'),
                'message': self.render_template('sms', context)}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print 'Pushover API Error: (%d) %s' % (response.status_code,
                                                   response.text)
