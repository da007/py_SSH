import xml.etree.ElementTree as ET
import os

file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(file_path)
#получение дерева xml
errorsTree = ET.parse(folder_path + "\\errors.xml")
answersTree = ET.parse(folder_path + "\\answers.xml")
processesTree = ET.parse(folder_path + "\\processes.xml")
errorsRoot = errorsTree.getroot()
answersRoot = answersTree.getroot()
processesRoot = processesTree.getroot()
#получение данных
errors = dict()
answers = dict()
processes = dict()

for device in errorsRoot.findall("device"):
    name = device.get("name")
    listErrors = list()
    for error in device.findall("error"):
        listErrors.append(r'' + error.text)
    errors[name] = listErrors
for device in answersRoot.findall("device"):
    name = device.get("name")
    listAnswers = list()
    for answer in device.findall("answer"):
        listAnswers.append({answer.get("command"):(r'' + answer.text, r'' + answer.get("process"))})
    answers[name] = listAnswers
for device in processesRoot.findall("device"):
    name = device.get("name")
    listProcesses = dict()
    for process in device.findall("process"):
        listProcesses[process.get("name")] = (r'' + process.get("argv"), r'' + process.text)
    processes[name] = listProcesses