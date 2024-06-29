#данные для программы
from data.config import dataApp
from data.modes import CLEAR, LINE, DEBUG

#для очистки терминала(не реализовано)            
def clear_cmd():
    if dataApp["mode"] & CLEAR:
        pass
#дополнительная линия для читаемости вывода(хотел чтобы здесь не просто перевод на новую строку а линия из диффизов)
def print_line():
    if dataApp["mode"] & LINE:
        print()
#для вывода данных для проверки
def alarmMess(text):
    if dataApp["mode"] & DEBUG:
        print(text)
#проверка на наличие ключей первого словаря во втором
def cheak_keys_A_in_B(A, B):
    for key_A in A:
        if key_A not in B:
            yield (key_A, False)

