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
def generate_tokugawa_service(installation_dir, executable_prefix, masternode_names):
    with open('/etc/init.d/tokugawa', 'w') as config:
        config.write('#! /bin/sh\n\
### BEGIN INIT INFO\n\
# Provides:          Tokugawad\n\
# Required-Start:\n\
# Required-Stop:\n\
# Default-Start:     2 3 4 5\n\
# Default-Stop:      0 1 6\n\
# Short-Description: Provides tokugawad service.\n\
### END INIT INFO\n\
\n');
        config.write("PIDOF_PROG=/bin/pidof\n");
        config.write("MASTERNODES=\"%s\"\n" %masternode_names);
        config.write("TOKUGAWAD_FOLDER=%s\n" %installation_dir);
        config.write("TOKUGAWAD_PREFIX=%s\n" %executable_prefix);
        config.write('case "$1" in\n\
    start)\n\
        for MN in ${MASTERNODES}; do\n\
            TOKUGAWAD_PROG="${TOKUGAWAD_FOLDER}/${TOKUGAWAD_PREFIX}_${MN}";\n\
            echo "Starting Tokugawad ${MN}";\n\
            sudo -u root ${TOKUGAWAD_PROG} -datadir=${TOKUGAWAD_FOLDER}/.${MN};\n\
        done\n\
    ;;\n\
    restart|reload|force-reload)\n\
        echo "Error: argument \'$1\' not supported" >&2\n\
        exit 3\n\
    ;;\n\
    status)\n\
        for MN in ${MASTERNODES}; do\n\
            TOKUGAWAD_PROG="${TOKUGAWAD_FOLDER}/${TOKUGAWAD_PREFIX}_${MN}";\n\
            TOKUGAWAD_PROG_PID=`sudo -u root ${PIDOF_PROG} ${TOKUGAWAD_PROG}`;\n\
            if [ $? -eq 0 ]; then\n\
                echo "Tokugawad ${MN} is running with pid ${TOKUGAWAD_PROG_PID}"\n\
            else\n\
                echo "Tokugawad ${MN} is not running"\n\
            fi\n\
        done\n\
    ;;\n\
    stop)\n\
        for MN in ${MASTERNODES}; do\n\
            TOKUGAWAD_PROG="${TOKUGAWAD_FOLDER}/${TOKUGAWAD_PREFIX}_${MN}";\n\
            TOKUGAWAD_PROG_PID=`sudo -u root ${PIDOF_PROG} ${TOKUGAWAD_PROG}`;\n\
            echo "Stopping Tokugawad ${MN}";\n\
            sudo -u root ${TOKUGAWAD_PROG} -datadir=${TOKUGAWAD_FOLDER}/.${MN} stop;\n\
        done\n\
    ;;\n\
    *)\n\
        echo "Usage: $0 start|stop" >&2\n\
        exit 3\n\
    ;;\n\
esac\n');
    #Set execution rights to file
    os.chmod('/etc/init.d/tokugawa', 0o755)

#Function to generate the tokugawa-server UFW application profile
def generate_ufw_profile(dest_folder, app, str_ports):
    #Default application profile name
    app_profilename = "%s-server" %app['name'].lower()
    #Write application profile
    with open(dest_folder+'/'+app_profilename, 'w') as config:
        config.write('[%s]\n' %app['name'])
        config.write('title=%s\n' %app['title'])
        config.write('description=%s\n' %app['description'])
        #Note protocol is tcp for that service only
        config.write('ports=%s/%s\n' %(str_ports, app['protocol']))

# Function to generate the Tokugawa.conf file under the MN directory
def generate_mn_tokugawaconf(dest_folder, mn):
    with open(dest_folder+'/'+'Tokugawa.conf', 'w') as config:
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

print('[INSTALLATION START]')

#Install all packages dependencies
print("  >> Installing required packages [TBD]")

#Loop through all and install them
for mn in cfg['MASTERNODES']:
    print("  >> Installing masternode: %s" %mn['name'])
    install_masternode(mn, installation_dir, executable, bootstrap)

#Install Tokugawa as boot service
print("  >> Configuring Tokugawa service")
masternode_names = "".join("%s " %mn['name'] for mn in cfg['MASTERNODES'])
masternode_executable_basename = os.path.basename(executable)
#Generate the service filename
generate_tokugawa_service(installation_dir, masternode_executable_basename, masternode_names)

#Firewall installation if present
print("  >> Configuring UFW firewall")
for app in cfg['FIREWALL']['PROFILES']:
    #Generate string in that way 1,2,3,4 and remove the trailing comma
    if app['ports'][0]=='MASTERNODES':
        str_ports = "".join("%s," %mn['port'] for mn in cfg['MASTERNODES'])
    else:
        str_ports = "".join("%s," %port for port in app['ports'])
    str_ports = str_ports[:-1]

    #Generate UFW application profile
    generate_ufw_profile('/etc/ufw/applications.d/', app, str_ports)

print('[INSTALLATION FINISH]')
print('')
print('Please execute as root: \'$ufw stop; ufw allow tokugawa; ufw allow openssh; ufw enable\' to enable the firewall!')
print('Additionally execute also as root: \'$systemctl enable tokugawa\' to allow tokugawa to start at boot.)
