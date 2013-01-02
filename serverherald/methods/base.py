import os
import sys
import json
import getpass
import pyrax
from jinja2 import Environment, PackageLoader


class ServerHerald:

    """Class for querying current cloud servers and sending
    notifications for new servers
    """

    def __init__(self, config, silent=False):
        """Initialize the class by setting the path to the config file,
        checking file and directory locations and parsing the config file

        silent (boolean) specifies whether or not to send email notifications
        (optional)

        """

        self.silent = silent
        self.config = config

        self.check_files()
        self.validate_config()
        self.template_env = Environment(loader=PackageLoader('serverherald',
                                        'templates'))

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
                os.path.makedirs(local_dir, 0700)
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

        self.lock_file = '%s/lock' % local_dir

        if os.path.isfile(self.lock_file):
          with open(self.lock_file) as f:
            lock_pid = f.read().strip()
          if os.path.isdir('/proc'):
            if os.path.isdir('/proc/%s' % lock_pid):
              exe = os.readlink('/proc/%s/exe' % lock_pid)
              if 'python' in exe:
                print 'serverherald[%s] is currently running' % lock_pid
                sys.exit(1)
              else:
                print 'serverherald pid file found, but is not running'
                os.unlink(self.lock_file)
          else:
            print 'serverherald lockfile found'
            print 'serverherald cannot check the pid on this OS'
            sys.exit(1)

        with open(self.lock_file, 'w+') as f:
            f.write('%s' % os.getpid())

    def validate_config(self):
        """Load the config.yaml file and validate it's contents within
        reason"""

        if not self.config:
            print 'The config file is empty and must be populated'
            sys.exit(1)

        accounts = self.config.get('accounts')
        if not accounts or not accounts.keys():
            print 'There are no accounts configured in the config file'
            sys.exit(1)

        for account, settings in accounts.iteritems():
            if 'apikey' not in settings:
                print 'Account %s does not have an API key' % account
                sys.exit(1)

    def check_servers(self):
        """Check all regions for an Auth endpoint querying for all servers,
        sending notifications for new servers in ACTIVE status
        """
        servers_file = os.path.expanduser('~/.serverherald/servers.json')
        if not os.path.isfile(servers_file):
            last_servers = {}
        else:
            with open(servers_file) as f:
                last_servers = json.load(f)
        servers = {}
        for username, settings in self.config['accounts'].iteritems():
            endpoint = settings.get('endpoint', 'US')
            if endpoint == 'LON':
                pyrax.default_region = 'LON'
            pyrax.set_credentials(username, settings.get('apikey'))
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
                    public_ips = server.addresses.get('public')
                    if public_ips:
                        ips = ', '.join([ver['addr'] for ver in public_ips])
                    else:
                        ips = 'None'
                    try:
                        image = filter(lambda x: x.id == server.image['id'],
                                       images)[0].name
                    except IndexError:
                        image = cs.images.get(server.image['id']).name
                    flavor = filter(lambda x: int(x.id) == int(
                                    server.flavor['id']), flavors)[0].name
                    if username not in servers:
                        servers[username] = []
                    if username not in last_servers:
                        last_servers[username] = []
                    servers[username].append(id)
                    if status == 'ACTIVE' and id not in last_servers[username]:
                        context = {'id': id, 'status': status,
                                   'server': server, 'server_image': image,
                                   'flavor': flavor, 'server_ips': ips,
                                   'server_ips_list': public_ips,
                                   'username': username, 'region': region}
                        self.notify(context)

        with open(servers_file, 'wb+') as f:
            json.dump(servers, f)

        os.unlink(self.lock_file)
