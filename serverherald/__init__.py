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

import os
import sys
import json
import getpass
import pprint
import pickle

import pyrax
import dateutil.parser

import serverherald.utils

"""
serverherald announces when new Rackspace NextGen cloud server become ACTIVE.
"""


class ServerHerald(object):

    """Class for querying current cloud servers and sending
    notifications for new servers
    """

    def __init__(self, config, notifier, silent=False):
        """Initialize the class by setting the path to the config file,
        checking file and directory locations and parsing the config file

        silent (boolean) specifies whether or not to send email notifications
        (optional)

        """

        self.silent = silent
        self._config = config
        self.notifier = notifier(config)

        self.check_files()

    def config(self, section, key=None, default=None):
        """Return the section or section/key value"""
        return serverherald.utils.config_get(self._config, section, key,
                                             default)

    def config_has(self, section, key=None):
        """Return true if the section/key pair exists"""
        return serverherald.utils.config_has(self._config, section, key)

    def check_files(self):
        """Check for the existence of the config.yaml file and validate that
        we can write to to the directory where the script lives for
        purposes of the cache file that will
        be created.
        """

        local_dir = os.path.expanduser('~/.serverherald')

        if not os.path.isdir(local_dir):
            if os.path.isfile(local_dir):
                print ('%s exists as a file, although it should be a '
                       'directory' % local_dir)
                sys.exit(1)
            try:
                os.makedirs(local_dir, 0700)
            except OSError:
                print 'Could not create the local directory %s' % local_dir
                sys.exit(1)

        test_file = '%s/writetest' % local_dir
        try:
            with open(test_file, 'w+') as f:
                f.write('test')
            os.unlink(test_file)
        except IOError:
            print ('It does not appear that the user (%s) this script was '
                   'executed as can write to\n%s' %
                   (getpass.getuser(), os.path.dirname(test_file)))
            sys.exit(1)

        logger = serverherald.utils.ServerHeraldLogger()
        self.logger = logger.logger(self.config('log'))

        self.lock_file = '%s/lock' % local_dir

        if os.path.isfile(self.lock_file):
            with open(self.lock_file) as f:
                lock_pid = f.read().strip()
            if os.path.isdir('/proc'):
                if os.path.isdir('/proc/%s' % lock_pid):
                    exe = os.readlink('/proc/%s/exe' % lock_pid)
                    if 'python' in exe:
                        print ('serverherald[%s] is currently running' %
                               lock_pid)
                        self.logger.warning('serverherald[%s] is currently '
                                            'running' % lock_pid)
                        sys.exit(1)
                    else:
                        print 'serverherald pid file found, but is not running'
                        self.logger.warning('serverherald pid file found, but '
                                            'is not running')
                        os.unlink(self.lock_file)
            else:
                print 'serverherald lockfile found'
                print 'serverherald cannot check the pid on this OS'
                self.logger.error('serverherald lockfile found')
                self.logger.error('serverherald cannot check the pid on this '
                                  'OS')
                sys.exit(1)

        with open(self.lock_file, 'w+') as f:
            f.write('%s' % os.getpid())

    def check_servers(self):
        """Check all regions for an Auth endpoint querying for all servers,
        sending notifications for new servers in ACTIVE status
        """

        self.logger.info('Starting to look for new servers')

        servers_file = os.path.expanduser('~/.serverherald/servers.json')
        if not os.path.isfile(servers_file):
            last_servers = {}
        else:
            with open(servers_file) as f:
                last_servers = json.load(f)
        servers = {}

        auth_file = os.path.expanduser('~/.serverherald/auth.pickle')
        if not os.path.isfile(auth_file):
            auth_details = {}
        else:
            with open(auth_file) as f:
                try:
                    auth_details = pickle.load(f)
                except EOFError:
                    self.logger.warning("Could not unpickle auth file")
                    os.remove(auth_file)
                    auth_details = {}

        new_servers = 0
        for username, settings in self.config('accounts').iteritems():
            self.logger.info('Username: %s' % username)

            endpoint = settings.get('endpoint', 'US')
            self.logger.info('Endpoint: %s' % endpoint)
            if endpoint == 'LON':
                pyrax.default_region = 'LON'

            if username in auth_details:
                user_auth_details = auth_details[username]
                pyrax.identity.username = username
                pyrax.identity.api_key = settings.get('apikey')
                pyrax.identity.token = user_auth_details.get('token')
                pyrax.identity.expires = dateutil.parser.parse(
                    user_auth_details.get('expires'))
                pyrax.identity.tenant_id = user_auth_details.get('tenant_id')
                pyrax.identity.tenant_name = (user_auth_details.
                                              get('tenant_name'))
                pyrax.identity.services = user_auth_details.get('services')
                pyrax.identity.user = user_auth_details.get('user')
                pyrax.identity.authenticated = True
            else:
                pyrax.set_credentials(username, settings.get('apikey'))
                if pyrax.identity.authenticated:
                    auth_details[username] = {
                        'token': pyrax.identity.token,
                        'expires': pyrax.identity.expires.isoformat(),
                        'tenant_id': pyrax.identity.tenant_id,
                        'tenant_name': pyrax.identity.tenant_name,
                        'services': pyrax.identity.services,
                        'user': pyrax.identity.user}
                    with open(auth_file, 'w+') as f:
                        try:
                            pickle.dump(auth_details, f)
                        except pyrax.exceptions.NoClientForService:
                            self.logger.warning("Failed to dump auth_details")
                            os.remove(auth_file)

            regions = ['DFW', 'ORD']

            for region in regions:
                self.logger.info('Region: %s' % region)
                try:
                    cs = pyrax.connect_to_cloudservers(region)
                except:
                    continue
                flavors = cs.flavors.list()
                images = cs.images.list()
                for server in cs.servers.list():
                    id = server.id
                    status = server.status

                    if username not in servers:
                        servers[username] = []
                    if username not in last_servers:
                        last_servers[username] = []

                    servers[username].append(id)

                    if (status == 'ACTIVE'
                            and id not in last_servers[username]):
                        public_ips = server.addresses.get('public')
                        if public_ips:
                            ips = ', '.join([ver['addr'] for ver in
                                            public_ips])
                        else:
                            ips = 'None'
                        try:
                            image = filter(lambda x: x.id ==
                                           server.image['id'],
                                           images)[0].name
                        except IndexError:
                            image = cs.images.get(server.image['id']).name

                        try:
                            flavor = filter(lambda x: int(x.id) == int(
                                server.flavor['id']), flavors)[0].name
                        except ValueError:
                            self.logger.warning("ValueError on server flavor")
                            flavor = server.flavor['id']

                        context = {'id': id, 'status': status,
                                   'server': server, 'server_image': image,
                                   'flavor': flavor, 'server_ips': ips,
                                   'server_ips_list': public_ips,
                                   'username': username, 'region': region}

                        self.logger.info('New Server: Hostname: (%s) IPs: (%s)'
                                         % (context['server'].name,
                                            context['server_ips']))
                        new_servers += 1
                        if not self.silent:
                            self.notifier.notify(context)

                if cs.client.auth_token != pyrax.identity.token:
                    pyrax.identity.token = cs.client.auth_token
                    auth_details[username]['token'] = cs.client.auth_token
                    with open(auth_file, 'w+') as f:
                        json.dump(auth_details, f)

        with open(servers_file, 'wb+') as f:
            json.dump(servers, f)

        os.unlink(self.lock_file)
        self.logger.info('Completed looking for new servers')
        self.logger.info('New servers found: %d' % new_servers)

    def cleanup(self):
        os.unlink(self.lock_file)
