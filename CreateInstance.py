#!/usr/bin/env python

# CreateInstance.py
#
# This class was intended to demonstrate an exercise using the Python AWS SDK 
# (boto), however it will probably be extended to do much more over time,
# especially as I continue to test additional infrastructure.
#
# This class (CreateInstance) has some wrapper functions around the 'boto' module 
# to make things seem more 'pythonic'.  However, the functionality is only
# wrapped for certain actions, all of which are used for the main purpose of
# this class, which is to demo the provisioning and configuration of a single
# EC2 instance in AWS.  The configuration uses cloud-init with dynamic supplied
# user data to use APT to update, install nginx, configure and symlink the sites
# available virtualhost file into /etc/nginx/sites-enabled/.  It then builds a
# static html page at the location nginx config is expecting, and outputs a 
# simple <h1> message.
#
# This is object oriented and as such, may be expanded, reduced, built around,
# inherited from, imported into another project, using basic principles of OOP.
# Most importantly, the functions can be reused within the same project to
# follow DRY coding principles.
#
#
# Besides using 
# I addded some custom code for basic error checking on the arguments you pass
# into the class.  I am using cloud-init to configure nginx and the webserver
# configuration, however further down in the CreateInstance::run() function, you
# could extend it to use Fabric / Paramiko to SSH into the instance.
#
# Requirements:
#    - BASH in Linux or OS X (If unsure, run 'echo $SHELL' from command line. It
#      should return '/bin/bash'.
#    I would recommend using a virtualenv & virtualenvwrapper if you don't want 
#    boto installed globally. (virtualenvwrapper is optional but gives you a
#    great set of helper functions and shortcuts)
#
#    (sudo pip install virtualenv virtualenvwrapper -U)
#    
#    Create virtualenv with virtualenvwrapper helper BASH function, then install
#    boto within virtualenv.
#
#    Requires boto >=2.38
#
# Install instructions from BASH:
#    Assuming virtualenv/virtualenvwrapper (otherwise you must install boto with
#    pip as sudo)..
#
#    mkvirtualenv auto-deploy #auto-deploy is the name of your virtualenv
#    (pip install boto -U)
#    
#    Add the following to your ~/.boto file (create it if it doesn't exist) to
#    match your access key environment.
#    
#
# Author: Brian Taylor
# Feel free to contact me on github.  This file is contained in the github repo:
# https://github.com/briantyr/auto-deploy

import os
import sys
from time import sleep

import boto.ec2


