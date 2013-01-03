import sys
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyPushover(ServerHeraldNotifyBase):
    """Class for sending push notifications via Pushover API"""

    def validate_config(self):
        ServerHeraldNotifyBase.validate_config(self)

        # Pushover requires an API key
        pushoverconfig = self.config.get('pushover')
        if not pushoverconfig:
            print ('`pushover` notification type requires a Pushover API '
                   'key to be specified in the config file.')
            sys.exit(1)

        if not pushoverconfig.get('apikey'):
            print 'Pushover requires an API key in the config file'
            sys.exit(1)

    def notify(self, context):
        APPLICATION_APIKEY = 'oPlGyPwBxgd5EicP1qocGV6bYi5RgF'
        url = 'https://api.pushover.net/1/messages.json'
        r = requests.post(url,
                          data={'token': APPLICATION_APIKEY,
                                'user': self.config['pushover'].get('apikey'),
                                'message': self.render_template('sms',
                                                                context)})
        if r.status_code != 200:
            print 'Pushover API Error: (%d) %s' % (r.status_code, r.text)
