#!/usr/bin/python

DOCUMENTATION = """
---

module: comware_ftp
short_description: Configure device FTP function.
description:
    -Configure device FTP function.
version_added: 1.8
category: Feature (RW)
author: liudongxue
notes:
    - When using the FTP function of the device,you need to enable FTP first.
options:
    state:
        description:
            - The state of FTP
        required: false
        default: disable
        choices: ['enable', 'disable']
        aliases: []
    hostname:
        description:
            - IP Address or hostname of the Comware v7 device that has
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
    port:
        description:
            - The Comware port used to connect to the switch
        required: false
        default: 830
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
EXAMPLE = """

# Enabling FTP
- comware_ftp: state=enable username={{ username }} password={{ password }} hostname={{ inventory_hostname }}
"""

import socket
import re
try:
    HAS_PYCW7 = True
    from pycw7_ansible.comware import COM7
    from pycw7_ansible.features.errors import *
    from pycw7_ansible.errors import *
    from pycw7_ansible.features.ftp import Ftp
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
            name=dict(required=False),
            state=dict(choices=['enable', 'disable'],
                       default='disable'),
            hostname=dict(required=True),
            username=dict(required=True),
            password=dict(required=False, default=None),
            port=dict(type='int', default=830),
            look_for_keys=dict(default=False, type='bool')
        ),
        supports_check_mode=True
    )
    if not HAS_PYCW7:
        safe_fail(module, msg='There was a problem loading from the pycw7 '
                  + 'module.', error=str(ie))

    filtered_keys = ('hostname', 'username', 'password',
                     'port', 'CHECKMODE', 'name', 'look_for_keys')

    hostname = socket.gethostbyname(module.params['hostname'])
    username = module.params['username']
    password = module.params['password']
    port = module.params['port']
    device = COM7(host=hostname, username=username,
                    password=password, port=port)
    state = module.params['state']
    changed = False

    proposed = dict((k, v) for k, v in module.params.items()
                    if v is not None and k not in filtered_keys)

    try:
        look_for_keys = module.params['look_for_keys']
        device.open(look_for_keys=look_for_keys)
    except ConnectionError as e:
        safe_fail(module, device, msg=str(e),
                  descr='Error opening connection to device.')

    ftp=Ftp(device,state)
    ftp.config_ftp(stage = True)
    existing = True
    commands = None
    end_state = True

    if device.staged:
        commands = device.staged_to_string()
        if module.check_mode:
            safe_exit(module, device, changed=True,
                      commands=commands)
        else:
            try:
                device.execute_staged()
                #end_state = interface.get_config()
            except PYCW7Error as e:
                safe_fail(module, device, msg=str(e),
                          descr='Error on device execution.')
            changed = True

    results = {}
    results['proposed'] = proposed
    results['existing'] = existing
    results['state'] = state
    results['commands'] = commands
    results['changed'] = changed
    results['end_state'] = end_state

    safe_exit(module, device, **results)

from ansible.module_utils.basic import *
main()
