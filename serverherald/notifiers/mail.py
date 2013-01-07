import sys
from serverherald.notifiers.base import ServerHeraldNotifyBase


class ServerHeraldNotifyEmail(ServerHeraldNotifyBase):
    """Parent class for sending email notifications.
    This doesn't supply notify() and should not be used directly.
    """

    def validate_config(self):
        """Email notifications require a `to` and `from` address"""
        ServerHeraldNotifyBase.validate_config(self)

        if not self.config_has('email') or self.config_has('email', 'to'):
            print 'There are no recipient email addresses in the config file'
            sys.exit(1)

        if not self.config_has('email', 'from'):
            print 'A from address has not been specified in the config file'
            sys.exit(1)

    def get_subject(self):
        """Set the email subject based on config, fall back to default"""
        return self.config('email', 'subject', 'New Cloud Server Online')

    def get_recipients(self):
        """Convert recipients from the config file into a list, if needed"""
        recipients = self.config('email', 'to')
        if not isinstance(recipients, list):
            recipients = [recipients]
        return recipients
