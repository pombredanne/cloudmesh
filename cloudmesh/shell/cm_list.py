from cloudmesh.config.cm_config import cm_config
from cloudmesh.iaas.cm_cloud import CloudManage
from cloudmesh_common.logger import LOGGER
from tabulate import tabulate
from pprint import pprint

#list_command_table_format = "simple"
list_command_table_format = "grid"


log = LOGGER(__file__)

def shell_command_list(arguments):
    """
    Usage:
        list flavor [CLOUD|--all] [--refresh]
        list image [CLOUD|--all] [--refresh]
        list vm [CLOUD|--all] [--refresh]
        list project
        list cloud

    Arguments:

        CLOUD    the name of the cloud

    Options:

        -v         verbose mode
        --all      list information of all active clouds
        --refresh  refresh data before list

    Description:
        
        List clouds and projects information, if CLOUD argument is not given,
        default or selected cloud will be used, you may use command 'cloud select' 
        to select the cloud to work with.
    
        list flavor [CLOUD|--all] [--refresh]
            list the flavors
        list image [CLOUD|--all] [--refresh]
            list the images
        list vm [CLOUD|--all] [--refresh]
            list the vms
        list project
            list the projects
        list cloud
            list active clouds
        
    """
    call = ListInfo(arguments)
    call.call_procedure()
    
    
