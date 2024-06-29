import xml.etree.ElementTree as ET
from pathlib import Path
folder_path = str(Path(__file__).parent.parent.parent)

#получение дерева xml
errorsTree = ET.parse(folder_path + r"\data\errors.xml")
answersTree = ET.parse(folder_path + r"\data\answers.xml")
processesTree = ET.parse(folder_path + r"\data\processes.xml")
errorsRoot = errorsTree.getroot()
answersRoot = answersTree.getroot()
processesRoot = processesTree.getroot()
#получение данных
errors = dict()
answers = dict()
processes = dict()
 
for device in errorsRoot.findall("device"):
    type = device.get("type")
    listErrors = dict()
    for name in device:
        listErrors[name.tag] = []
        for error in device.findall("error"):
            listErrors[name.tag].append({"error": r'' + error.text, "command": error.get("command"), "process": error.get("process")})
    errors[type] = listErrors
for device in answersRoot.findall("device"):
    type = device.get("type")
    listAnswers = dict()
    for name in device:
        listAnswers[name.tag] = []
        for answer in name.findall("answer"):
            listAnswers[name.tag].append({answer.get("command"):(r'' + answer.text, r'' + answer.get("process"))})
    answers[type] = listAnswers
for device in processesRoot.findall("device"):
    type = device.get("type")
    listProcesses = dict()
    for name in device:
        listProcesses[name.tag] = {}
        for process in device.findall("process"):
            listProcesses[process.get("type")] = (r'' + process.get("argv"), r'' + process.text)
    processes[type] = listProcesses