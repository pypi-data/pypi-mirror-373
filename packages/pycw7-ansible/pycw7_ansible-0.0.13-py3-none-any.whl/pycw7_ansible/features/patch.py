"""Operation for patch in COM7 devices.
"""
from lxml import etree
from ncclient.xml_ import qualify
from pycw7_ansible.utils.xml.namespaces import NCDATA, NCDATA_C, NCACTION
from pycw7_ansible.utils.xml.lib import *
import time

class Patch(object):
    """This class is used to get data and configure a specific File.

    Args:
        device (COM7): connected instance of a ``pycw7.comware.COM7``
            object.

    Attributes:
        device (COM7): connected instance of a ``pycw7.comware.COM7``
            object.

    """
    def __init__(self, device, patchname):
        self.device = device
        if patchname:
            self.patchname = patchname

    def get_file_lists(self):
        commands = 'dir | inc bin'
        Filename = '{0}'.format(self.patchname)
        res = self.device.cli_display(commands)
        if Filename in res:
            return True
        else:
            return False

    def Check_result(self):

        commands = 'dis install committed'
        Filename = 'flash:/{0}'.format(self.patchname)
        res = self.device.cli_display(commands)

        if Filename in res:
            return True
        else:
            return False

    def Activate(self, stage=False, **check_file):
        check_file['patchname'] = self.patchname
        Patchname = check_file.get('patchname')
        commands = []
        cmd_1 = 'install activate patch flash:/{0} slot 1'.format(Patchname)
        cmd_2 = 'install commit'
        commands.append(cmd_1)
        commands.insert(-1, 'quit')
        commands.append(cmd_2)
        c2 = True
        if commands:
            if stage:
                c2 = self.device.stage_config(commands, 'cli_config')
            else:
                c2 = self.device.cli_config(commands)
        # time.sleep(10)
        if stage:

            return c2
        else:
            return [c2]

    def build(self, stage=False, **check_file):
        return self.Activate(stage=stage, **check_file)


