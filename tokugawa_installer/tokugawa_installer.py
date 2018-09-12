#!/usr/bin/env python3
# Copyright (c) 2018 Lyndros <lyndros@hotmail.com>
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

###############################################################################
# MASTERNODE AUTOINSTALLER by Lyndros <lyndros@hotmail.com>                   #
###############################################################################
# Repository: https://github.com/Lyndros/crypto_tools                         #
#                                                                             #
# If you want to support and motivate me I accept donations even 1 TOK is     #
# always welcome :-)!                                                         #
# > ethereum address: 0x44F102616C8e19fF3FED10c0b05B3d23595211ce              #
# > tokugawa address: TjrQBaaCPoVW9mPAZHPfVx9JJCq7yZ7QnA                      #
#                                                                             #
###############################################################################
import yaml
import argparse
import sys
import os
import errno
import string
import random
from shutil import copyfile 

def show_banner():
    print('')
    print('###############################################################################')
    print('# MASTERNODE AUTOINSTALLER by Lyndros <lyndros@hotmail.com>                   #')
    print('###############################################################################')
    print('# Repository: https://github.com/Lyndros/crypto_tools                         #')
    print('#                                                                             #')
    print('# If you want to support and motivate me I accept donations even 1 TOK is     #')
    print('# always welcome :-)!                                                         #')
    print('# > ethereum address: 0x44F102616C8e19fF3FED10c0b05B3d23595211ce              #')
    print('# > tokugawa address: TjrQBaaCPoVW9mPAZHPfVx9JJCq7yZ7QnA                      #')
    print('#                                                                             #')
    print('###############################################################################')
    print('')

def show_warning(os_name):
    print('This installer is configured to run on %s' %os_name)
    input('Press ENTER to continue, or CTRL+C to abort installation.\n')

#Function to generate a random password
#Note: Passwords are enforced to be 12 characters long
def generate_password():
    min_char = 12
    max_char = 12
    allchar = string.ascii_letters + string.punctuation + string.digits
    password = "".join(random.choice(allchar) for x in range(random.randint(min_char, max_char)))
    
    return password

