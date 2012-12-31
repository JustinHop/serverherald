# serverherald

serverherald announces when a new Rackspace OpenStack Cloud Server becomes
ACTIVE by polling the API. It supports multiple notification methods, with
email being the most popular.

## Usage

For your first run, enable the silent switch so that serverherald can learn
about your existing servers:

    $ serverherald --silent

All future runs can drop the silent option so that notifications are sent for
new servers.

    $ serverherald

## Notification Methods

serverherald has a pluggable notification system that currently supports the
following methods:

* Email (SMTP, [Mailgun](http://www.mailgun.com/), or [Sendgrid](http://sendgrid.com))
* SMS ([Twilio](http://www.twilio.com/) or [Nexmo](http://nexmo.com/))
* iOS push notifications via [Prowl](http://www.prowlapp.com/)
* [PagerDuty](http://www.pagerduty.com/) event trigger
* Custom HTTP(S) webhook

The `method` directive in the configuration file determines how serverherald
sends notifications.

## Installation

serverherald is written in Python. It requires Python 2.6 or Python 2.7 and
multiple dependencies. It is recommended to install this inside of a Python
virtual environment.

### Red Hat / CentOS

Install python-virtualenv:

    # rpm -ivh http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
    # yum install python-virtualenv
    
### Ubuntu / Debian

Install python-virtualenv:

    $ sudo apt-get install python-virtualenv

### serverherald Installation

    $ git clone /change/this/later.git
    $ virtualenv ~/venv
    $ source ~/venv/bin/activate
    $ python setup.py install


## Configuration File

serverherald requires a configuration file in
[YAML format](http://yaml.org/spec/1.1/#id857168). You can specify the file
location at runtime with the `--config` option. Otherwise serverherald will
search these locations and select the first file that exists:
 * serverherald.yaml (in the current directory)
 * ~/serverherald.yaml
 * /etc/serverherald.yaml
 * /etc/serverherald/serverherald.yaml

### Example Configurations

SMTP notifications via a local mail server:

    method: smtp
    email:
      to:
        - you@yourcompany.com
        - list@yourcompany.com
      from: Server Herald <noreply@yourcompany.com>
    accounts:
      myclouduser1:
        apikey: db2132af5dc3125f9c688661fefab621
        endpoint: US
      myclouduser2:
        apikey: cef58b947cd85a4fd772fe37c9408ffa
        endpoint: US
      myclouduser3:
        apikey: 6d708e45a377d3f4421542217c282a22
        endpoint: LON

SMTP notifications via Mailgun:

    method: mailgun
    mailgun:
      domain: mydomain.mailgun.com
      apikey: 6d708e45a377d3f4421542217c282a22
    email:
      to:
        - you@yourcompany.com
    from: Server Herald <noreply@yourcompany.com>
    accounts:
      myclouduser1:
        apikey: db2132af5dc3125f9c688661fefab621

SMS notifications via Twilio:

    method: twilio
    twilio:
      accountsid: 6d708e45a377d3f4421542217c282a22
      token: cef58b947cd85a4fd772fe37c9408ffa
      from: "+15551234567"
      to: "+15557654321"
    accounts:
      myclouduser1:
      apikey: db2132af5dc3125f9c688661fefab621

SMS notifications via Nexmo:

    method: nexmo
    nexmo:
      apikey: 12345678
      apisecret: 87654321
      from: 15551234567
      to: 155577654321
      accounts:
        myclouduser1:
        apikey: db2132af5dc3125f9c688661fefab621

iOS push notifications via Prowl:

    method: prowl
    prowl:
      apikey: 6d708e45a377d3f4421542217c282a55
    accounts:
      myclouduser1:
        apikey: db2132af5dc3125f9c688661fefab621

PagerDuty event trigger:

    method: pagerduty
    pagerduty:
      apikey: 6d708e45a377d3f4421542217c282a55
    accounts:
      myclouduser1:
        apikey: db2132af5dc3125f9c688661fefab621

Custom HTTP or HTTPS webhook notifications:

    method: webhook
    webhook:
      url: http://example.com/notify-me
    accounts:
      myclouduser1:
        apikey: db2132af5dc3125f9c688661fefab621


## Deployment

serverherald should be used to poll the Rackspace Cloud Servers API on
a regular interval so that it can detect changes and then announce them.

A 5 minute cron job is recommended:

    */5 * * * * /path/to/serverherald

## FAQ
    
### Do I have to use Python virtualenv?

No, there is no requirement to use Python virtualenv. Python virtualenv
enables us to keep the global Python packages clean and to prevent conflicts
between required versions of Python modules between different Python
applications.

If you decide to go this route, there is a python-yaml in Ubuntu and a PyYAML
package in Red Hat/CentOS.

Many of the other Python modules will still need to be installed via
pip/easy_install as there are no packages provided by your distribution's
software repository.

## Additional Notes

### Server Cache File

This script will create a `~/.serverherald-servers.json` cache file to record
the results from the previous execution.

## Developers

1. [Matt Martz](mailto:matt.martz@rackspace.com) - Primary Developer
1. [Caleb Groom](mailto:cgroom@rackspace.com)