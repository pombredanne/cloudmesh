""" run with

nosetests -v --nocapture test_cm_shell.py

"""
from cloudmesh_base.util import HEADING
from cloudmesh_base.logger import LOGGER, LOGGING_ON, LOGGING_OFF

log = LOGGER(__file__)

import sys
import os
import cloudmesh

import unittest


class Test(unittest.TestCase):
    vm = []

    def test_01_init(self):
        HEADING()
        cloudmesh.shell("cloud list")
      
    def test_02_activate_cloud(self):
        HEADING()
        cloudmesh.shell("cloud on india")

    def test_03_select_default_cloud(self):
        HEADING()
        cloudmesh.shell("default cloud india")

    @classmethod
    def test_04_start_a_vm(cls):
        HEADING()
        import random
        vm_name = "nosetests_"+str(random.randint(1, 100))
        cloudmesh.shell("vm start --name={0} --cloud=india \
                        --image=futuregrid/ubuntu-14.04 \
                        --flavor=m1.small".format(vm_name))
        cls.vm.append(vm_name)

    def test_05_default_flavor(self):
        HEADING()
        cloudmesh.shell("cloud set flavor india --id=2")

    def test_06_default_image(self):
        HEADING()
        cloudmesh.shell("cloud set image india --name=futuregrid/ubuntu-14.04")

    def test_07_list_flavors(self):
        HEADING()
        cloudmesh.shell("list flavor india --refresh")

    def test_08_list_images(self):
        HEADING()
        cloudmesh.shell("list image india --refresh")

    @classmethod
    def test_09_quick_start(cls):
        HEADING()
        import random
        vm_name = "nosetests_"+str(random.randint(1, 100))
        cloudmesh.shell("vm start --name={0} --cloud=india".format(vm_name))
        cls.vm.append(vm_name)

    def test_10_refresh_vms(self):
        HEADING()
        cloudmesh.shell("list vm india --refresh")

    @classmethod
    def test_11_delete_vms(cls):
        HEADING()
        for vm_name in cls.vm:
            cloudmesh.shell("vm delete {0} --cloud=india --force".format(vm_name))
            cls.vm.remove(vm_name)

    def test_12_start_3_vms(self):
        HEADING()
        cloudmesh.shell("vm start --cloud=india --group=nosetests --count=3")

    def test_13_delete_3_vms(self):
        HEADING()
        cloudmesh.shell("vm delete --cloud=india --group=nosetests --force")

