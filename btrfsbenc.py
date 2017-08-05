#!/usr/bin/python3
import subprocess as sp
from os.path import basename
from os import path
from os import listdir
import pexpect
#List of backupvolumes
uuiddict={'a2ffcdb8-0372-41d1-b2a2-a62ea16aeaf1':'B5'} #uuid:name
uuidlist=list(uuiddict)
MAX=9
verbosity_level=2
verbose_groups={}
DEVC='device: \"'
Q='\"'
DIRC='dir: \"'
setup_mountpoint_done=False
setup_snapshot_done=False
setup_decryptvol_done=False
basedir='/mnt/backup/'

def get_device_name(line):
    name=''
    for char in line:
        if not char is ' ':
            name=name+char
        else: break
    if name[-1] is ':':
        return name[:-1]
    else: raise Exception('damned, where is the colon. fix code bro')

def get_name_at_start_of_line(line):
    return get_device_name(line)

def v(message,minlevel,**kwargs):
    ##prints only highes allowed level of a group
    ##specify smallest highest first
    if 'g' in kwargs and 'r' in kwargs:
            group = kwargs['g']
            verbose_groups.pop(group)
    if minlevel <= verbosity_level:
        if 'g' in kwargs and not 'r' in kwargs:
            group = kwargs['g']
            if group in verbose_groups:
                if minlevel >= verbose_groups[group]:
                    verbose_groups.update({group:minlevel})
                    print(message)
            else:
                verbose_groups.update({group:minlevel})
                print(message)
        else:
            print(message)
    
def check_if_devname_is_crypto_LUKS(dev_name):
    foundline=False
    for line in blkidout:
        if get_device_name(line) == dev_name:
            v('found line of blkidout with device name matching device name',6)
            found=line.find("TYPE=")
            v('found type keyword in line of blkidout',6)
            if found is -1:
                raise Exception("no type found in line : "+line)
            found=line.find("TYPE=\""+"crypto_LUKS"+"\"")
            if not found is -1: return True
            else: return False
            foundline=True
    if not foundline: raise Exception("devname not found in the lines.")

def check_luks_open(devname):
    cmd=['sudo','dmsetup','deps','-o','blkdevname']
    out=sp.check_output(cmd).decode().splitlines()
    #print(out)
    for line in out:
        if line.find("("+basename(devname)+")") is not -1:
            #print('found')
            name=get_name_at_start_of_line(line)
            #print(name)
            cmd2=['sudo','cryptsetup','status',name]
            out2=sp.check_output(cmd2).decode().splitlines()
            #print(out2[0])
            if out2[0].find(name+' is active') is not -1:
                #opened
                return True
            else: return False
    return False

def get_crypto_LUKS_volume_devname(dev_name):
    cmd=['sudo','dmsetup','deps','-o','blkdevname']
    out=sp.check_output(cmd).decode().splitlines()
    #print(out)
    for line in out:
        if line.find("("+basename(dev_name)+")") is not -1:
            #print('found')
            name=get_name_at_start_of_line(line)
            cmd2=['sudo','cryptsetup','status',name]
            out2=sp.check_output(cmd2).decode().splitlines()
            #print(out2[0])
            f=out2[0].find(name+' is active')
            if f is not -1:
                mycryptvol_devname=out2[0][0:f+len(name)]
                return mycryptvol_devname
            else: raise Exception('volume devname can not determined if cryptvol is inactive and it  seems not active')
    raise Exception( 'devname( '+dev_name+' ) not found in output of :'+str(cmd)+' Probably not open.')
    
def open_crypto_LUKS(encrypt_dev_name,decrypt_vol_name):
    cmd=['sudo','cryptsetup','luksOpen',encrypt_dev_name,decrypt_vol_name]
    child = pexpect.spawn(cmd[0],cmd[1:])
    child.interact()

def close_crypto_LUKS(decrypt_vol_name):
    cmd=['sudo','cryptsetup','luksClose',decrypt_vol_name]
    sp.check_call(cmd)

def setup_snapshot():
    global snap
    time=sp.check_output(['date','-Is']).decode().splitlines()
    snap='/snapshot-start-'+time[0]
    a=sp.check_call(['sudo','btrfs','sub','snap','-r','/',snap])
    global setup_snapshot_done
    setup_snapshot_done=True

