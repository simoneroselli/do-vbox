#!/usr/bin/env python

import hashlib, os
import paramiko, sys
from getpass import *


# MD5 sum
def md5Sum(filename):
    f = open(filename, 'r')
    md5 = hashlib.md5()
    while True:
        data = f.read(8196)
        if not data:
            break
        md5.update(data)

    md5hash = md5.hexdigest()
    f.close()
    return md5hash

# Create a virtual machines python list (virtual_machines = [] )
# from vbox-index text file
class VirtualMachine(object):
    def __init__(self, name=None, md5=None, desc=None, updated=None, size=None, ostype=None, arc=None, ram=None, vram=None, login=None, repo=None):
        self.name = name
        self.md5 = md5
        self.desc = desc
        self.updated = updated
        self.size = size
        self.ostype = ostype
        self.arc = arc
        self.ram = ram
        self.vram = vram
        self.login = login
        self.repo = repo

    def isValid(self):
        return self.name is not None and self.md5 is not None
    
    @staticmethod
    def parseFileList(filename):
        """ Put vbox-index file into a python list """
        virtual_machines = []

        if not os.path.exists(filename):
            return virtual_machines

        f = open(filename, "r")
        vm = VirtualMachine()
        for line in f:
            line = line.strip()
            if len(line) == 0:
                if vm.isValid():
                    virtual_machines.append(vm)
                vm = VirtualMachine()
            else:
                # cerco i : (split su i :)
                # ottengo key: valore
                key, value = line.split(':',1)
                key = key.strip()
                value = value.strip()
                setattr(vm, key, value)             
        if vm.isValid():
            virtual_machines.append(vm)
        f.close()

        return virtual_machines
    
    @staticmethod
    def saveFileList(filename, vm_list):
        fd = open(filename, 'w')
        for vm in vm_list:
            for key, value in vm.__dict__.items():
                if value: fd.write(key + ': ' + value + '\n')
            fd.write('\n')
        fd.close() 
    
    @staticmethod
    def appendFileList(filename, vm_list):
        fd = open(filename, 'a')
        for line in vm_list:
            fd.write(line)

        fd.write('\n')
        fd.close() 

# Commit parameters class
class vboxCommit(object):
        def __init__(self, host=None, user=None, port=None, key=None):
            self.host = host
            self.user = user
            self.port = port
            self.key = key

        def __str__(self):
            return " ".join(["Host:", self.host, "User:", self.user, "Port:",
                self.port, "Key:", self.key])

        @staticmethod
        def parseCfg(cfgfile):
            """ Retrieve all connection parameters from /etc/do-vbox/commit config file
            """
            commit_param = {}

            f = open(cfgfile, 'r')
            section = ""
            for line in f:
                line = line.strip()
                if len(line) == 0:
                    pass
                elif line.startswith("#"):
                    pass
                elif line.startswith("["):
                    section = line[1:-1]
                    cmmt = vboxCommit()
                    commit_param[section] = cmmt
                else:
                    key,value = line.split('=',1)
                    key = key.strip()
                    value = value.strip()
                    setattr(cmmt, key, value)
            return commit_param

        @staticmethod
        def vboxSsh(host, username, port, key, local, remote):
            """ Establish a ssh connection to a given or retrieved repository URL and
            upload the locally committed VM 
            """
            keyfile = os.path.expanduser(key)
            server, user = (host, username)
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                key = paramiko.DSSKey.from_private_key_file(key)
            except paramiko.PasswordRequiredException:
                passph = getpass('Type your key passphrase: ')
                key = paramiko.DSSKey.from_private_key_file(key, passph)
            
            # Connection
            ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
            ssh.connect(server, port, username=user)

            local_path = local
            remote_path = remote

            sftp = ssh.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            ssh.close()

