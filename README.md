
### Auto provision, deploy, and configure Webserver EC2 instance in AWS

#####**Description:**
This class was intended to demonstrate an exercise using the Python AWS SDK 
(boto), however it will probably be extended to do much more over time,
especially as I continue to test additional infrastructure changes with the SDK, implement code coverage unit tests as well as infrastructure tests, hopefully all in Python.

This class (CreateInstance) has some wrapper functions around the 'boto' module 
to make things seem more 'pythonic'.  However, the functionality is only
wrapped for certain actions, all of which are used for the main purpose of
this class, which is to demo the provisioning and configuration of a single
EC2 instance in AWS.  The configuration uses cloud-init with dynamic supplied
user data to use APT to update, install nginx, configure and symlink the sites
available virtualhost file into /etc/nginx/sites-enabled/.  It then builds a
static html page at the location nginx config is expecting, and outputs a 
simple \<h1> message, by default saying **"Automation for the people!"** when browsing to the EC2 Instance IP.

This is object oriented and as such, may be expanded, reduced, built around,
inherited from, imported into another project, using basic principles of OOP.
Most importantly, the functions can be reused within the same project to
follow DRY coding principles.

You may import any function in **CreateInstance.py** or use inheritance and override/extend existing funcitons.
For example, to import and create your own class that inherits CreateInstance, you can simple use something like:
```python
from CreateInstance import CreateInstance

class AwesomeInstanceCreator(CreateInstance):
    def __init__(self, *args,**kwargs):
        # Call super() function to instantiate base class constructor
        # At this point, you inherit all functions from the CreteInstance class (CreateInstance.py) and call them.
        super(AwesomeInstanceCreator, self).__init__(*args, **kwargs)
        
    def do_something_cooler_than_my_class(self):
        # Do stuff in your inherited class.
        pass
```
.. or .. you can write an "Factory class" that instantiates CreateInstance within your class and object composition to keep your code and my code decoupled, such as:
```python
from CreateInstance import CreateInstance

class FactoryInstanceCreator(object):
    def __init__(self, *args, **kwargs):
        self.create_instance_objects = []
        # Create 5 instances to create 5 CreateInstace objects or something crazy like that. (this has not been tested, YMMV)
        for inst_num in range(0, 4):
            self.create_instance_objects.append(CreateInstance(Name='Web-{0}-dev".format(inst_num), **kwargs)
```
**Implementation Overview**

I decided to write this little project completely in Python and use the official 
AWS API's instead of using familiar tools such as Terraform, Ansible, and Puppet
because I really wanted to dive deep into not only building my own infrastructure and 
configuration management using a single language, but also because Python and 
the modules used are cross platform and require very little effort to install. 

Finally, modern versions of Python come pre-installed by default on every UNIX 
derived operating system as system dependencies, so this example has tested & 
works on OS X (El Capitan - a bit shakey due to module bug), Ubuntu 14.04, CentOS 7, and even Windows 7.  
In the default configuration, I am specifying my AMI as Ubuntu 14.04, 
but any differences between Linux OS's are easy to abstract into separate
functions if necessary, and you can always change the AMI if you'd like.

Another advantage of working with the low level Boto API is that I'm forced to
learn it and start small.  In the end, this means I can not only write my own 
code coverage unit tests to verify my functional code and expected results, but 
I can also write my own infrastructure tests with one of the many Python
testing frameworks.

*** Required Requirements ***
- Python 2.7.x
  * Support for standard library string.Template backport from Python 3.x)
  * Tested in Python 2.7.10 and 2.7.11
- Python module(s): 
  * boto (Amazon official Python SDK) >= v. =2.39.0
  * (optional - but highly recommended) virtualenv and virtualenvwrapper for 
    convenience, security, and isolation from the rest of your systems python 
    modules.  *NOTE*: You must have sudo access to the machine you run this
    script on in order to install the virtualenv packages.

**Recommended Pre-Requisites**

As user with sudo, use pip to install 'virtualenv' and 'virtualenvwrapper' packages.  'virtualenvwrapper' provides some convienient methods to make creating a virtualenv much faster and better oganized.

You will also need to configure your users' ~/.boto file (create it if it does not exist and make sure it matches your AWS environment's 
keys.

For example:

    [Credentials]
    aws_access_key_id = <your access key>
    aws_secret_access_key = <your secret access key>
    

_**OS X (El Capitan) virtualenvwrapper installation issues**_

El Capitan has some problems with the Python 'six' module when installing virtualenvwrapper but you can easily fix it by runninng the following commands as sudo, then continue on:

    sudo pip install --upgrade pip
    sudo pip install --upgrade virtualenv
    sudo pip install pbr
    sudo pip install —no-deps stevedore
    sudo pip install —no-deps virtualenvwrapper
 
**Ubuntu 14.04 and other linux distributions**

     sudo pip install --upgrade pip
     sudo pip install --upgrade virtualenv virtualenvwrapper

**Now on both OS X or Ubuntu (and probably Windows), finish the installation**

    **AS YOUR REGULAR USER**
    
    cd ~/
    git clone https://github.com/briantyr/auto-deploy.git
    cd auto-deploy
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bash_profile
    source ~/.bash_profile

_**Now you should have access to new shell functions, such as mvirtualenv, workon, etc.  We're going to create a unique virtualenv using one of the virtualenvwrapper helper functions to make a new virtualenv and use our packages in requirement.txt to install to it.**_

    mkvirtualenv -r requirements.txt auto-deploy

**(Names your virtualenv auto-deploy in ~/.virtualenv/auto-deploy ... rename as you feel necessary in your mkvirtualenv call)**

**At this point, it should drop you into the auto-deploy virtualenv and you should only have the minimum installed packages you require for this program to work.**

**You no longer need sudo access and can run everything out of the cloned git repo.**
Ensure you're working on the 'auto-deploy' virtualenv:

    workon auto-deploy

Type: **pip list** and you should receive onyl a mimimal amount of packages back, including boto, that looks something like below.  If so, are good to execute the Python code in CreateInstance.py, but you may want to change the keyword arguments athe botttom.

    (auto-deploy) dev:stelli-project btaylor$ pip list
    boto (2.39.0)
    pip (8.0.2)
    setuptools (20.0)
    wheel (0.29.0)
    chmod +x CreateInstance.py
    (modify CreateInstance.py run arguments)
    ./CreateInstance.py
    
#### **More to come on installation, newer code, and running later.  Contact me if anything is broken.**

**In the meantime, feel free to open CreateInstance.py and change the arguments at the bottom to match yuour keypair, security_group, instance_tags, etc.**