class CreateInstance(object):
    """
    CreateInstance
    
    Class to instantiate, provision, and configure a single EC2 instance using
    Cloud Formation templates and the official Python SDK.
    Requires:
    'boto' module.
    
    Designed to create an EC2 instance in AWS and take advantage of cloud-init
    by supplying user-data.
    
    """
    
    # These variables are passed in when this class is instantiated.  Changing
    # them here will have no effect, they are only here for reference.
    region = None
    instance_type = None
    key_pair = None
    ec2_tag_Name = None
    ami = None
    security_group = None
    
    def __init__(self, *args, **kwargs):
        """
        __init__(self, *args, **kwargs):
        
        Accepts a bunch of named parameters and automatically lowercases them
        when doing comparisons, so the class accepts case insensitive args.
        
        This constructor populates the variables above.
        
        """
        self.conn = None
        
        for key in kwargs:
            if key.lower() == 'name':
                self.ec2_tag_Name = kwargs.get(key)
            elif key.lower() == 'region':
                self.region = kwargs.get(key)
            elif key.lower() == 'ami':
                self.ami = kwargs.get(key)
            elif key.lower() == 'type':
                self.instance_type = kwargs.get(key)
            elif key.lower() == 'security_group':
                self.security_group = kwargs.get(key)
            elif key.lower() == 'key_pair':
                self.key_pair = kwargs.get(key)
                
                
    def _validate_input(self):
        """
        Checks that the variables passed into the class are real and validates
        what it can.
        """
        # Check for a valid EC2 region, else raise an exception.
        if not boto.ec2.get_region(self.region):
            raise NotImplementedError("ERROR: The region specified is invalid: '%s'" % 
                             self.region)
        
        # Connect to region using credentials in ~/.boto
        # Boto will raise an exception if credentials are missing.
        self.conn = boto.ec2.connect_to_region(self.region)
        
        
        # Check if valid key_pair name
        if not self.conn.get_key_pair(self.key_pair):
            raise NotImplementedError("ERROR: The key_pair specified does not "
                                      "exist in this environment: %s" % self.key_pair)
        
        # This will either create a brand new group, or use an existing one you
        # specified in the constructor.  If creating new, keep in mind port 80
        # and 22 are open by default.
        self.sg = self.create_security_group(self.security_group)
        
    def run(self):
        """
        from createinstance.createinstance import CreateInstance
        CreateInstance().run() 
        
        Main Program Logic to connect return values.
        """
        self._validate_input()
        
        # Returns class boto.ec2.instance.Reservation object
        # http://boto.cloudhackers.com/en/latest/ref/ec2.html#boto.ec2.instance.Reservation    
        self.reservation_id = self.conn.run_instances(image_id=self.ami, 
                                                      key_name=self.key_pair, 
                                                      security_groups=[self.security_group],
                                                      instance_type=self.instance_type,
                                                      user_data=self._inject_user_data()
                                                      )
        
        launched_instance = self.reservation_id.instances[0]
        
        print "Provisioning '%s' EC2 Instance ID: '%s' in '%s', "\
              "named '%s'...\n" % (str(launched_instance.instance_type), 
                                  str(launched_instance.id),
                                  str(launched_instance.region.name), 
                                  str(self.ec2_tag_Name))
        
        self.wait_for_state_running(launched_instance)
        
        # Get all instances function call
        # Pass in string or list of instance_id that we just launched to get the
        # specific instance.
        instances = self.get_all_instances(launched_instance.id)
        if not instances:
            print "WARNING: self.get_all_instances returned an empty list of"\
                  " Instances."
        for ec2 in instances:
            if ec2.id == launched_instance.id:
                self.tag_instance(ec2, "Name", self.ec2_tag_Name)
                print "Successfully provisioned '{0}' and started new instance "\
                      "'{1}' with a Public DNS of '{2}'.\n\n".format(ec2.tags['Name'],
                                                                 ec2.id, 
                                                                 ec2.public_dns_name)
                print "Try navigating to http://{0} to see if the server came "\
                      "up and nginx properly displays 'Automation for the People!'\n\n "\
                      "Keep in mind occasionally Ubuntu updates take a while and "\
                      "same with nginx installation.. It should be available in "\
                      "under 2 minutes.  If not, SSH in and troubleshoot.\n"\
                      .format(ec2.public_dns_name)
                
            
    def tag_instance(self, instance_obj, key, value):
        """
        Added code to properly tag instances upon launching.
        :arg1 boto.ec2.Instance object
        :arg2 Key (e.g Name)
        :arg3 value (e.g Web-01-dev)
        
        Times out after 60 seconds if the instance has not changed states.
        """
        if isinstance(instance_obj, boto.ec2.instance.Instance):
            print "Attempting to tag Instance: {0} with Key: {1}, Value: {2}".format\
                  (instance_obj.id, key, value)
            if instance_obj.state is not u'running':
                if not self.wait_for_state_running(instance_obj):
                    raise Exception("Timeout waiting for Instance running: {0}".format(\
                        instance_obj.id))
           
            instance_obj.add_tag(key, value)
        else:
            raise NotImplementedError("instance_obj is not of type "\
                                      "boto.ec2.instance.Instance")
                    
    def get_all_instances(self, instance_ids=None):
        """
        CreateInstance.get_all_instances(instance_ids)
        Returns a list of type <class 'boto.ec2.instance.Instance'>, so each
        element in the list is a boto 'Instance' object representing a unique
        EC2 instance. (Returns started and stopped instances).
        
        If self.conn has not been assigned by boto, return empty list.
        
        Examples:
        - Retrieve only instances matching an EC2 instance_id of 'i-3255158'.
          (Passing in string)
          CreateInstance.get_all_instances(instance_ids='i-3255158')
          (Passing in list)
          CreateInstance.get_all_instances(instance_ids=['i-3255158'])
        """
        # If self.conn is None, return empty list
        if not self.conn:
            print "The self.conn variable is set to None! Can't get instances."
            return []
        
        # Check if passed in argument is a string, and if so, make into a list.
        if instance_ids and not isinstance(instance_ids, list):
            instance_ids = list().append(instance_ids)
            
        return self.conn.get_only_instances(instance_ids=instance_ids)
    
    def wait_for_state_running(self, instance_obj, timeout=180):
        """Waits for an Instance object to be started.  Timeout is 3 minutes, but
        can be adjusted with 'timeout' argument.
        
        :arg1: boto.ec2.instance.Instance object
        :arg2: timeout in seconds (optional: default is 180 seconds)
        :rval: Returns True if object started"""
        
        if not isinstance(instance_obj, boto.ec2.instance.Instance):
            raise NotImplementedError("Error: instance_obj is not a boto Instance object.")
        print "Waiting for Instance ID '{0}' to be in 'running' state.."\
              .format(instance_obj.id)
        increment = 0
        while instance_obj.state != u'running':
            sleep(1)
            increment += 1
            if increment >= timeout:
                print "wait_for_state_running::Error: Instance failed to run"\
                      " after {0} seconds.  Exiting..".format(timeout)
                # Exit with POSIX error code to handle in BASH, if necessary.
                sys.exit(1)
            instance_obj.update()
        
        print "Instance: {0} successfully started.".format(instance_obj.id)
        return True
            
    def get_tag_name(self):
        """ return ec2_tag_Name"""
        return self.ec2_tag_Name
    
    def create_security_group(self, name):
        """
        Create EC2 Security Group called "name".  By default, allows port 80 and
        22 open to the public.  If the group already exists, it will be used
        and no new group is created.
        
        
        args: name -> string
        :rval: self.conn.get_all_security_groups()[int]
        """
        for sg in self.conn.get_all_security_groups():
            if sg.name.lower() == name.lower():
                return sg

        # We need to create the SG (WARNING: Allows SSH and port 80 access)
        sg = self.conn.create_security_group(
            name, 
            'SG that allows Port 80 and 22 wide open.')
        # Allow ports 80 and 22 from any CIDR
        sg.authorize('tcp', 80, 80, '0.0.0.0/0')
        sg.authorize('tcp', 22, 22, '0.0.0.0/0')
        return sg
        
    def _inject_user_data(self, file_name='user_data.sh'):
        bootstrap = open(file_name).read()
        return bootstrap

if __name__ == "__main__":
    try:
        # Instantiate instance with arguments here.
        instance = CreateInstance(Name='Web-01-Dev', Region='us-east-1',
                                  Type='t2.micro', AMI='ami-20d3fc4a',
                                  key_pair='brian-test',
                                  security_group='webserver-with-ssh')
        # Call the CreateInstance.run() function to kick everything off.
        instance.run()
    except Exception as error:
        raise