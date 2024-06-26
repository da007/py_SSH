#своя библиотека многострочного ввода для пользователя
from stdin import *
#своя обработка xml файлов
import XML
import process
#для подключения по SSH
import paramiko
import socket
#для получения путей к файлам программы
import os
import sys
import msvcrt
#для управления программой
import time
import modes
# регулярные выражения
import re

#пути к фйлам программы
file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(file_path)
#необходимые ключи и псевдонимы для них
listNameKey = ["name", "hostname", "username", "password", "port", "pkey", "pkey_password"]
listPseudonym = {'n': "name", 'h': "hostname", 'u': "username", 'pw': "password", 'prt': "port", 'pk': "pkey", 'pkp': "pkey_password"}
#внутриние данные
listDevices = list()
connectedDevices = list()
commandAlias = dict()
messData = False
dataApp = dict()
#настройка программы
def init():
    file = open(folder_path + "\\setting", 'r', encoding="utf-8")
    for line in file.readlines():
        if line:
            if not(line[0] == '#' or line[0] == '\n') and '=' in line:
                key = line.split('=')
                name = key[0].strip()
                value = key[1].strip()
                if value.startswith("0b"):
                    value = int(value, 2)
                elif '.' in value:
                    value = float(value)
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        value = r'' + value
                dataApp[name] = value
#команды для программы
#вывод подключенных устройств
def lsd():
    return '\n'.join([f"{index}: {device[0]}" for index, device in enumerate(connectedDevices)])
#получить вывод последней комманды
def gbfr(i):
    i = int(i)
    return connectedDevices[i][2]["commands"][-1][1] if i < len(connectedDevices) else "not device"
#подключиться к оболочке устройства(в разработке)
def cnct(i):
    i = int(i)
    if i < len(connectedDevices):
        connect_shell(connectedDevices[i])
        return "Disconnect shell"
    else:
        return "not device"
#отправить команду
def send(i, command):
    i = int(i)
    if i < len(connectedDevices):
        return send_command(connectedDevices[i], command)        
    else:
        return "not device"
#добавить устройство
def add():
    get_list_devices(False)
    return ''
#подключить новые устройства
def nwcn():
    connect_devices()
    return ''
#завершить сессию с выбранным устройством
def cls(i):
    return connectedDevices.pop(int(i), "not device")[1].close()
#список алиасов(из папки commandes)
def lsalias():
    return '\n'.join([f"{i}: {name}:\n{'\n'.join([f'   {command}' for command in commands])}" for i, (name, commands) in enumerate(commandAlias.items())])
#выполнить алиас для устройства
def aliasfor(i, nameAlias):
    i = int(i)
    if i < len(connectedDevices) and nameAlias in commandAlias:
        send_alias(connectedDevices[i], nameAlias)
        return "Ok"
    else:
        return "not device"
#перечень команд. Доступ к устройству через его индекс
localListCommands = {"lsd": lsd,            #вывод подключенных устройств
                     "gbfr": gbfr,          #получить вывод последней комманды
                     "cnct": cnct,          #подключиться к оболочке устройства(в разработке)
                     "send": send,          #отправить команду
                     "add": add,            #добавить устройство
                     "nwcn": nwcn,          #подключить новые устройства
                     "cls": cls,            #завершить сессию с выбранным устройством
                     "lsalias": lsalias,    #список алиасов(из папки commandes)
                     "aliasfor": aliasfor}  #выполнить алиас для устройства
#для очистки терминала(не реализовано)            
def clear_cmd():
    if dataApp["mode"] & modes.CLEAR:
        os.system('cls')
#дополнительная линия для читаемости вывода(хотел чтобы здесь не просто перевод на новую строку а линия из диффизов)
def print_line():
    if dataApp["mode"] & modes.LINE:
        print()
#для вывода данных для проверки
def alarmMess(text):
    if dataApp["mode"] & modes.DEBUG:
        print(text)
