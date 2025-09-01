#!/usr/bin/python

DOCUMENTATION = """
---

module: comware_facts
short_description: Gather facts of Comware 7 devices
description:
    - Gather fact data (characteristics) of Comware 7 devices
version_added: 1.8
category: Read-Only
return_data:
    - vendor
    - model
    - serial_number
    - uptime
    - hostname
    - os
    - localtime
    - config (name of running config)
    - interface_list
options:
    port:
        description:
            - NETCONF port number
        required: true
        default: 830
        choices: []
        aliases: []
    hostname:
        description:
            - IP Address or hostname of the Comware 7 device that has
              NETCONF enabled
        required: true
        default: null
        choices: []
        aliases: []
    username:
        description:
            - Username used to login to the switch
        required: true
        default: null
        choices: []
        aliases: []
    password:
        description:
            - Password used to login to the switch
        required: true
        default: null
        choices: []
        aliases: []
    look_for_keys:
        description:
            - Whether searching for discoverable private key files in ~/.ssh/
        required: false
        default: False
        choices: []
        aliases: []

"""
EXAMPLES = """

# get facts
- comware_facts: username={{ username }} password={{ password }} hostname={{ inventory_hostname }}

"""

import socket
try:
    HAS_PYCW7 = True
    from pycw7_ansible.features.facts import Facts
    from pycw7_ansible.comware import COM7
    from pycw7_ansible.features.errors import *
    from pycw7_ansible.errors import *
except ImportError as ie:
    HAS_PYCW7 = False


def safe_fail(module, device=None, **kwargs):
    if device:
        device.close()
    module.fail_json(**kwargs)


def safe_exit(module, device=None, **kwargs):
    if device:
        device.close()
    module.exit_json(**kwargs)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            port=dict(default=830, type='int'),
            hostname=dict(required=True),
            username=dict(required=True),
            password=dict(required=False, default=None),
            look_for_keys=dict(default=False, type='bool'),
        ),
        supports_check_mode=False
    )

    if not HAS_PYCW7:
        safe_fail(module, msg='There was a problem loading from the pycw7 '
                  + 'module.', error=str(ie))

    username = module.params['username']
    password = module.params['password']
    port = module.params['port']
    hostname = socket.gethostbyname(module.params['hostname'])

    device_args = dict(host=hostname, username=username,
                       password=password, port=port)

    device = COM7(**device_args)

    try:
        look_for_keys = module.params['look_for_keys']
        device.open(look_for_keys=look_for_keys)
    except ConnectionError as e:
        safe_fail(module, device, msg=str(e),
                  descr='error opening connection to device')

    try:
        facts = Facts(device)
    except PYCW7Error as e:
        safe_fail(module, device, msg=str(e),
                  descr='error collecting facts')

    device_facts = facts.facts

    safe_exit(module, device, ansible_facts=device_facts)

from ansible.module_utils.basic import *
main()
