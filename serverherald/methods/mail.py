from serverherald.methods.base import ServerHerald


class ServerHeraldEmail(ServerHerald):
    """Parent class for sending email notifications.
    This doesn't supply notify() and should not be used directly.
    """

    def validate_config(self):
        """Email notifications require a `to` and `from` address"""
        ServerHerald.validate_config(self)

        email = self.config.get('email')
        if not email or not email.get('to'):
            print 'There are no recipient email addresses in the config file'
            sys.exit(1)

        if not email.get('from'):
            print 'A from address has not been specified in the config file'
            sys.exit(1)

    def get_subject(self):
        return self.config['email'].get('subject',
                                        'New Cloud Server Online')

    def get_message(self, context):
        template = self.template_env.get_template('message')
        return template.render(context)

    def get_recipients(self):
        if not isinstance(self.config['email']['to'], list):
            self.config['email']['to'] = [self.config['email']['to']]
        return self.config['email']['to']