#проверка на наличие ключей первого словаря во втором
def cheak_keys_A_in_B(A, B):
    for key_A in A:
        if key_A not in B:
            yield (key_A, False)
#проверка на наличие необходимых данных для подключения
def check_device(device, nessesaryKeys, clear = False):
    if clear:
        # если устройство не подключилось из-за неправильныз данных то старые данные удаляються
        for key in nessesaryKeys:
            device.pop(key, None)
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
    if (dataApp["mode"] & modes.FROM_FILE) and reconnect:
        nessesaryKeys = ["hostname"]
        alarmMess("File has")
        file = open(folder_path + "\\devices.txt", 'r', encoding="utf-8")
        texts = file.read().split('\n\n')
        for data in texts:         
            device = dict()
            if take_info_device(device, data.split('\n')):
                listDevices.append(device)
        if listDevices:
            print("Hosts added succesful")
        file.close()
    #ввод данных от пользователя      
    while True:
        r = input('Enter new host(device)?(y/n): ')
        print_line()
        if r == 'y':
            global messData
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
    nessesaryKeys = ["name", "hostname"]
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
                connectedDevices.append((device["name"], c_device, {"wellcome": '', "channel": channel , "pc": '', "commands": [], "alloutput": ''}))
                break
    #очистка информации для возможности подключения новых устройств не переподключая старых
    listDevices.clear()
#создание списка алиасов из папки commandes
def get_alias():
    items = os.listdir(folder_path + "\\commands")
    for item in items:
        file = open(folder_path + "\\commands\\" + item, 'r', encoding="utf-8")
        commandAlias["".join(item.split('.')[:-1])] = [command.replace('\n', '') for command in file]
        file.close()
    alarmMess(commandAlias)
#отправка команды и получение ответа(своя реализация может глючить при долгом ожидании ответа от сервера)
def c_get(channel, command = ''):
    output = ''
    if command:
        channel.send(command + '\n')
        channel.send_ready()
    while True:
        try :
            time.sleep(2*dataApp["timeout"])
            r = channel.recv(dataApp["lenghtTextRecive"]).decode("utf-8")
            if r:
                output += r
        except (paramiko.buffered_pipe.PipeTimeout, TimeoutError):
            return output 
#проверка вывода
def check_output(device, command, output):
    if dataApp["mode"] & modes.PROCESSING: 
        channel = device[2]["channel"]
        ncommand = command
        isError = False
        isAnswerIncorrect = False
        isResend = False
        if dataApp["mode"] & modes.OUTPUT:
            print(f'{device[2]["pc"] + ncommand}')
            for line in output.split('\n'):
                print(f'{line}')
        while True:
            alarmMess("PROCESSING")
            #проверка вывода на ошибки
            for i, (name, errors) in enumerate(XML.errors.items()):
                for error in errors:
                    if re.findall(error, output):
                        if dataApp["mode"] & modes.OUTPUT:
                            print(f'{device[2]["pc"] + ncommand}')
                            for line in output.split('\n'):
                                print(f'{line}')
                        isError = True
                        break
                if isError:
                    break
            #проверка на не соответствие вывода
            for i, (name, answers) in enumerate(XML.answers.items()):
                for answer in answers:
                    if answer.get(ncommand):
                        if not re.findall(answer[ncommand][0], output):
                            alarmMess("not match")
                            if XML.processes[name].get(answer[command][1]):
                                isAnswerIncorrect = True
                                isResend = True
                                ncommands = process.set_argv_command(*XML.processes[name][answer[command][1]])
                                for ncommand in ncommands.split('\n'):
                                    send_command(device, ncommand)
                                break
                isAnswerIncorrect = False
            if isError:
                break
            if isResend and not isAnswerIncorrect:
                output = c_get(channel, command)
                break
            if not isAnswerIncorrect:
                break