def setup_decryptvol():
    global blkidout
    global backupdecryptvolname
    global backupdecryptvol_devname
    global encrypted_dev_name
    global setup_decryptvol_done
    blkidout=sp.check_output(['sudo','blkid']).decode().splitlines()
    for line in blkidout:
        v('processing line of blkidout: '+line,9)
        for uuid in uuidlist:
            v('uuid: '+uuid,9)
            found=line.find("UUID=\""+uuid+"\"")
            if found is not -1:
                v('backupdevice found: '+uuid,2)
                v('uuid found in line of blkidout, means backupdevice found: '+uuid,4)
                dev_name=get_device_name(line)
                v('could obtain device name: '+dev_name,5)
                v('checking if type is crypto_LUKS by useing the device name for searching the whole blkidout. Ignoring that there is already the line found...',7)
                v('checking if type is crypto_LUKS by useing the device name for searching the whole blkidout. Ignoring that there is already the line found...',3)
                is_crypto_LUKS=check_if_devname_is_crypto_LUKS(dev_name)
                backupdecryptvolname='backupdecryptvol_'+uuiddict[uuid]
                if is_crypto_LUKS:
                    encrypted_dev_name=dev_name
                    v('it is crypto_LUKS',7)
                    if check_luks_open(dev_name):
                        v('it is already open',3)
                        backupdecryptvol_devname=get_crypto_LUKS_volume_devname(dev_name)
                        v('backupdecryptvol devname is : \"'+backupdecryptvol_devname+'\"',2)
                        setup_decryptvol_done=True
                    else:
                        v('it is not open. opening , name will be: \"'+backupdecryptvolname+'\" ...',2)
                        open_crypto_LUKS(dev_name,backupdecryptvolname)
                        backupdecryptvol_devname=get_crypto_LUKS_volume_devname(dev_name)
                        v('backupdecryptvol devname is : \"'+backupdecryptvol_devname+'\"',2)
                        setup_decryptvol_done=True
                else: raise Exception('found uuid but is not crypto_LUKS... something is wrong')

def check(function):
    def checker(*args):
        if function(*args):
            pass
        else: raise Exception('Check failed: '+function.__name__+' '+str(args))
    return checker

def checkisnot(function):
    def checker(*args):
        if not function(*args):
            pass
        else: raise Exception('Check is not failed: '+function.__name__+' '+str(args))
    return checker

def path_is_mountpoint(path):
    cmd=['mountpoint',path]
    try:
        if sp.check_call(cmd,stdout=sp.DEVNULL,stderr=sp.DEVNULL) is 0:
            #is mountpoint
            return True
        else:
            return False
            v('warning: not expected that case',1)
    except sp.CalledProcessError:
        return False
    
def try_sys_cmd(cmdlist):
    sp.check_call(cmdlist,stdout=sp.DEVNULL,stderr=sp.DEVNULL)
    
def setup_basedir():
    basedir='/mnt/backup/' ##need trailing slash
    check(path.isdir)(basedir)
    v('basedir \"'+basedir+'\" ok',5)

def dir_is_empty(dir):
    if len(listdir(dir)) is 0:
        return True
    else: return False

def mount(dev,dir):
    cmd=['sudo' ,'mount',dev,dir]
    try_sys_cmd(cmd)
    
def _unmount(dev):
    cmd=['sudo' ,'umount',dev]
    try_sys_cmd(cmd)

def setup_backupdir():
    global backupdir
    backupdir=basedir+backupdecryptvolname
    if path.exists(backupdir):
        check(path.isdir)(backupdir)
        v('backupdir is existing dir',3)
    else:
        v('try to create dir: \"'+backupdir,2)
        try_sys_cmd(['sudo', 'mkdir',backupdir])
        check(path.isdir)(backupdir)
        v('backupdir is there now: \"'+backupdir+'\"',3)


def is_dev_mounted_to_dir(dev,dir):
    v('checking if dev: \"'+dev+'\" is mounted to dir: \"'+dir,5)
    cmd=['cat' ,'/proc/mounts']
    out=sp.check_output(cmd).decode().splitlines()
    for line in out:
        if line.find(dev) is not -1:
            v('#dev is mounted to somewhere...',8)
            if line.find(dir) is -1:
                v('#but on this line not to dir',8)
            else:
                v('#and it is dir',8)
                v('--> True',5)
                return True
    v('--> False',5)
    return False

