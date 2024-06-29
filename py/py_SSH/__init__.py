import sys, os
sys.path.insert(0, os.path.abspath(__file__)[:-11])

#собственные библиотеки
from data.local_command import *
#подключие и отправка команд
from ssh.ssh_connect import *
from ssh.ssh_exchange import *

def init():
    initData()
    get_list_devices()
    connect_devices()
    get_alias()
    do_alias_for_all()