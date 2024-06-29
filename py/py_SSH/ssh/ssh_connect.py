#для подключения по SSH
import paramiko, socket
#данные для программы
from data.config import *
from data.modes import *
#необходиммые инструменты
from equipment.tools import *
from equipment.stdin import *

#проверка на наличие необходимых данных для подключения
def check_device(device, nessesaryKeys, clear = False):
    if clear:
        # если устройство не подключилось из-за неправильныз данных то старые данные удаляються
        for key in nessesaryKeys:
            device.pop(key, None)
    if not device.get("type"):
            device["type"] = "default"
    for item in cheak_keys_A_in_B(nessesaryKeys, device):
        while True:
            #ввод новых данных
            r = input(f"Nesessary for {device['name'] if device.get('name') else device['hostname']}: {item[0]} = ")
            if r:
                device[item[0]] = r
                break
                
#получение списка устройств содержаших данные для подключения
def get_list_devices(reconnect = True):
    #подключение из файла(опционально)
    if (dataApp["mode"] & FROM_FILE) and reconnect:
        nessesaryKeys = ["hostname"]
        alarmMess("File has")
        file = open(folder_path + r"\data\devices.txt", 'r', encoding="utf-8")
        texts = file.read().split('\n\n')
        for data in texts:         
            device = dict()
            if take_info_device(device, data.split('\n')):
                listDevices.append(device)
        if listDevices:
            print("Hosts added succesful")
        file.close()
    #ввод данных от пользователя 
    messData = False
    while True:
        r = input('Enter new host(device)?(y/n): ')
        print_line()
        if r == 'y':
            device = dict()
            device["name"] = input("Enter name for host(device): ")
            #чтобы не донимать пользователя данной пометкой
            if not messData:
                print("Enter data for connect with host:(Press CTRL + Z next press Enter to finish for this host)")
                messData = True
            #многострочный ввод
            data = mulinput().split('\n')
            take_info_device(device, data)          
            listDevices.append(device) 
        elif r == 'n':
            break         
    messData = False
    
#обработка данных и заполнение информацией для подключения
def take_info_device(device, data): 
    #битовый флаг для проверки наличие данных для подключения в полученном масиве данных
    hasData = False 
    nessesaryKeys = ["name", "hostname", "type"]
    for line in data:
        if line:
            if not(line[0] == '#' or line[0] == '\n') and '=' in line:
                #если данная строка соддержит информацию для подключения то делим ее по знаку равно
                key = line.split('=')
                #название поля
                nameKey = key[0].strip()
                #значение поля
                valueKey = key[1].strip()
                #проверка из списка псевдонимов
                if listPseudonym.get(nameKey):
                    nameKey = listPseudonym[nameKey]
                #проверка названия среди списка ключей для подключения
                if nameKey in listNameKey:
                    hasData = True
                    if valueKey:
                        device[nameKey] = valueKey
                    else:
                        nessesaryKeys.append(nameKey)
    if hasData:
        #проверка на наличие необходиммых данных
        check_device(device, nessesaryKeys)
    alarmMess(device)
    return hasData
    
#заполнение аргументов для передачи в функцию для подключения
def fill_arg(elem_list):
    dict_value = dict()
    if elem_list.get("username") and elem_list["username"] != '':
        dict_value["username"] = elem_list["username"]
    if elem_list.get("password") and elem_list["password"] != '':
        dict_value["password"] = elem_list["password"]
    if elem_list.get("port") and elem_list["port"] != '':
        dict_value["port"] = elem_list["port"]
    #проверка на наличие публичного ключа(реализовано только для ed25519)
    if elem_list.get("pkey") and elem_list["pkey"] != '':
        while True:
            try:
                dict_value["pkey"] = paramiko.Ed25519Key.from_private_key_file(elem_list["pkey"])
            except FileNotFoundError:
                #если неправильный путь
                print(f"Error with {listDevices[-1]['name']}: not found path: {elem_list['pkey']}")
                elem_list = input("Enter path of pkey: ")
            except paramiko.ssh_exception.PasswordRequiredException:
                #если нужен пароль для ключа
                pkey_password = elem_list["pkey_password"] if elem_list.get("pkey_password") else input(f"Enter password of pkey for {elem_list["name"]}: ")
                dict_value["pkey"] = paramiko.Ed25519Key.from_private_key_file(elem_list["pkey"], password=pkey_password)
                break
            else:
                break
    alarmMess(dict_value)
    return dict_value
    
#подключение устройств
def connect_devices():
    for device in listDevices:
        while True:
            try:
                c_device = paramiko.SSHClient()
                c_device.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                c_device.connect(device["hostname"], **fill_arg(device))
            except paramiko.ssh_exception.AuthenticationException:
                r = input(f"Error Authentication with {device['name']}\n Do you want reconnect(y, n): ")
                if r == 'y':
                    check_device(device, ["username", "password"], clear = True)
                elif r == 'n':
                    break
            except paramiko.ssh_exception.SSHException:                  
                r = input(f"Error Connecting with {device['name']}\n Do you want reconnect(y, n): ")
                if r == 'y':
                    check_device(device, ["port", "pkey"], clear = True)
                elif r == 'n':
                    break
            except (socket.gaierror, TimeoutError):
                r = input(f"Error Connecting with {device['name']}\n Do you want reconnect(y, n): ")
                if r == 'y':
                    check_device(device, ["hostname", "port"], clear = True)
                elif r == 'n':
                    break
            else:
                print(f"{device['name']} connected succesful")
                #костыль во избежания зависания программы на длинных коммандах просящих доп. ввода
                channel = c_device.invoke_shell()
                channel.setblocking(0)
                #сохранения подключение
                connectedDevices.append(({"type": device["type"], "name": device["name"]}, c_device, {"wellcome": '', "channel": channel , "pc": '', "commands": [], "alloutput": ''}))
                break
    #очистка информации для возможности подключения новых устройств не переподключая старых
    listDevices.clear()

#закрытие всех соединений при выхода из программы
def close_ssh():
    for device in connectedDevices:
        alarmMess(f"{device[0]["name"]} close")
        device[1].close()
        del device
    alarmMess("Programm is done")