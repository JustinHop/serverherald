import smtplib
from email.mime.text import MIMEText

from serverherald.notifiers.mail import ServerHeraldNotifyEmail


class ServerHeraldNotifySMTP(ServerHeraldNotifyEmail):
    """Class for sending email notifications via SMTP"""

    def notify(self, context):
        """Send email notification"""
        email = MIMEText(self.render_template('message', context))
        email['Subject'] = self.get_subject()
        email['From'] = self.config('email', 'from')
        email['To'] = ', '.join(self.get_recipients())
        sender = smtplib.SMTP()
        sender.connect()
        sender.sendmail(email['From'], self.get_recipients(),
                        email.as_string())
        sender.quit()
