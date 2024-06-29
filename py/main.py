import py_SSH as ssh
#подготовка программы
ssh.init()
#пользовательский ввод комманд для программы
while True:
   r = input(">")
   if r == "exit":
      break
   r = [text for text in r.split(' ') if text != '']
   if ssh.localListCommands.get(r[0]):
      try:
         #проверка на наличие локальной команды        
         if len(r) == 1:
            print(ssh.localListCommands[r[0]]())
         elif len(r) >= 2:
            print(ssh.localListCommands[r[0]](*r[1:]))
      except TypeError:
         print("Incorect")
   else:
      print("command not found")
#закрытие подключений
ssh.close_ssh()