#Function to create a directory
#Note: All non existing parent directories will be created
def create_directory(absfolder_path):
    try:
        os.makedirs(absfolder_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

#Function to generate the tokugawa service
def generate_init_service(afilename, name, start_command, stop_command):
    with open(afilename, 'w') as config:
        config.write('#! /bin/sh\n');
        config.write('### BEGIN INIT INFO\n');
        config.write("# Provides:          %s\n" %name);
        config.write('# Required-Start:\n');
        config.write('# Required-Stop:\n');
        config.write('# Default-Start:     2 3 4 5\n');
        config.write('# Default-Stop:      0 1 6\n');
        config.write("# Short-Description: %s masternode service\n" %name);
        config.write('### END INIT INFO\n');
        config.write('\n')
        config.write("PIDOF_PROG=/bin/pidof\n");
        config.write('\n')
        config.write('case "$1" in\n');
        config.write('  start)\n');
        config.write("    echo \"Starting %s\";\n" %name);
        config.write("    sudo -u root %s;\n" %start_command);
        config.write('  ;;\n');
        config.write('  restart|reload|force-reload)\n');
        config.write('    echo "Error: argument \'$1\' not supported" >&2\n');
        config.write('    exit 3\n');
        config.write('  ;;\n');
        config.write('  status)\n');
        config.write("    PROG_PID=`sudo -u root ${PIDOF_PROG} %s`;\n" %start_command);
        config.write('    if [ $? -eq 0 ]; then\n');
        config.write("      echo \"%s is running with pid ${PROG_PID}\"\n" %name);
        config.write('    else\n');
        config.write("      echo \"%s is not running\"\n" %name);
        config.write('    fi\n');
        config.write('  ;;\n');
        config.write('  stop)\n');
        config.write("    PROG_PID=`sudo -u root ${PIDOF_PROG} %s`;\n" %start_command);
        config.write("    echo \"Stopping %s\";\n" %name);
        config.write("    sudo -u root %s;\n" %stop_command);
        config.write('  ;;\n');
        config.write('  *)\n');
        config.write('    echo "Usage: $0 start|stop" >&2\n');
        config.write('    exit 3\n');
        config.write('  ;;\n');
        config.write('esac\n');

    #Set access rights to file
    os.chmod(afilename, 0o755)

#Function to generate an UFW application profile
def generate_ufw_profile(afilename, name, title, description, ports, protocols):
    #Write application profile
    with open(afilename, 'w') as config:
        config.write("[%s]\n"           %name)
        config.write("title=%s\n"       %title)
        config.write("description=%s\n" %description)
        #Build string for ports
        str_ports     = "".join("%s," %p for p in ports)
        str_protocols = "".join("%s/" %p for p in protocols)
        #Add ports and protocols removing trainling char
        config.write("ports=%s/%s\n"    %(str_ports[:-1], str_protocols[:-1]))

    #Set access rights to file
    os.chmod(afilename, 0o644)

# Function to generate the Tokugawa.conf file under the MN directory
def generate_masternode_tokugawaconf(afilename, mn):
    with open(afilename, 'w') as config:
        config.write('rpcuser=myrpcuser%s\n' % mn['name'].lower())
        config.write('rpcpassword=%s\n' % generate_password())
        config.write('rpcport=%s\n' % mn['rpcport'])
        config.write('server=1\n')
        config.write('listen=1\n')
        config.write('daemon=1\n')
        config.write('port=%s\n' % mn['port'])
        config.write('masternodeaddr=%s:%s\n' % (mn['ip'], mn['port']))
        config.write('masternode=1\n')
        config.write('masternodeprivkey=%s\n' % mn['privkey'])

    #Set access rights to file
    os.chmod(afilename, 0o644)


def install_tokugawa_masternode():
    return "tokugawa"


def install_smartcash_masternode():
    return "smartcash"

switcher = {
    'Tokugawa':  install_tokugawa,
    'Smartcash': install_smartcash
}

def install_masternode(coinname, configuration):
    # Get the function from switcher dictionary
    func = switcher.get(coinname, "nothing")
    # Execute the function
    return func()

#Function to install a masternode in the desire location
def install_masternode(mn, installation_dir, executable, bootstrap):
    #Masternode directory creation
    masternode_dir = os.path.abspath(installation_dir+"/."+mn['name'])
    create_directory(masternode_dir)
    #Tokugawa.conf file generation
    generate_mn_tokugawaconf(masternode_dir, mn)
    #Define binary file name for masternode
    masternode_executable_basename = os.path.basename(executable + "_" + mn['name'])
    masternode_executable=os.path.abspath(installation_dir+'/'+masternode_executable_basename)
    #Copy daemon file with the following name
    copyfile(executable, masternode_executable)
    #Set execution rights to file
    os.chmod(masternode_executable, 0o755)
    #Copy bootstrap if present
    if bootstrap:
        masternode_bootstrap_basename= os.path.basename(bootstrap)
        masternode_bootstrap=os.path.abspath(masternode_dir+'/'+masternode_bootstrap_basename)
        copyfile(bootstrap, masternode_bootstrap)

###############################################################################
#                                    MAIN                                     #
###############################################################################

#Program input parameters
parser = argparse.ArgumentParser()
parser.add_argument("installation_dir",   help="The installation directory.")
parser.add_argument("executable",         help="The tokugawad binary file.")
parser.add_argument("configuration",      help="The installer configuration file.")
parser.add_argument("--bootstrap",        help="The bootstrap file.")
args = parser.parse_args()

#Build abs names to avoid problems
installation_dir = os.path.abspath(args.installation_dir)
executable = os.path.abspath(args.executable)
configuration = os.path.abspath(args.configuration)
if args.bootstrap:
    bootstrap = os.path.abspath(args.bootstrap)
else:
    bootstrap = ""

#Check input files
if (not os.path.exists(executable)) or (not os.path.exists(configuration)):
    print("Error! One of the supplied files does not exist.")
    sys.exit(-1)

#Parse the configuration file
with open(configuration, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#Show presentation
show_banner()
show_warning(cfg['SYSTEM']['description'])

print('[PREREQUISITES]')
print('  >> Installing required packages [TBD]')

print('[INSTALLATION START]')
for mn in cfg['MASTERNODES']:
    #Masternode name header
    print("  %s_%s" %(coin_name, %mn['name']))
    #Install masternode software
    print('    >> Installing masternode')
    install_masternode(mn, installation_dir, executable, bootstrap)
    #Generating boot service
    print('    >> Generating /etc/init.d service')
    generate_masternode_service(mn, )
    masternode_names = "".join("%s " %mn['name'] for mn in cfg['MASTERNODES'])
    masternode_executable_basename = os.path.basename(executable)
    #Generate the service filename
    generate_tokugawa_service(installation_dir, masternode_executable_basename, masternode_names)
    #Generating firewall profile
    print('   >> Generating UFW firewall rules')
    generate_ufw_profile('/etc/ufw/applications.d/', app)
    #Allow firewall profile

#Enable services
if cfg['services'] == 'enabled':
    print(' >> Enabling services')

#Enable firewall
if cfg['firewall'] == 'enabled':
    print(' >> Activating firewall')

print('[INSTALLATION FINISH]')
print('')
print('Please execute as root: \'$ufw stop; ufw allow tokugawa; ufw allow openssh; ufw enable\' to enable the firewall!')
print('Additionally execute also as root: \'$systemctl enable tokugawa\' to allow tokugawa to start at boot.)
