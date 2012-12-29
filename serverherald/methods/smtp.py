import smtplib
#from email.mime.text import MIMEText

from serverherald.methods.mail import RSNGCSNotifyEmail


class RSNGCSNotifySMTP(RSNGCSNotifyEmail):
    """Class for sending email notifications via SMTP"""

    def notify(self, context):
        if self.silent:
            return

        email = MIMEText(self.get_message(context))
        email['Subject'] = self.get_subject()
        email['From'] = self.config['email']['from']
        email['To'] = ', '.join(self.get_recipients())
        s = smtplib.SMTP()
        s.connect()
        s.sendmail(email['From'], self.get_recipients(), email.as_string())
        s.quit()