class ListInfo(object):
    cloudmanage = CloudManage()
    try:
        config = cm_config()
    except:
        log.error("There is a problem with the configuration yaml files")
    
    username = config['cloudmesh']['profile']['username']
    
    def __init__(self, arguments):
        self.arguments = arguments
        
        
    def _list_flavor(self):
        clouds = self.get_working_cloud_name()
        if clouds:
            itemkeys = [
                         ['id', 'id'],
                         ['name', 'name'],
                         ['vcpus', 'vcpus'],
                         ['ram', 'ram'],
                         ['disk', 'disk'],
                         ['refresh time', 'cm_refresh']
                       ]
            if self.arguments['--refresh']:
                self.cloudmanage.mongo.activate(cm_user_id=self.username, names=clouds)
                self.cloudmanage.mongo.refresh(cm_user_id=self.username, names=clouds, types=['flavors'])
            for cloud in clouds:
                self.cloudmanage.print_cloud_flavors(username=self.username, cloudname=cloud.encode("ascii"), itemkeys=itemkeys, refresh=False, output=False)
        
        else:
            return
        
        
    def _list_image(self):
        clouds = self.get_working_cloud_name()
        if clouds:
            itemkeys = {"openstack":
                        [
                            # [ "Metadata", "metadata"],
                            [ "name" , "name"],
                            [ "status" , "status"],
                            [ "id", "id"],
                            [ "type_id" , "metadata", "instance_type_id"],
                            [ "iname" , "metadata", "instance_type_name"],
                            [ "location" , "metadata", "image_location"],
                            [ "state" , "metadata", "image_state"],
                            [ "updated" , "updated"],
                            #[ "minDisk" , "minDisk"],
                            [ "memory_mb" , "metadata", 'instance_type_memory_mb'],
                            [ "fid" , "metadata", "instance_type_flavorid"],
                            [ "vcpus" , "metadata", "instance_type_vcpus"],
                            #[ "user_id" , "metadata", "user_id"],
                            #[ "owner_id" , "metadata", "owner_id"],
                            #[ "gb" , "metadata", "instance_type_root_gb"],
                            #[ "arch", ""]
                        ],
                      "ec2":
                        [
                            # [ "Metadata", "metadata"],
                            [ "state" , "extra", "state"],
                            [ "name" , "name"],
                            [ "id" , "id"],
                            [ "public" , "extra", "is_public"],
                            [ "ownerid" , "extra", "owner_id"],
                            [ "imagetype" , "extra", "image_type"]
                        ],
                      "azure":
                        [
                            [ "name", "label"],
                            [ "category", "category"],
                            [ "id", "id"],
                            [ "size", "logical_size_in_gb" ],
                            [ "os", "os" ]
                        ],
                      "aws":
                        [
                            [ "state", "extra", "state"],
                            [ "name" , "name"],
                            [ "id" , "id"],
                            [ "public" , "extra", "ispublic"],
                            [ "ownerid" , "extra", "ownerid"],
                            [ "imagetype" , "extra", "imagetype"]
                        ]
                     }
            if self.arguments['--refresh']:
                self.cloudmanage.mongo.activate(cm_user_id=self.username, names=clouds)
                self.cloudmanage.mongo.refresh(cm_user_id=self.username, names=clouds, types=['images'])
            for cloud in clouds:
                self.cloudmanage.print_cloud_images(username=self.username, cloudname=cloud.encode("ascii"), itemkeys=itemkeys, refresh=False, output=False)
        
        else:
            return
        
        
    def _list_server(self):
        clouds = self.get_working_cloud_name()
        if clouds:
            itemkeys = {"openstack":
                      [
                          ['name','name'],
                          ['status','status'],
                          ['addresses','addresses'],
                          ['id','id'],
                          ['flavor', 'flavor','id'],
                          ['image','image','id'],
                          ['user_id', 'cm_user_id'],
                          ['metadata','metadata'],
                          ['key_name','key_name'],
                          ['created','created'],
                      ],
                      "ec2":
                      [
                          ["name", "id"],
                          ["status", "extra", "status"],
                          ["addresses", "public_ips"],
                          ["flavor", "extra", "instance_type"],
                          ['id','id'],
                          ['image','extra', 'imageId'],
                          ["user_id", 'user_id'],
                          ["metadata", "metadata"],
                          ["key_name", "extra", "key_name"],
                          ["created", "extra", "launch_time"]
                      ],
                      "aws":
                      [
                          ["name", "name"],
                          ["status", "extra", "status"],
                          ["addresses", "public_ips"],
                          ["flavor", "extra", "instance_type"],
                          ['id','id'],
                          ['image','extra', 'image_id'],
                          ["user_id","user_id"],
                          ["metadata", "metadata"],
                          ["key_name", "extra", "key_name"],
                          ["created", "extra", "launch_time"]
                      ],
                      "azure":
                      [
                          ['name','name'],
                          ['status','status'],
                          ['addresses','vip'],
                          ['flavor', 'flavor','id'],
                          ['id','id'],
                          ['image','image','id'],
                          ['user_id', 'user_id'],
                          ['metadata','metadata'],
                          ['key_name','key_name'],
                          ['created','created'],
                      ]
                     }
            if self.arguments['--refresh']:
                self.cloudmanage.mongo.activate(cm_user_id=self.username, names=clouds)
                self.cloudmanage.mongo.refresh(cm_user_id=self.username, names=clouds, types=['servers'])
            for cloud in clouds:
                self.cloudmanage.print_cloud_servers(username=self.username, cloudname=cloud.encode("ascii"), itemkeys=itemkeys, refresh=False, output=False)
        
        else:
            return
        
        
    def _list_project(self):
        selected_project = None
        try:
            selected_project = self.cloudmanage.mongo.db_defaults.find_one({'cm_user_id': self.username + "OIO"})['project']
        except Exception, NoneType:
            log.error("clould not find selected project in the database")

        except Exception, e:
            log.error("clould not connect to the database")
            print e
            
        print "\n"
        print tabulate([[selected_project]], ["selected project"], tablefmt=list_command_table_format)


        #
        # active projects
        #

        
        projects = {}

        for state in ["active", "completed"]:

            projects[state] = None
            try:
                projects[state] = self.cloudmanage.mongo.db_user.find_one({'cm_user_id': self.username})['projects'][state]
            except:
                log.error("clould not find objects or connect to the database containing the projects")

            to_print = []
            if projects[state] == None:
                to_print = [[None]]
            else:
                to_print = [[str(p)] for p in projects[state]]
            print "\n"                
            print tabulate(to_print, ["{0} projects".format(state)], tablefmt=list_command_table_format)

        
    def _list_cloud(self):
        active_clouds = []
        other_clouds = []
        activeclouds = self.cloudmanage.mongo.active_clouds(self.username)
        clouds = self.cloudmanage.get_clouds(self.username)
        clouds = clouds.sort([('cm_cloud', 1)])
        for cloud in clouds:
            name = cloud['cm_cloud']
            if name in activeclouds:
                active_clouds.append([str(name)])
            else:
                other_clouds.append([str(name)])
        if active_clouds == []: active_clouds = [None]
        if other_clouds == []: other_clouds = [None]
        print tabulate(active_clouds, ["active clouds"], tablefmt=list_command_table_format)
        print "\n"
        print tabulate(other_clouds, ["other clouds"], tablefmt=list_command_table_format)
        print "\n"
            
    
    # --------------------------------------------------------------------------
    def get_working_cloud_name(self):
        '''
        get the name of a cloud to be work on, if CLOUD not given, will pick the
        slected cloud, is --all, will return a list of active clouds
        '''
        activeclouds = None
        try:
            activeclouds = self.cloudmanage.mongo.active_clouds(self.username)
        except:
            pass
        if self.arguments['--all']:
            if activeclouds == None:
                print "no active cloud, please activate a cloud by 'cloud on [CLOUD]'"
                return False
            return activeclouds
        else:
            if self.arguments['CLOUD']:
                name = self.arguments['CLOUD']
            else:
                name = self.cloudmanage.get_selected_cloud(self.username)
            if self.cloudmanage.get_clouds(self.username, getone=True, cloudname=name) == None:
                log.error("no cloud information of '{0}' in database".format(name))
                return False
            if name not in activeclouds:
                log.error("cloud '{0} is active, please activate a cloud by 'cloud on [CLOUD]'".format(name))
                return False
            return [name]
        
        
    def call_procedure(self):

        if self.arguments['flavor'] == True:
            call = 'flavor'
        elif self.arguments['vm'] == True:
            call = 'server'
        elif self.arguments['image'] == True:
            call = 'image'
        elif self.arguments['project'] == True:
            call = 'project'
        elif self.arguments['cloud'] == True:
            call = 'cloud'
        func = getattr(self, "_list_" + call)
        func()
        
        
        
        
        
        
        
