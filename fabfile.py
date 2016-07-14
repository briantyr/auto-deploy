from fabric.api import env, run, sudo, execute

env.hosts = ['ec2-52-90-73-119.compute-1.amazonaws.com']
#env.hosts.extend('new-host')
env.user = 'ubuntu'
env.key_file = '~/.ssh/brian-test.pem'

def install_nginx():
    sudo('apt-get install nginx')
