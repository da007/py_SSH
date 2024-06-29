#управление вводом
import msvcrt, time, os
#регулярные выражения
import re
#данные для программы
from data.config import *
from data.modes import *
#необходиммые инструменты
from equipment.tools import *
from equipment.stdin import *
import equipment.process as process
import equipment.XML as XML

#создание списка алиасов из папки commandes
def get_alias():
    items = os.listdir(folder_path + "\\data\\commands\\")
    for item in items:
        file = open(folder_path + "\\data\\commands\\" + item, 'r', encoding="utf-8")
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
#проверка вывода на ошибки
def check_error(device, command, output):    
    dtype = device[0]["type"]
    name = device[0]["name"]
    if XML.errors.get(dtype):
        for error in XML.errors[dtype]:
            if re.findall(error, output):
                if XML.processes[dtype].get(answer[command][1]):
                    if dataApp["mode"] & ASKBEFORE:
                        r = input(f"Incorrect command output. Do you want to process it?(y, n): ")
                        if r == 'n':
                            return False
                    commands = process.set_argv_command(*XML.processes[dtype][answer[command][1]])
                    for command in commands.split('\n'):
                        send_command(device, command)
                    return True
    else:
        for dtype, errors in XML.errors.items():
            for error in errors:
                if re.findall(error, output):
                    if XML.processes[dtype].get(name):
                        if dataApp["mode"] & ASKBEFORE:
                            r = input(f"Incorrect command output. Do you want to process it?(y, n): ")
                            if r == 'n':
                                return False
                        commands = process.set_argv_command(*XML.processes[dtype][name][answer[command][1]])
                        for command in commands.split('\n'):
                            send_command(device, command)
                        return True
                    else:
                        if dataApp["mode"] & ASKBEFORE:
                            r = input(f"Incorrect command output. Do you want to process it?(y, n): ")
                            if r == 'n':
                                return False
                        commands = process.set_argv_command(*XML.processes[dtype][name][answer[command][1]])
                        for command in commands.split('\n'):
                            send_command(device, command)
                        return True
    return False
#проверка на не соответствие вывода
def check_answer(device, command, output):
    dtype = device[0]["type"]
    name = device[0]["name"]
    if XML.answers.get(dtype):
        if XML.answers[dtype].get(name):
            for answer in XML.answers[dtype][name]: 
                if answer.get(command):
                    if not re.findall(answer[command][0], output):
                        alarmMess("not match")
                        if XML.processes[dtype].get(name):
                            if dataApp["mode"] & ASKBEFORE:
                                r = input(f"Incorrect command output. Do you want to process it?(y, n): ")
                                if r == 'n':
                                    return False
                            commands = process.set_argv_command(*XML.processes[dtype][name][answer[command][1]])
                            for command in commands.split('\n'):
                                send_command(device, command)
                            return True
                        else:
                            if dataApp["mode"] & ASKBEFORE:
                                r = input(f"Incorrect command output. Do you want to process it?(y, n): ")
                                if r == 'n':
                                    return False
                            commands = process.set_argv_command(*XML.processes[dtype][name][answer[command][1]])
                            for command in commands.split('\n'):
                                send_command(device, command)
                            return True
        else:
            for answer in XML.answers[device[0]["type"]]["default"]: 
                if answer.get(command):
                    if not re.findall(answer[command][0], output):
                        alarmMess("not match")
                        if XML.processes[dtype].get(name):
                            if dataApp["mode"] & ASKBEFORE:
                                r = input(f"Incorrect command output. Do you want to process it?(y, n): ")
                                if r == 'n':
                                    return False
                            commands = process.set_argv_command(*XML.processes[dtype][name][answer[command][1]])
                            for command in commands.split('\n'):
                                send_command(device, command)
                            return True
                        else:
                            if dataApp["mode"] & ASKBEFORE:
                                r = input(f"Incorrect command output. Do you want to process it?(y, n): ")
                                if r == 'n':
                                    return False
                            commands = process.set_argv_command(*XML.processes[dtype]["default"][answer[command][1]])
                            for command in commands.split('\n'):
                                send_command(device, command)
                            return True
    else:
        for dtype, data in XML.answers.items():
            for answer in XML.answers[device[0]["type"]]["default"]: 
                if answer.get(command):
                    if not re.findall(answer[command][0], output):
                        alarmMess("not match")
                        if XML.processes[dtype]["default"].get(answer[command][1]):
                            if dataApp["mode"] & ASKBEFORE:
                                r = input(f"Incorrect command output. Do you want to process it?(y, n): ")
                                if r == 'n':
                                    return False
                            commands = process.set_argv_command(*XML.processes[dtype]["default"][answer[command][1]])
                            for command in commands.split('\n'):
                                send_command(device, command)
                            return True
    return False
def check_output(device, command, output):
    if dataApp["mode"] & PROCESSING: 
        channel = device[2]["channel"]
        ncommand = command
        isError = False
        isResend = False
        if dataApp["mode"] & OUTPUT:
            print(f'{device[2]["pc"] + ncommand}')
            for line in output.split('\n'):
                print(f'{line}')
        alarmMess("PROCESSING")
        #проверка вывода на ошибки
        isError = check_error()
        #проверка на не соответствие вывода
        isResend = check_answer(device, ncommand, output)
        if isResend :
            send_command(device, command)
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
    device[2]["alloutput"] += output
    output = '\n'.join(output.split('\n')[1:-1])
    device[2]["commands"].append((command, output))
    if (dataApp["mode"] & OUTPUT) and not(dataApp["mode"] & PROCESSING):
        print(f'{device[2]["pc"] + ncommand}')
        for line in output.split('\n'):
            print(f'{line}')
    check_output(device, command, output)
    return output
#отправка алиаса на устройтство(по командно)
def send_alias(device, nameAlias):    
    if dataApp["mode"] & OUTPUT:
        print(device[0]["name"] + ': ')
    if commandAlias.get(nameAlias):
        for command in commandAlias[nameAlias]:
            output = send_command(device, command)    
            if (dataApp["mode"] & OUTPUT) and not (dataApp["mode"] & PROCESSING):
                print(f'{device[2]["pc"] + command}')
                for line in output.split('\n'):
                    print(f'{line}')
#интерактивное подключение к устройству
def connect_shell(device):
    print(f"Connecting with {device[0]["name"]}")
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
    if dataApp["mode"] & DO_FOR_ALL:
        for device in connectedDevices:
            alarmMess(f"{device[0]["name"]} are running alias")
            for nameAlias in commandAlias:
                send_alias(device, nameAlias)