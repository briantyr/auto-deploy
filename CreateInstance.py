#!/usr/bin/env python

# CreateInstance.py
#
# Brian Taylor
#
#
# This Class is a wrapper around the Python module, boto. Besides that module,
# I addded some custom code for basic error checking on the arguments you pass
# into the class.  I am using cloud-init to configure nginx and the webserver
# configuration, however further down in the CreateInstance::run() function, you
# could extend it to use Fabric / Paramiko to SSH into the instance.
#
# Requirements:
#    I would recommend using a virtualenv if you don't want boto installed
#    globally.
#
#    boto >=2.38 (pip install boto)
#    
#    Add the following to your ~/.boto file (create it if it doesn't exist) to
#    match your access key environment.
#    
#

import os
import sys
import time

import boto.ec2


class CreateInstance(object):
    '''
    CreateInstance
    
    Class to instantiate, provision, and configure a single EC2 instance using
    Cloud Formation templates and the official Python SDK.
    Requires:
    'boto' module.
    
    Designed to create an EC2 instance in AWS and take advantage of cloud-init
    by supplying user-data.
    
    '''
    
    # These variables are passed in when this class is instantiated.  Changing
    # them here will have no effect, they are only here for reference.
    region = None
    instance_type = None
    key_pair = None
    ec2_tag_Name = None
    ami = None
    security_group = None
    
    def __init__(self, *args, **kwargs):
        '''
        __init__(self, *args, **kwargs):
        
        Accepts a bunch of named parameters and automatically lowercases them
        when doing comparisons, so the class accepts case insensitive args.
        
        This constructor populates the variables above.
        
        '''
        
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
        '''
        Checks that the variables passed into the class are legit and validates
        what it can.
        '''
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
        
        self._validate_input()
        
        # Returns class boto.ec2.instance.Reservation object
        # http://boto.cloudhackers.com/en/latest/ref/ec2.html#boto.ec2.instance.Reservation
        self.instance_id = self.conn.run_instances(image_id=self.ami, 
                                                        key_name=self.key_pair, 
                                                        security_groups=[self.security_group],
                                                        instance_type=self.instance_type,
                                                        user_data=self._inject_user_data()
                                                        )
        
        # Add name tag
        #boto.ec2.ec2object.TaggedEC2Object(self.conn).add_tag('Name', 
        #                                                     self.ec2_tag_Name)
                
    def get_tag_name(self):
        return self.ec2_tag_Name
    
    def create_security_group(self, name):
        '''
        Create EC2 Security Group called "name".  By default, allows port 80 and
        22 open to the public.  If the group already exists, it will be used
        and no new group is created.
        
        
        args: name -> string
        '''
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
    
    # Instantiate instance with arguments here.
    instance = CreateInstance(Name='Web-01-Dev', Region='us-east-1',
                              Type='t2.micro', AMI='ami-20d3fc4a',
                              key_pair='brian-test',
                              security_group='webserver-with-ssh')
    # Call the CreateInstance->run() function to kick everything off.
    instance.run()