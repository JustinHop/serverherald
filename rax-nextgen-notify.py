#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2012 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
A script intended to be run via cron for sending notification emails as new
Rackspace NextGen cloud servers become ACTIVE.
"""

import pyrax
import yaml
import json
import sys
import os
import smtplib
import getpass
import argparse
from email.mime.text import MIMEText


class RSNGCSNotify:

    """Class for querying current cloud servers and sending email
    notifications for new servers
    """

    def __init__(self, silent=False):
        """Initialize the class by setting the path to the config file,
        checking file and directory locations and parsing the config file

        silent (boolean) specifies whether or not to send email notifications
        (optional)

        """

        self.silent = silent

        self.configFile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'config.yaml')

        self.checkFiles()
        self.loadConfig()

    def checkFiles(self):
        """Check for the existence of the config.yaml file and validate that
        we can write to to the directory where the script lives for
        purposes of the cache file that will
        be created.
        """

        if not os.path.isfile(self.configFile):
            print 'The config file does not exist at %s' % self.configFile
            sys.exit(1)

        testWriteFile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'writetest')
        try:
            with open(testWriteFile, 'w+') as f:
                f.write('test')
            os.unlink(testWriteFile)
        except IOError:
            print 'It does not appear that the user (%s) this script was ' \
                  'executed as can write to\n%s' % (
                  getpass.getuser(), os.path.dirname(testWriteFile))
            sys.exit(1)

    def loadConfig(self):
        """Load the config.yaml file and validate it's contents within
        reason"""

        with open(self.configFile) as f:
            self.config = yaml.load(f)

        if not self.config:
            print 'The config file is empty and must be populated'
            sys.exit(1)

        email = self.config.get('email')
        if not email or not email.get('to'):
            print 'There are no recipient email addresses in the config file'
            sys.exit(1)

        if not email.get('from'):
            print 'A from address has not been specified in the config file'
            sys.exit(1)

        accounts = self.config.get('accounts')
        if not accounts or not accounts.keys():
            print 'There are no accounts configured in the config file'
            sys.exit(1)

        for account, settings in accounts.iteritems():
            if 'apiKey' not in settings:
                print 'Account %s does not have an API key' % account
                sys.exit(1)
            if 'endpoint' not in settings:
                print 'Account %s does not have an auth endpoint' % account
                sys.exit(1)

    def notify(self, server):
        """Send notification emails as configured in config.yaml for an
        individual server

        server (dict) A dictionary of server values to populate the email with
        """

        if self.silent:
            return

        if not isinstance(self.config['email']['to'], list):
            self.config['email']['to'] = [self.config['email']['to']]
        message = """New cloud server online.

Cloud Server: %(name)s
IP Addresses: %(ips)s
Image: %(image)s
Type: %(flavor)s

This server is accessible through the control panel at:

https://mycloud.rackspace.com/a/%(username)s/#compute,cloudServersOpenStack,%(region)s/%(id)s

Note: Your Cloud Server does not get backed up until you configure and
schedule backups. To learn how, please visit the following knowledge base
article:

http://www.rackspace.com/knowledge_center/index.php/Configuring_Backups

Additional Resources:
Knowledge Base: http://www.rackspace.com/knowledge_center/
API Developer Guide: http://docs.rackspacecloud.com/servers/api/cs-devguide-latest.pdf
Cloud Tools: http://www.rackspace.com/cloud/tools/

If you have any questions or received this message in error, please let us
know.

Best Regards,
The Rackspace Cloud
US Toll Free: 1.877.934.0407
International: +1.210.581.0407
UK: 0800-083-3012""" % server
        email = MIMEText(message)
        email['Subject'] = 'New Cloud Server Online'
        email['From'] = self.config['email']['from']
        email['To'] = ', '.join(self.config['email']['to'])
        s = smtplib.SMTP()
        s.connect()
        s.sendmail(email['From'], self.config['email']['to'],
                   email.as_string())
        s.quit()

    def checkForServers(self):
        """Check all regions for an Auth endpoint querying for all servers,
        sending notifications for new servers in ACTIVE status
        """
        serversFile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'servers.json')
        if not os.path.isfile(serversFile):
            lastServers = {}
        else:
            with open(serversFile) as f:
                lastServers = json.load(f)
        servers = {}
        for username, details in self.config['accounts'].items():
            endpoint = details.get('region', 'DFW')
            if endpoint == 'LON':
                pyrax.default_region = 'LON'
            pyrax.set_credentials(username, details.get('apiKey'))
            if pyrax.identity.auth_endpoint == pyrax.identity.uk_auth_endpoint:
                regions = ['LON']
            else:
                regions = ['DFW', 'ORD']

            for region in regions:
                try:
                    cs = pyrax.connect_to_cloudservers(region)
                except:
                    continue
                flavors = cs.flavors.list()
                images = cs.images.list()
                for server in cs.servers.list():
                    id = server.id
                    status = server.status
                    public_ips = server.addresses['public']
                    ips = ', '.join([ver['addr'] for ver in public_ips])
                    try:
                        image = filter(lambda x: x.id == server.image['id'],
                                       images)[0].name
                    except IndexError:
                        image = cs.images.get(server.image['id']).name
                    flavor = filter(lambda x: int(x.id) == int(
                                    server.flavor['id']), flavors)[0].name
                    if username not in servers:
                        servers[username] = []
                    if username not in lastServers:
                        lastServers[username] = []
                    servers[username].append(id)
                    if status == 'ACTIVE' and id not in lastServers[username]:
                        self.notify(
                            dict(id=id, status=status, name=server.name,
                                 image=image, flavor=flavor, ips=ips,
                                 username=username, region=region))

        with open(serversFile, 'wb+') as f:
            json.dump(servers, f)


def main():
    description = """A script intended to be run via cron for sending
notification emails as new Rackspace NextGen cloud servers become ACTIVE.
---------------------------------------------------------------------------"""

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-s', '--silent', action='store_true', default=False,
                        help='Run silently, not sending any notification '
                             'emails. Useful for the initial run to build '
                             'a baseline of current servers')

    args = parser.parse_args()

    notify = RSNGCSNotify(silent=args.silent)
    notify.checkForServers()

if __name__ == '__main__':
    main()