def is_dev_mounted_elsewhere(dev,dir):
    v('checking if dev: \"'+dev+'\" is mounted to somewhere else than dir: \"'+dir,5)
    cmd=['cat' ,'/proc/mounts']
    out=sp.check_output(cmd).decode().splitlines()
    for line in out:
        if line.find(dev) is not -1:
            v('#dev is mounted to somewhere...',8)
            if line.find(dir) is -1:
                v('#but its something else than backupdir...',8)
                v('--> True',5)
                return True
    v('--> False',5)
    return False

def is_dev_only_thing_mounted_here(dev,dir):
    v('checking if dev: \"'+dev+'\" is the only thing mounted to dir: \"'+dir,5)
    cmd=['cat' ,'/proc/mounts']
    out=sp.check_output(cmd).decode().splitlines()
    for line in out:
        if line.find(dir) is not -1:
            v('#something is mounted to dir',8)
            if line.find(dev) is -1:
                v('#but its something else than dev...',8)
                v('--> False',5)
                return False
    v('--> True',5)
    return True

def is_mountpoint_ok(dev,dir):
    if path_is_mountpoint(dir):
        if is_dev_mounted_to_dir(dev,dir):
            if is_dev_only_thing_mounted_here(dev,dir):
                if not is_dev_mounted_elsewhere(dev,dir):
                    return True
    return False
    
def setup_mountpoint():
    global setup_mountpoint_done
    setup_basedir()
    setup_backupdir()
    if path_is_mountpoint(backupdir):
        check(is_mountpoint_ok)(backupdecryptvol_devname,backupdir)
        setup_mountpoint_done=True
        v('mountpoint setup successfull: '+backupdir,2,g=1)
        v('mountpoint setup successfull',1,g=1)
        v('',9,g=1,r=1)
    else:
        checkisnot(is_dev_mounted_elsewhere)(backupdecryptvol_devname,backupdir)#if is, better abort
        check(dir_is_empty)#else better abort
        mount(backupdecryptvol_devname,backupdir)
        check(is_mountpoint_ok)(backupdecryptvol_devname,backupdir)
        setup_mountpoint_done=True
        v('mountpoint setup successfull: '+backupdir,2,g=1)
        v('mountpoint setup successfull',1,g=1)
        v('',9,g=1,r=1)

def unmount():
    if is_dev_mounted_to_dir(backupdecryptvol_devname,backupdir):
        if not is_dev_mounted_elsewhere(backupdecryptvol_devname,backupdir):
            _unmount(backupdecryptvol_devname)
            setup_mountpoint_done=False
        else:
            setup_mountpoint_done=False
            raise Exception(DEVC+backupdecryptvol_devname+Q+' is mounted elsewhere. unmount manualy.')
    else:
        setup_mountpoint_done=False
        v(DEV+backupdecryptvol_devname+Q+' is already unmounted.',0)

def unmap():
    if get_crypto_LUKS_volume_devname(encrypted_dev_name)==backupdecryptvol_devname:
        ##dev_name seems ok
        if check_luks_open(encrypted_dev_name):
            close_crypto_LUKS(backupdecryptvol_devname)
            setup_decryptvol_done=False
        else:
            setup_decryptvol_done=False
            raise Exception('backupdecryptvol_devname: '+Q+backupdecryptvol_devname+Q+' is already closed')
        checkisnot(check_luks_open)(dev_name)
        setup_decryptvol_done=False
    else:
        setup_decryptvol_done=False
        raise Exception('get_crypto_LUKS_volume_devname(dev_name)==backupdecryptvol_devname is not equal. not expected')

def do_backup():
    setup_all()
    bashcode1='nice -n19 ionice -c3 sudo btrfs send '+snap
    bashcode2='nice -n19 ionice -c3 sudo btrfs receive '+backupdir
    pipe='|'
    q1='\''
    bashcode=bashcode1+pipe+bashcode2
    shell=['bash','-c',bashcode]
    sp.check_call(shell)

def setup_all():
    if not setup_snapshot_done: setup_snapshot()
    if not setup_decryptvol_done: setup_decryptvol()
    if not setup_mountpoint_done: setup_mountpoint()

def search_for_shared_snapshot_pairs():
    """
    search for shared snapshots, that are needed to do incremental backups.
    return list of pathnames. latest one first.
    """


setup_all()
a=input('do backup? (y/n)')
if a=='y':
    do_backup()
elif a=='n':
    pass
else:
    print('invalid input. exit')
