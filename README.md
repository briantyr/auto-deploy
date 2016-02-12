# auto-deploy
Provisions an EC2 instance in AWS and configures Nginx with a static page.  Written in Python and used to demo automation of provisioning an EC2 instance as well as configuring Nginx with a static page for demo purposes.

*** Requirements ***
- Python 2.7.x
- boto python library (pip install boto)

I installed boto under a Python virtual environment to keep the applications packages separated from my system Python packages.  You can do this by executing 'sudo pip install virtualenv' and then create the virtualenv with which you can install boto in.

You will also need to configure your users' ~/.boto file (create it if it does not exist to match your AWS environment's keys.
For example:

    [Credentials]
    aws_access_key_id = XXXXXXXXXXXXXXXXXXX
    aws_secret_access_key = yyeaii3oafj3akjfa....
    

After making the above changes, you should only need to modify the CreateInstance.py class when it is instantiated, to match your environment.  Once doing so, executing the Python script should automatically provision an EC2 instane in AWS and install Nginx with a static website that says "Automation for the people!", which you can access by going to the public IP address that AWS generates for you.

