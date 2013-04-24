""" run with

nosetests -v --nocapture

or

nosetests -v

"""
#import sys
#sys.path.insert(0, '..')

from cm_config import cm_config

import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

header = False

def HEADING(txt):
    if header:
        print
        print "#", 70 * '#'
        print "#", txt
        print "#", 70 * '#'

class Test_cloudmesh:

    def setup(self):
        self.config = cm_config("credentials-example.yaml")

    def tearDown(self):
        pass

    def test01_print(self):
        print self.config

    def test02_active(self):
        HEADING("LIST ACTIVE PROJECTS")
        result = self.config.projects('active')
        assert result == ['fg-82', 'fg-101']
        
    def test03_completed(self):
        HEADING("LIST COMPLETED PROJECTS")
        result = self.config.projects('completed')		
        assert result == ['fg-81', 'fg-102']

    def test04_active(self):
	HEADING("LIST ACTIVE PROJECTS")
        result = self.config.projects('default')
        assert result == 'fg-82'

    def test05_india(self):
	HEADING("LIST India")
        result = self.config.get('india-openstack')
        assert result["OS_VERSION"] == "essex"

    def test06_keys_india_openstack(self):
	HEADING("KEY india-openstack")
        keys = self.config.keys()
        assert 'india-openstack' in keys

    def test07_keys_india_eucalyptus(self):
	HEADING("KEY india-eucalyptus")
	keys = self.config.keys()
        assert 'india-eucalyptus' in keys

    def test08_keys_grizzly_openstack(self):
	HEADING("KEY grizzly-openstack")
	keys = self.config.keys()
        assert 'grizzly-openstack' in keys

    def test09_keys_india_eucalyptus(self):
	HEADING("KEY azure")
	keys = self.config.keys()
        assert 'azure' in keys

    def test10_grizzly(self):
	HEADING("LIST GRIZZLY")
        result = self.config.get('grizzly-openstack')
	assert result["OS_VERSION"] == 'grizzly'

    def test11_grizzly(self):
	HEADING("LIST GRIZZLY EXPANDED")
        result = self.config.get('grizzly-openstack', expand=True)
	assert result["OS_VERSION"] == 'grizzly'

    def test12_clouds(self):
        HEADING("CLOUD")
        clouds = self.config.clouds()
        assert isinstance(clouds, dict)
        assert 'india-openstack' in clouds

    def test13_cloud(self):
        HEADING("CLOUD")
        india_cloud = self.config.cloud('india-openstack')
        assert isinstance(india_cloud, dict)
        assert 'cm_host' in india_cloud
        assert india_cloud['cm_host'] == 'india.futuregrid.org'

    def test14_cloud_default(self):
        HEADING("CLOUD")
        assert self.config.cloud_default('india-openstack', 'flavor') == 'm1.small'
        assert self.config.cloud_default('india-openstack', 'not defined') is None

    def test15_project_default(self):
        HEADING("PROJECT")
        project = self.config.projects('default')
        assert project == 'fg-82'
