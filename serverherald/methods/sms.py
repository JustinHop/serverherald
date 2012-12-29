from serverherald.methods.base import RSNGCSNotify


class RSNGCSNotifySMS(RSNGCSNotify):

    def notify(self, context):
        print 'Sent you a txt, did you get it?'

    def validate_config(self):
        RSNGCSNotify.validate_config(self)
        # TODO: Check for carrier, phone number, etc
