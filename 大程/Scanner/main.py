from __future__ import annotations
import os, chardet

IGNORE_LIST = ["__pycache__", "_distutils_hack", "pip", "pip-20.3.3.dist-info", "pkg_resources", "setuptools",
               "setuptools-51.1.1.dist-info"]


class Module():
    def __init__(self, name: str):
        self.name = name
        self.nLines = 0
        self.imports = []

    def equals(self, other: Module):
        return self.name == other.name


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
    return


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
        moduleObj = Module(moduleName)
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
        importedObj = Module(imported)
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
    with open(path, "rb") as file:
        content = file.read()
        encoding = chardet.detect(content)["encoding"]
        return encoding


main()
