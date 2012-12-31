import sys
import json
import requests

from serverherald.methods.base import RSNGCSNotify


class RSNGCSNotifyPagerduty(RSNGCSNotify):
    """Class for sending push notifications via PagerDuty API"""

    def validate_config(self):
        RSNGCSNotify.validate_config(self)

        # PagerDuty requires an API key
        pdconfig = self.config.get('pagerduty')
        if not pdconfig:
            print '`pagerduty` notification type requires a PagerDuty API ' \
                  'key to bespecified in the config file.'
            sys.exit(1)

        if not pdconfig.get('apikey'):
            print 'PagerDuty requires an API key in the config file'
            sys.exit(1)

    def get_details(self, context):
        template = self.template_env.get_template('pagerduty')
        return template.render(context)

    def notify(self, context):
        if self.silent:
            return

        url = 'https://events.pagerduty.com' \
              '/generic/2010-04-15/create_event.json'
        description = 'Server %s online' % context['server'].name
        data = {'service_key': self.config['pagerduty'].get('apikey'),
                'event_type': 'trigger',
                'description': description,
                'details': self.get_details(context)}

        r = requests.post(url, data=json.dumps(data))

        if r.status_code != 200:
            print 'PagerDuty API Error: (%d) %s' % (r.status_code, r.text)
