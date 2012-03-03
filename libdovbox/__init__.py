#!/usr/bin/env python

import hashlib, os
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


