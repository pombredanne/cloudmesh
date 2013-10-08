# -*- coding: utf-8 -*-
"""
    cloudmesh.user.cm_user
    ~~~~~~~~~~~~~~~~~~~~~~

    cm_user provides user information from the ldap and the cloud like openstack
    through mongodb. fab mongo.cloud command initialize mongo database and pour
    the information into the mongodb. Once the mongodb for cloudmesh has the
    user information, cm_user retrieves the user data from the mongodb
    instead of directly accessing the ldap and OpenStack Keystone. cm_user_id is
    the unique identification in ldap and cloud.

"""
from cloudmesh.config.cm_config import cm_config_server, get_mongo_db, cm_config
from cloudmesh.util.encryptdata import encrypt, decrypt
from cloudmesh.util.logger import LOGGER
from cloudmesh.util.util import deprecated
from cloudmesh.user.cm_userLDAP import cm_userLDAP

import traceback
from pprint import pprint
# ----------------------------------------------------------------------
# SETTING UP A LOGGER
# ----------------------------------------------------------------------

log = LOGGER(__file__)

class cm_user(object):
    """cm_user provides user information including the ldap's and the clouds'.
    The ldap has a user profile such as a first name, last name and active
    project ids. In OpenStack Keystone, it has cloud-related information such as
    a tenant id, user id, cloud version, cloud type and location.
    """

    config_server = None


    def __init__(self, from_yaml=False):
        self.from_yaml = from_yaml
        self.config_server = cm_config_server()
        self.password_key = self.config_server.get("cloudmesh.server.mongo.collections.password.key")
        self.with_ldap = cm_config_server().get("cloudmesh.server.ldap.with_ldap")
        self.connect_db()



    def authenticate(self, userId, password):
        if not self.with_ldap:
            return True
        try:
            idp = cm_userLDAP ()
            idp.connect("fg-ldap", "ldap")
            return idp.authenticate(userId, password)
        except Exception, e:
            log.error("{0}".format(e))
            return False

    def generate_yaml(id, basename):
        '''
        Generates the content for a yaml file based on the passwed parameters.
        
        :param id: The username for which we want to create the yaml file
        :type id: String
        :param basename: The base name of the yaml file in the etc directory.
                         Allowed values are 'me' and 'cloudmesh'
        :type basename: String
        '''

        """id = username"""
        """basename = me, cloudmesh"""

        log.info("generate {1} yaml {0}".format(id, basename))
        result = self.info(id)

        # banner("RESULT")
        # pprint (result)


        etc_filename = path_expand("~/.futuregrid/etc/{0}.yaml".format(basename))

        # print etc_filename

        t = cm_template(etc_filename)
        out = t.replace(kind='dict', values=result)
        # banner("{0} DATA".format(basename))

        return out


    def connect_db(self):
        """ Connect to the mongo db."""

        if not self.from_yaml:

            ldap_collection = 'user'
            cloud_collection = 'cloudmesh'
            defaults_collection = 'defaults'
            passwd_collection = 'password'

            self.db_clouds = get_mongo_db(cloud_collection)
            self.db_users = get_mongo_db(ldap_collection)
            self.db_defaults = get_mongo_db(defaults_collection)
            self.userdb_passwd = get_mongo_db(passwd_collection)




    def info(self, portal_id, cloud_names=[]):
        """Return th<: the list of cloud names to search, e.g.
        sierra_openstack_grizzly
        :type cloud_names: list
        :returns: dict

        """

        if self.from_yaml:
            return get_ldap_user_from_yaml()

        else:

            ldap_info = self.db_users.find({"cm_user_id": portal_id})
            cloud_info = self.db_clouds.find({"name": portal_id, "cm_kind": "users"})
            userinfo = {}
            # username is unique in ldap
            if ldap_info.count() > 0:
                ldap_user = ldap_info[0]
                del ldap_user['_id']
                userinfo["profile"] = ldap_user
                #
                # repositionning kesya nd projects
                #

                try:
                    userinfo["keys"] = {}
                    userinfo["keys"]["keylist"] = ldap_user['keys']
                except:
                    userinfo["keys"]["keylist"] = {}

                try:
                    userinfo["projects"] = ldap_user['projects']
                except:
                    userinfo["projects"] = {'active': [], 'completed': []}

                del userinfo['profile']['keys']
                del userinfo['profile']['projects']

                userinfo['portalname'] = portal_id
                userinfo['cm_user_id'] = portal_id

            userinfo['clouds'] = {}
            for arec in cloud_info:
                del arec['_id']
                if len(cloud_names) > 0:
                    if arec['cm_cloud'] in cloud_names:
                        userinfo['clouds'][arec['cm_cloud']] = arec
                else:
                    userinfo['clouds'][arec['cm_cloud']] = arec
            userinfo['defaults'] = self.get_defaults(portal_id)
            #
            # update project names
            #


            projects = userinfo["projects"]
            projects = self.update_users_project_names(projects)


            return userinfo

    cloud_names = cm_config().cloudnames()
    default_security_group = cm_config().get("cloudmesh.security.default")
    default_cloud = 'sierra_openstack_grizzly'

    def init_defaults(self, username):

        user = self.info(username)

        defaults = self.get_defaults(username)
        defaults['cm_user_id'] = username
        if 'prefix' not in defaults:
            defaults['prefix'] = user['cm_user_id']
        if 'index' not in defaults:
            defaults['index'] = 1

        if 'cloud' not in defaults:
            if self.default_cloud in self.cloud_names:
                defaults['cloud'] = self.default_cloud
            elif len(self.cloud_names) > 0:
                defaults['cloud'] = self.cloud_names[0]

        if 'key' not in defaults:
            keylist = user['keys']['keylist']
            if len(keylist) > 0:
                defaults['key'] = keylist.keys()[0]

        if 'project' not in defaults:
            projectlist = user['projects']['active']
            if len(projectlist) > 0:
                defaults['project'] = projectlist[0]

        if 'activeclouds' not in defaults:
            if 'cloud' in defaults:
                defaults['activeclouds'] = [defaults['cloud']]


        if 'securitygroup' not in defaults:
            defaults['securitygroup'] = self.default_security_group


        self.update_defaults(username, defaults)

    def update_users_project_names(self, projects):

        if "active" not in projects.keys():
            projects["active"] = []

        if "completed" not in projects.keys():
            projects["active"] = []

        return projects

    def list_users(self, cloud_names=[]):
        """Return all user information with a given cloud.

        :param cloud_names: the cloud name
        :type cloud_names: list
        
        """
        if self.from_yaml:
            log.critical("NOT IMPLEMENTED")
        else:

            ldap_info = self.db_users.find()
            usersinfo = {}
            for ldap_user in ldap_info:
                # e.g. ldap_user = {u'cm_user_id': u'abc', u'lastname': u'abc'
                # , u'_id': ObjectId('abc'), u'projects':
                # {u'active': []}, u'firstname': u'bbc'}
                portal_id = ldap_user['cm_user_id']
                usersinfo[portal_id] = {}

                userinfo = usersinfo[portal_id]

                userinfo['portalname'] = portal_id
                userinfo['profile'] = ldap_user
                #
                # repositioning
                #
                userinfo["keys"] = {'keylist': ldap_user['keys']}

                userinfo["projects"] = ldap_user['projects']
                del userinfo['profile']['keys']
                del userinfo['profile']['projects']

                #
                # correct projects
                #
                projects = userinfo["projects"]
                projects = self.update_users_project_names(projects)

            cloud_info = self.db_clouds.find({"cm_kind": "users"})
            for cloud_user in cloud_info:
                portal_id = cloud_user['name']
                try:
                    usersinfo[portal_id]
                except KeyError:
                    print portal_id + " doesn't exist in the ldap, skip to search"
                    continue

                try:
                    usersinfo[portal_id]['clouds']
                except KeyError:
                    usersinfo[portal_id]['clouds'] = {}

                if cloud_names:
                    if cloud_user['cm_cloud'] in cloud_names:
                        usersinfo[portal_id]['clouds'][cloud_user['cm_cloud']] = \
                        cloud_user
                else:
                    usersinfo[portal_id]['clouds'][cloud_user['cm_cloud']] = \
                    cloud_user

            return usersinfo

    def __getitem__(self, key):
        return self.info(key)

    @deprecated
    def get_name(self, portal_id):
        """Return a user name in a tuple. (firstname, lastname)
        
        :param portal_id: the unique portal id
        :type portal_id: str
        :returns: tuple

        """
        (firstname, lastname) = (None, None)
        ldap_data = self.db_users.find({"cm_user_id": portal_id})
        if ldap_data.count() > 0:
            ldap_info = ldap_data[0]
            (first_name, last_name) = (ldap_info['firstname'], ldap_info['lastname'])

        return (first_name, last_name)

    def update_defaults(self, username, d):
        """ Sets the defaults for a user """
        stored_d = self.get_defaults(username)
        for attribute in d:
            stored_d[attribute] = d[attribute]
        self.set_defaults(username, stored_d)

    def set_defaults(self, username, d):
        """ Sets the defaults for a user """
        if type(d) is dict:
            self.db_defaults.update({'cm_user_id': username}, d, upsert=True)

        else:
            raise TypeError, 'defaults value must be a dict'

    def set_default_attribute(self, username, attribute, value):
        """will set a variable in mongo
            ["defaults"][attribute]
        """
        d = self.get_defaults(username)
        d[attribute] = value
        self.set_defaults(username, d)

    def get_defaults(self, username):
        """returns the defaults for the user"""
        user = self.db_defaults.find_one({'cm_user_id': username})

        if user is None:
            user = {}
        return user

    def set_password(self, username, password, cloud):
        """Store a user password for the cloud

        :param username: OS_USERNAME or cm_user_id
        :type username: str
        :param password: OS_PASSWORD
        :type password: str
        :param cloud: the cloud name e.g. sierra_openstack_grizzly
        :type cloud: str

        """
        safe_password = encrypt(password, self.password_key)
        self.userdb_passwd.update({"username": username, "cloud": cloud }, \
                                  {"username":username, "password":safe_password, \
                                   "cloud": cloud}, upsert=True)

    def get_password(self, username, cloud):
        """Return a user password for the cloud

        :param username: OS_USERNAME
        :type username: str
        :param cloud: the cloud name e.g. sierra_openstack_grizzly
        :type cloud:str

        """
        try:
            safe_password = self.userdb_passwd.find({"username": username, "cloud":cloud})[0]["password"]
            return decrypt(safe_password, self.password_key)
        except:
            return None

    def get_passwords(self, username):
        """Return all user passwords in the form of a dict, keyed by cloud name"""
        passwds = self.userdb_passwd.find({ "username": username })
        return dict(map(lambda d: (d["cloud"], decrypt(d["password"], self.password_key)), passwds))
