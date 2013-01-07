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
import getpass
import logging

import keyring


class ServerHeraldLogger(object):
    def info(self, string):
        pass

    def warning(self, string):
        pass

    def error(self, string):
        pass

    def logger(self, enabled=True):
        if enabled:
            logger = logging.getLogger('serverherald')
            logger.setLevel(logging.INFO)
            log_file = os.path.expanduser('~/.serverherald/serverherald.log')
            fh = logging.FileHandler(log_file)
            fmt = '%(asctime)s %(name)s[%(process)d] [%(levelname)s] ' \
                  '%(message)s'
            datefmt = '%b %d %H:%M:%S'
            formatter = logging.Formatter(fmt, datefmt)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            return logger
        else:
            return self


def config_has(config, section, key=None):
    if key:
        return key in config[section]
    return section in config


def config_get(config, section, key=None, default=None):
    """Return value that matches key in config settings.
    Reference keyring if needed.
    """
    config_section = config.get(section)
    if not key:
        return config_section
    if config_section.get(key, default) == 'USE_KEYRING':
        keyring_path = section + '/' + key
        keyring_value = keyring.get_password('serverherald', keyring_path)
        if keyring_value is None:
            print 'The keyring storage mechanism has been selected for' \
                  '%s but the keyring is empty' % keyring_path

            while 1:
                user_value = getpass.getpass("%s: " % key)
                if user_value != '':
                    keyring.set_password('serverherald', keyring_path,
                                         user_value)
                    break
            return user_value
        else:
            return keyring_value
    else:
        return config_section.get(key, default)
