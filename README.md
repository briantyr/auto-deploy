# auto provision, deploy, and configure Webserver EC2 instance in AWS

# https://github.com/briantyr/auto-deploy
-------------------------------------------------------------------------------
*** Description ***
A small DevOps demonstration in provisioning a single AWS resource (EC2 instance)
and install, configure, enable a static page, and restart Nginx so that it 
listens on port 80, and displays a simple HTML page with a specific message.

*** Implementation Overview ***
I decided to write this little project completely in Python and use the official 
AWS API's instead of using familiar tools such as Terraform, Ansible, and Puppet
because I really wanted to dive deep into not only building my own infrastructure and 
configuration management using a single language, but also because Python and 
the modules used are cross platform and require very little effort to install. 

Finally, modern versions of Python come pre-installed by default on every UNIX 
derived operating system as system dependencies, so this example has tested & 
works on OS X (El Capitan), Ubuntu 14.04, CentOS 7, and even Windows 7.  
In the default configuration, I am specifying my AMI as Ubuntu 14.04, 
but any differences between Linux OS's are easy to abstract into separate
functions if necessary, and you can always change the AMI if you'd like.

Another advantage of working with the low level Boto API is that I'm forced to
learn it and start small.  In the end, this means I can not only write my own 
code coverage unit tests to verify my functional code and expected results, but 
I can also write my own infrastructure tests with one of the many Python
testing frameworks.

*** Recommended Requirements ***
- Python 2.7.x
  * Support for standard library string.Template backport from Python 3.x)
  * Tested in Python 2.7.10 and 2.7.11
- Python module(s): 
  * boto (Amazon official Python SDK) >= v. =2.39.0
  * (optional - but highly recommended) virtualenv and virtualenvwrapper for 
    convenience, security, and isolation from the rest of your systems python 
    modules.  *NOTE*: You must have sudo access to the machine you run this
    script on in order to install the virtualenv packages.

*** Recommended Pre-Requisites***
As user with sudo, use pip to install 'virtualenv' and 'virtualenvwrapper' packages.
I installed boto under a Python virtual environment to keep the applications packages separated from my system Python packages.  You can do this by executing 'sudo pip install virtualenv' and then create the virtualenv with which you can install boto in.

You will also need to configure your users' ~/.boto file (create it if it does not exist to match your AWS environment's keys.
If you do not have a key;acess)
For example:

    [Credentials]
    aws_access_key_id = <your access key>
    aws_secret_access_key = <your secret access key>
    

After making the above changes, you should only need to modify the CreateInstance.py class when it is instantiated, to match your environment.  Once doing so, executing the Python script should automatically provision an EC2 instane in AWS and install Nginx with a static website that says "Automation for the people!", which you can access by going to the public IP address that AWS generates for you.

