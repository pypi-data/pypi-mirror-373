from distutils.dir_util import copy_tree
from pathlib import Path

import pystache


class HumanNumberFormatter:
    @staticmethod
    def format(number):
        magnitude = 0
        while abs(number) >= 1000:
            magnitude += 1
            number /= 1000.0

        # add more suffixes if you need them
        return "%.2f%s" % (number, ["", "K", "M", "G", "T", "P"][magnitude])


class ReportElement:
    def __init__(self, title) -> None:
        self.defaultTemplate = "{{#title}}<h2>{{.}}</h2>{{/title}}\n"
        self.title = title
        self.template = None
        self.templateFile = None
        self.vars = {}

    def getTemplate(self):
        if self.template is not None:
            return self.template

        if self.templateFile is not None:
            with open(Reporter.baseFilePath + self.templateFile, "r") as template:
                self.template = template.read()
        else:
            self.template = self.defaultTemplate

        return self.template

    def getAssetPath(self):
        return Reporter.assetPath + "/"

    def getVarName(self, name):
        return name.replace(" ", "")

    def getValue(self, name):
        return self.vars[self.getVarName(name)]

    def addVar(self, name, value, formatter=""):

        if formatter == "humannumber":
            value = HumanNumberFormatter.format(value)

        name = self.getVarName(name)
        self.vars[name] = value

    def getVars(self):
        vars = self.vars
        vars["title"] = self.title
        return vars

    def getHtml(self):
        self.addVar("assetPath", self.getAssetPath())
        return pystache.render(self.getTemplate(), self.getVars())


class ReportSegment(ReportElement):
    def __init__(self, title) -> None:
        super().__init__(title)
        self.defaultTemplate += "{{#segments}}{{&getHtml}}\n{{/segments}}"

        self.segments = []
        self.addVar("segments", self.segments)

    def getFullAssetPath(self):
        return Reporter.basePath + "/" + self.getAssetPath()

    def addSegment(self, segment):
        self.segments.append(segment)

    def addSegments(self, segments):
        for s in segments:
            self.segments.append(s)

    def addAsset(self, name, extension="svg", bbox_inches="tight", dpi=300):
        from matplotlib import pyplot as plt
        pre = "" if self.title is None else self.title + "-"
        fullName = pre + name + "." + extension
        assetPath = Reporter.assetPath + "/" + fullName
        fullPath = Reporter.basePath + "/" + assetPath
        plt.savefig(fullPath, bbox_inches=bbox_inches, dpi=dpi)
        plt.close()
        self.addVar(name, assetPath)

        return assetPath


class ReportTable(ReportSegment):
    def __init__(self, rows=[], head=[], title="", cssClass="") -> None:
        super().__init__(title)
        self.templateFile = "table.html"
        self.head = head
        self.rows = rows
        self.addVar("rows", self.rows)
        self.addVar("head", self.head)
        self.addVar("cssClass", cssClass)

    def setTable(self, rows, head):
        self.rows = rows
        self.head = head

    def addRow(self, rows):
        self.rows.append(rows)


class ReportDict(ReportElement):
    def __init__(self, dictionary, title="") -> None:
        super().__init__(title)
        self.defaultTemplate += "<dl>{{#dict}}<dt>{{&name}}</dt><dd>{{&value}}</dd>{{/dict}}</dl>"
        dictList = []
        for name in dictionary:
            dictList.append(
                {
                    "name": name,
                    "value": dictionary[name],
                }
            )
        self.addVar("dict", dictList)


class Reporter(ReportSegment):
    baseContentFolder = "./SleePyPhases/assets/reportTemplate"
    baseFilePath = "./SleePyPhases/assets/"
    assetPath = "assets"
    basePath = "."

    def __init__(self, name, title=None, dependencies=[], templateFile="report.html") -> None:
        super().__init__(title)
        self.templateFile = templateFile
        self.name = name
        self.dependencies = dependencies

        if title is None:
            title = name

        self.createFolder()

    def createFolder(self):
        path = self.getFullAssetPath()

        if not Path(path).exists():
            Path(path).mkdir(parents=True, exist_ok=True)

        copy_tree(Reporter.baseContentFolder, Reporter.basePath)

    def getFilePath(self):
        return Reporter.basePath + "/" + self.name + ".html"

    def save(self):
        reportFilePath = self.getFilePath()
        html = self.getHtml()

        with open(reportFilePath, "w+") as reportFile:
            reportFile.write(html)
