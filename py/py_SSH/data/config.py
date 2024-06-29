from pathlib import Path
#пути к фйлам программы
folder_path = str(Path(__file__).parent.parent.parent)
#необходимые ключи и псевдонимы для них
listNameKey = ["name", "type", "hostname", "username", "password", "port", "pkey", "pkey_password"]
listPseudonym = {'t': "type",'n': "name", 'h': "hostname", 'u': "username", 'pw': "password", 'prt': "port", 'pk': "pkey", 'pkp': "pkey_password"}
#внутриние данные
listDevices = list()
connectedDevices = list()
commandAlias = dict()
dataApp = dict()

#настройка программы
def initData():
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