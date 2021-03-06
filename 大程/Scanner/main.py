from __future__ import annotations
import os, chardet, json

IGNORE_LIST = ["__pycache__", "_distutils_hack", "pip", "pip-20.3.3.dist-info", "pkg_resources", "setuptools",
               "setuptools-51.1.1.dist-info"]


class Module():
    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index
        self.nLines = 0
        self.imports = []
        self.importedBy = []
        self.nConnections = 0

    def equals(self, other: Module):
        return self.name == other.name

    def importsModules(self):
        list = []
        for imported in self.imports:
            list.append({
                "index": imported.index,
                "name": imported.name
            })
        return list

    def importedByModules(self):
        list = []
        for importing in self.importedBy:
            list.append({
                "index": importing.index,
                "name": importing.name
            })
        return list


def main():
    path = input("输入项目目录路径：")
    modules = []
    if not os.path.exists(path):
        print("目录不存在")
        input()
    for root, dirs, files in os.walk(path):
        skip = False
        for ignored in IGNORE_LIST:  # 此模块被忽略
            if ignored in root.split("\\"):
                skip = True
                break
        if skip:
            continue
        for file in files:
            filePath = os.path.join(root, file)
            analyzeFile(filePath, modules)
    for module in modules:  # 填充importedBy列表
        for imported in module.imports:
            imported.importedBy.append(module)
    for module in modules:
        module.nConnections = len(module.imports) + len(module.importedBy)
    jsonDict = toJson(modules)
    with open("modules.json", "w") as file:
        json.dump(jsonDict, file)


def toJson(modules: list) -> dict:
    """
    利用模块列表生成力导图使用的Json文件\n
    :param modules: 模块对象列表
    :return: 适用于力导图的字典
    """
    jsonDict = {}
    jsonDict["links"] = []
    jsonDict["nodes"] = []
    # 添加边
    for module in modules:
        for imported in module.imports:
            jsonDict["links"].append({"source": module.index, "target": imported.index})
    # 添加节点
    for module in modules:
        jsonDict["nodes"].append({
            "index": module.index,
            "name": module.name,
            "nLines": module.nLines,
            "imports": module.importsModules(),
            "importedBy": module.importedByModules(),
            "nConnections": module.nConnections
        })
    return jsonDict


def analyzeFile(path: str, modules: list) -> None:
    """
    分析文件\n
    :param path: 文件路径
    :param modules: 模块对象列表
    :return: 无返回值
    """
    if not ".py" in path:
        return
    if path.find(".py") + 3 != len(path):
        return
    moduleName = path.split("\\")[-1].split(".")[0]
    moduleObj = findModule(moduleName, modules)
    if not moduleObj:
        moduleObj = Module(moduleName, len(modules))
        modules.append(moduleObj)
    try:
        with open(path, encoding=guessEncoding(path)) as file:
            for line in file:
                moduleObj.nLines += 1
                analyzeLine(line, moduleObj, modules)
    except UnicodeDecodeError:  # 字符集猜测失败，直接返回
        return


def analyzeLine(line: str, moduleObj: Module, modules: list) -> None:
    """
    分析行，若存在导入语句，则更新此模块对象的导入列表\n
    :param line: 文件中的一行
    :param moduleObj: 行所属的模块对象
    :param modules: 模块对象列表
    :return: 无返回值
    """
    if not "import" in line:
        return
    if "from" in line:
        startIndex = line.find("from")
        if startIndex != 0:  # "from"不处在开头位置，此行不是导入行
            return
        startIndex += 4
        while line[startIndex] == " ":
            startIndex += 1
        endIndex = startIndex
        while line[endIndex] != " ":
            endIndex += 1  # 左闭右开
        moduleName = line[startIndex:endIndex].split(".")[-1].strip()
        if len(moduleName) > 0:
            appendModule(moduleObj, moduleName, modules)
    else:
        startIndex = line.find("import")
        if startIndex != 0:
            return
        startIndex += 6
        while startIndex < len(line) - 1 and line[startIndex] != "\n":
            while line[startIndex] == " " or line[startIndex] == ",":
                startIndex += 1
            if startIndex + 2 <= len(line) and line[startIndex:startIndex + 2] == "as":  # 跳过"as"和别名，并进入下一循环
                startIndex += 2
                while line[startIndex] == " ":
                    startIndex += 1
                while line[startIndex] != "," and line[startIndex] != " " and line[startIndex] != "\n":
                    startIndex += 1
                continue
            endIndex = startIndex
            while endIndex < len(line) and line[endIndex] != " " and line[endIndex] != "," and line[endIndex] != "\n":
                endIndex += 1
            moduleName = line[startIndex:endIndex].split(".")[-1].strip()
            if len(moduleName) > 0:
                appendModule(moduleObj, moduleName, modules)
            startIndex = endIndex  # 将startIndex调整至下一次循环的起始位置


def appendModule(moduleObj: Module, imported: str, modules: list) -> None:
    """
    将被导入模块对象加入此模块对象的导入列表\n
    :param moduleObj: 导入其他模块的模块对象
    :param imported: 被导入模块模块名
    :param modules: 模块对象列表
    :return: 无返回值
    """
    importedObj = findModule(imported, modules)
    if not importedObj:
        importedObj = Module(imported, len(modules))
        modules.append(importedObj)
    moduleObj.imports.append(importedObj)


def findModule(moduleName: str, modules: list) -> any:
    """
    尝试在modules列表中寻找名为moduleName的模块对象并返回其引用\n
    :param moduleName: 模块名
    :param modules: 模块对象列表
    :return: 若找到名为moduleName的模块则返回其引用，否则返回None
    """
    for module in modules:
        if module.name == moduleName:
            return module
    return None


def guessEncoding(path: str) -> str:
    """
    猜测文件的编码方式\n
    :param path: 文件路径
    :return: 猜测的编码方式
    """
    with open(path, "rb") as file:
        content = file.read()
        encoding = chardet.detect(content)["encoding"]
        return encoding


main()
