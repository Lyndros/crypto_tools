#!/usr/bin/env python3
# Copyright (c) 2018 Lyndros <lyndros@hotmail.com>
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

###################################################################
# If you want o support this repository I accept donations        #
# even 1 TOK is always welcome :-)!                               #
# > ethereum address: 0x44F102616C8e19fF3FED10c0b05B3d23595211ce  #
# > tokugawa address: TjrQBaaCPoVW9mPAZHPfVx9JJCq7yZ7QnA          #
###################################################################
import yaml
import argparse
import sys
import os
import errno
import string
import random
from shutil import copyfile 

#Funtion to generate a random password
def generate_password():
    min_char = 12
    max_char = 12
    allchar = string.ascii_letters + string.punctuation + string.digits
    password = "".join(random.choice(allchar) for x in range(random.randint(min_char, max_char)))
    
    return password

#Non existing parent directories will be created
def create_directory(absfolder_path):
    try:
        os.makedirs(absfolder_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

#Function to generate the Tokugawa.conf file under the MN directory
def generate_tokugawaconf(masternode_folder, mn):
    with open(masternode_folder+'/Tokugawa.conf', 'w') as config:
        config.write('rpcuser=myrpcuser%s\n' %mn['name'].lower())
        config.write('rpcpassword=%s\n' %generate_password())
        config.write('rpcport=%s\n' %mn['rpcport'])
        config.write('server=1\n')
        config.write('listen=1\n')
        config.write('daemon=1\n')
        config.write('port=%s\n' %mn['port'])
        config.write('masternodeaddr=%s:%s\n' %(mn['ip'], mn['port']))
        config.write('masternode=1\n')
        config.write('masternodeprivkey=%s\n' %mn['privkey'])

#Function to generate the tokugawa-server UFW application profile
def generate_tokugawa_firewall_rules(port_list):
    with open(/etc/ufw/applications.d/tokugawa-server_testinst', 'w') as config:
        config.write('[Tokugawa]\n')
        config.write('title=Tokugawa Daemon\n')
        config.write('description=Tokugawa Daemon FW configuration by Lyndros autoinstaller\n')
        #Generate string in that way 1,2,3,4/tcp
        str_ports = "".join("%s," %i for i in port_list)
        ufw_ports = str_ports[:-1]
        #Note protocol is tcp for that service only
        config.write('port=%s/tcp' %ufw_ports)

#Install masternode
def install_masternode(daemon_file, bootstrap_file, dest_folder, mn_config):
    print("Installing masternode: %s" %mn_config['name'])
    #Masternode directory creation
    masternode_folder = dest_folder+"."+mn_config['name']
    create_directory(masternode_folder)
    #Tokugawa.conf file generation
    generate_tokugawaconf(masternode_folder, mn_config)  
    #Define binary file name for masternode
    masternode_binary_file = daemon_file + "_" + mn_config['name']
    #Copy daemon file with the following name
    copyfile(daemon_file, dest_folder+'/'+masternode_binary_file)

#START THE MAIN ACTION#
#Define my program input parameters
parser = argparse.ArgumentParser()
parser.add_argument("binary_file", help="The tokugawad binary file.")
parser.add_argument("dest_folder", help="Base destination folder.") 
parser.add_argument("--bootstrap", help="The boostrap file.")
parser.add_argument("config_file", help="The masternodes configuration file.")
args = parser.parse_args()

#Check input parameters
if (not os.path.exists(args.binary_file)) or (not os.path.exists(args.config_file)):
    print("Error! One of the supplied files does not exist.")
    sys.exit(-1)

#Parse the configuration file
with open(args.config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#Install all masternodes
for mn_config in cfg['MASTERNODES']:
    install_masternode(args.binary_file, args.bootstrap, args.dest_folder, mn_config)

#Generate Tokugawa service file

#Generate UFW application configuration
port_list = []
for mn_port in cfg['MASTERNODES']['port']:
    port_list.add(mn_port)

print(port_list)