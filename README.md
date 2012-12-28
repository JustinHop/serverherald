# rax-nextgen-notify

A script intended to be run via cron for sending notification emails as new Rackspace NextGen cloud servers become ACTIVE.

The email should look very similar to the FirstGen notification emails, but with some additional informaiton.

---

## Download

### Where?

**Link**: [Coming Soon](http://rackspace.com/)

**From the command line**:

Coming Soon

**Directly from git:**

Coming Soon

---

## Usage

For your first run, enable the silent switch so that `rax-nextgen-notify.py` can learn about your existing servers:

    $ ./rax-nextgen-notify.py --silent

All future runs can drop the silent option so that notifications are sent for new servers.

    $ ./rax-nextgen-notify.py

## Installation

This script is written in Python. It requires Python 2.6 or Python 2.7 and multiple dependencies. It is recommended to install this inside of a Python virtual environment.

### Recommended Operating Systems

* Red Hat Enterprise Linux 6
* CentOS 6
* Ubuntu 12.04 LTS

### Dependencies

* [pyrax](https://github.com/rackspace/pyrax)
* [PyYAML](http://pyyaml.org/)
* Standard Modules (Should be included in the default Python installation)
  * json
  * sys
  * os
  * smtplib
  * getpass
  * argparse
  * email
  
### Red Hat / CentOS
 
1. Install the EPEL repository: `rpm -ivh http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm`
1. Install Python virtualenv: `yum install python-virtualenv`
1. Create a Python virtualnv: `cd; virtualenv rax-nextgen-notify`
1. Activate the virtualenv: `cd rax-nextgen-notify; . bin/activate`
1. Install the dependencies: `pip install PyYAML pyrax`
1. Copy the downloaded rax-nextgen-notify.py and cron.sh files to the virtualenv created in step 3
1. Make cron.sh executable: `chmod +x cron.sh`
1. Create a config file as documented below
1. For the first run the script with the -s flag: `python rax-nextgen-notify.py -s`
1. Create a cronjob to run on the frequency you determine, that executes the cron.sh script
 
### Ubuntu

1. Install Python virtualenv: `sudo apt-get install python-virtualenv`
2. Create a Python virtualenv: `cd; virtualenv rax-nextgen-notify`
1. Activate the virtualenv: `cd rax-nextgen-notify; . bin/activate`
1. Install the dependencies: `pip install PyYAML pyrax`
1. Copy the downloaded rax-nextgen-notify.py and cron.sh files to the virtualenv created in step 2
1. Make cron.sh executable: `chmod +x cron.sh`
1. Create a config file as documented below
1. For the first run the script with the -s flag: `python rax-nextgen-notify.py -s`
1. Create a cronjob to run on the frequency you determine, that executes the cron.sh script

### Configuration File

The configuration file must be named `config.yaml` and must be located in the same directory as `rax-nextgen-notify.py`

The configuration file is in YAML format. See the following links for more information about YAML format:

* [PyYAML](http://pyyaml.org/wiki/PyYAMLDocumentation#YAMLsyntax)
* [YAML Spec](http://yaml.org/spec/1.1/#id857168)

#### Example Configuration

    email:
      to:
        - you@yourcompany.com
        - list@yourcompany.com
      from: Cloud Tracker <noreply@yourcompany.com>
    accounts:
      myclouduser1:
        apiKey: db2132af5dc3125f9c688661fefab621
        endpoint: US
      myclouduser2:
        apiKey: cef58b947cd85a4fd772fe37c9408ffa
        endpoint: US
      myclouduser3:
        apiKey: 6d708e45a377d3f4421542217c282a22
        endpoint: LON

---


## FAQ

### How often should I configure the cron job for?

That is completely up to you. The more frequently the script runs, the sooner you will be notified when the cloud server is up and in ACTIVE status. It is not recommended to use anything less than 5 minutes.

The more often the cron job runs the more API calls you use. Use the lowest value that doesn't impact your API usage and that maximizes the amount of time that can go between polling.

#### Sample Cron Entry

    */5 * * * * /home/user/rax-nextgen-notify/cron.sh

### Do I have to use Python virtualenv?

No, there is no requirement to use Python virtualenv. Python virtualenv enables us to keep the global Python packages clean and to prevent conflicts between required versions of Python modules between different Python applications.

If you decide to go this route, there is a python-yaml in Ubuntu and a PyYAML package in Red Hat/CentOS.

Many of the other Python modules will still need to be installed via pip/easy_install as there are no packages provided by your Operating Systems software repository.

In addition you will need to modify cron.sh to no longer source bin/activate. Ohter modifications may be possible as well.

---

## Additional Notes

### Server Cache File

This script will create a cache file in the same directory as `rax-nextgen-notify.py` titled `servers.json`. This file will keep a record of all current NextGen cloud servers and is formatted as a JSON string.

---

## Developers

1. [Matt Martz](mailto:matt.martz@rackspace.com) - Primary Developer