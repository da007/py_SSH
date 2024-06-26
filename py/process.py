import datetime
com = {'ntime': datetime.datetime.now().strftime}
def replace_pr(text):
    r = text
    for pr in com:
        index = text.find(pr)
        if index != -1:
            r = com[pr](text[index + len(pr) + 1:-1])
    return r
def fill_data(args, command):
    for name in args:
        ncommand = command.replace(name, args[name])
    return ncommand
def set_argv_command(data, command):
    data = data.split(';')
    args = dict()
    for field in data:
        arg = field.split('=')
        name = arg[0].strip()
        value = replace_pr(arg[1].strip())
        args[name] = value
    return fill_data(args, command)