#отправка команды с их первичной обработкой(использует c_get выше)
def send_command(device, command):
    channel = device[2]["channel"]
    if not device[2]["pc"]:
        r = c_get(channel)
        device[2]["alloutput"] += r
        r = r.split('\r\n')
        device[2]["wellcome"] = '\n'.join(r[:-1])
        device[2]["pc"] = r[-1]
    output = c_get(channel, command)
    #запускаеться только если есть определеный флаг
    device[2]["alloutput"] += output
    output = '\n'.join(output.split('\n')[1:-1])
    device[2]["commands"].append((command, output))
    if (dataApp["mode"] & modes.OUTPUT) and (dataApp["mode"] & modes.PROCESSING):
        print(f'{device[2]["pc"] + ncommand}')
        for line in output.split('\n'):
            print(f'{line}')
    check_output(device, command, output)
    return output
#отправка алиаса на устройтство(по командно)
def send_alias(device, nameAlias):    
    if dataApp["mode"] & modes.OUTPUT:
        print(device[0] + ': ')
    if commandAlias.get(nameAlias):
        for command in commandAlias[nameAlias]:
            output = send_command(device, command)    
            if (dataApp["mode"] & modes.OUTPUT) and not (dataApp["mode"] & modes.PROCESSING):
                print(f'{device[2]["pc"] + command}')
                for line in output.split('\n'):
                    print(f'{line}')
#интерактивное подключение к устройству
def connect_shell(device):
    print(f"Connecting with {device[0]}")
    alarmMess(device[2])
    channel = device[2]["channel"]
    pc = device[2]["pc"]
    pre= dataApp["prefixCommand"]
    print(device[2]["alloutput"], end = '')
    channel.send('')
    commands = [['','']]
    command = ''        
    output = ''
    r = ''
    while True:
        ch = ''
        if msvcrt.kbhit():
            try:
                ch = msvcrt.getch().decode()
                if ch in ['\r']:
                    ch += '\n'
                    if text.startswith(pre):
                        if command[len(pre):] == 'ex':
                            break                        
                        channel.send("\x08"*len(command))
                        send_alias(device, command[len(pre):])
                        ch = ''
                        command = ''
                    else:
                        commands[-1][0] = command
                        command = ''
                elif ch == "\x08":
                    if command:
                        command = command[:-1]
                else:
                    if not commands[-1][0]:
                        command += ch
            except UnicodeDecodeError:
                pass
        try:
            if ch:
                channel.send(ch)
            time.sleep(dataApp["timeout"]/7)
            r = channel.recv(dataApp["lenghtTextRecive"]).decode()
        except (paramiko.buffered_pipe.PipeTimeout, TimeoutError):
            pass
        finally: 
            if r:
                output += r
                if commands[-1][0]:
                    if pc not in r:
                        commands[-1][0] += r
                    else:
                        commands[-1][0] += r[:r.find(pc)]
                        commands.append(['',''])
                while True:
                    matches = re.finditer(r"\x1B\[\d{1,3}D", r)
                    try:
                        m = next(matches)
                    except StopIteration:
                        break
                    else:
                        try:
                            num = int(m.group()[2:-1])
                            r = r[:m.start()] + '\b'*num + r[m.end():]
                        except TypeError:
                            pass
                print(r, end = '', flush=True)
                r = ''
    device[2]["alloutput"] += output
    for data in commands:
        device[2]["commands"].append((data[0], data[1]))
#выполнение алиасов для всех
def do_alias_for_all():
    if dataApp["mode"] & modes.DO_FOR_ALL:
        for device in connectedDevices:
            alarmMess(f"{device[0]} are running alias")
            for nameAlias in commandAlias:
                send_alias(device, nameAlias)
#закрытие всех соединений при выхода из программы
def close_ssh():
    for device in connectedDevices:
        alarmMess(f"{device[0]} close")
        device[1].close()
        del device
    alarmMess("Programm is done")