#данные для программы
from data.config import connectedDevices

#вывод подключенных устройств
def lsd():
    return '\n'.join([f"{index}: {device[0]["name"]}" for index, device in enumerate(connectedDevices)])
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