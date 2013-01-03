import sys
import json
import requests

from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyPagerduty(ServerHeraldNotifyBase):
    """Class for sending event notifications via PagerDuty API"""

    def validate_config(self):
        ServerHeraldNotifyBase.validate_config(self)

        # PagerDuty requires an API key
        pdconfig = self.config.get('pagerduty')
        if not pdconfig:
            print ('`pagerduty` notification type requires a PagerDuty API '
                   'key to be specified in the config file.')
            sys.exit(1)

        if not pdconfig.get('apikey'):
            print 'PagerDuty requires an API key in the config file'
            sys.exit(1)

    def notify(self, context):
        url = ('https://events.pagerduty.com'
               '/generic/2010-04-15/create_event.json')
        description = 'Server %s online' % context['server'].name
        data = {'service_key': self.config['pagerduty'].get('apikey'),
                'event_type': 'trigger',
                'description': description,
                'details': self.render_template('pagerduty', context)}

        r = requests.post(url, data=json.dumps(data))

        if r.status_code != 200:
            print 'PagerDuty API Error: (%d) %s' % (r.status_code, r.text)
