class HtmlBuilder:
    def __init__(self, DocumentTitle):
        self.htmlDocument = []
        self.DocumentTitle = DocumentTitle

    def initaliseHtml(self, styleFilePath=None, useW3StyleSheet=True):
        self.htmlDocument.append('<!DOCTYPE html>\n<html>\n\t<head>\n\t<meta charset="UTF-8">\n\t<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        self.htmlDocument.append(f"\t<title>{self.DocumentTitle}</title>")

        if useW3StyleSheet:
            self.htmlDocument.append('\t<link rel="stylesheet" href="https://www.w3schools.com/lib/w3.css">')

        if styleFilePath != None:
            self.htmlDocument.append(f'\t<link rel="stylesheet" type="text/css" href="{styleFilePath}" title="DevEng Style"/>')

        self.htmlDocument.append("\t</head>")
        self.htmlDocument.append("<body>")
    
    def ImportMathJax(self):
        importScript = '<script type="text/javascript" id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>'
        settingsScript = """\nwindow.MathJax = {
    loader: {
        load: ['[tex]/physics', '[tex]/color']
    },
    tex: {
        packages: {
            '[+]': ['physics', 'color']
        }
    }
};\n"""
        
        self.script(settingsScript)
        self.appendRawText(importScript)

    def appendRawText(self, text):
        self.htmlDocument.append(text)

    def comment(self, text):
        self.htmlDocument.append(f"<!--{text}-->")

    @staticmethod
    def convKwargs(**kwargs):
        html = ""
        for key, value in kwargs.items():
            html += f" {key}=\"{value}\""
        return html

    def Heading(self, text, level, **kwargs):
        html = f"<h{level}{self.convKwargs(**kwargs)}>{text}</h{level}>"
        self.htmlDocument.append(html)

    def p(self, text, **kwargs):
        html = f"<p{self.convKwargs(**kwargs)}>{text}</p>"
        self.htmlDocument.append(html)
    
    def hr(self):
        self.htmlDocument.append("<hr>")

    def br(self):
        self.htmlDocument.append("<br>")

    def ul(self, items, **kwargs):
        html = f"<ul{self.convKwargs(**kwargs)}>"
        for item in items:
            html += f"\n<li>{item}</li>"
        html += "</ul>"
        self.htmlDocument.append(html)

    def ol(self, items, **kwargs):
        html = f"<ol{self.convKwargs(**kwargs)}>"
        for item in items:
            html += f"\n<li>{item}</li>"
        html += "</ol>"
        self.htmlDocument.append(html)

    def image(self, src, **kwargs):
        html = f"<img{self.convKwargs(**kwargs)} src=\"{src}\"/>"
        self.htmlDocument.append(html)

    def startDiv(self, **kwargs):
        self.htmlDocument.append(f"<div{self.convKwargs(**kwargs)}>")

    def endDiv(self):
        self.htmlDocument.append("</div>")

    def script(self, text="", **kwargs):
        self.htmlDocument.append(f"<script{self.convKwargs(**kwargs)}>{text}</script>")
    
    def blockquote(self, text, **kwargs):
        self.htmlDocument.append(f"<blockquote{self.convKwargs(**kwargs)}>{text}</blockquote>")

    @staticmethod
    def link(text, **kwargs):
        return (f"<a{HtmlBuilder.convKwargs(**kwargs)}>{text}</a>")

    @staticmethod
    def it(text, **kwargs):
        return (f"<it{HtmlBuilder.convKwargs(**kwargs)}>{text}</it>")

    @staticmethod
    def b(text, **kwargs):
        return (f"<b{HtmlBuilder.convKwargs(**kwargs)}>{text}</b>")

    @staticmethod
    def sub(text, **kwargs):
        return (f"<sub{HtmlBuilder.convKwargs(**kwargs)}>{text}</sub>")

    @staticmethod
    def sup(text, **kwargs):
        return (f"<sup{HtmlBuilder.convKwargs(**kwargs)}>{text}</sup>")

    @staticmethod
    def small(text, **kwargs):
        return (f"<small{HtmlBuilder.convKwargs(**kwargs)}>{text}</small>")

    def table(self, ColHeaders, ColAlignments, TableData, **kwargs):
        self._fixColAlignmets(ColAlignments, len(ColHeaders))

        html = f"<table{self.convKwargs(**kwargs)}><thead><tr>"
        for i in range(len(ColHeaders)):
            html += f"<th style=\"text-align:{ColAlignments[i]}\">{ColHeaders[i]}</th>"
        html += "</tr></thead><tbody>"

        for i in range(len(TableData)):
            html += "<tr>"
            for j in range(len(TableData[i])):
                html += f"<td style=\"text-align:{ColAlignments[j]}\">{TableData[i][j]}</td>"
            html += "</tr>"
        html += "</tr></body></table>"

        self.htmlDocument.append(html)

    @staticmethod
    def _fixColAlignmets(ColAlignments, numberOfCols):
        for i in range(numberOfCols):
            if len(ColAlignments) > i:
                if ColAlignments[i] == "l":
                    ColAlignments[i] = "left"
                elif ColAlignments[i] == "r":
                    ColAlignments[i] = "right"
                elif ColAlignments[i] == "c":
                    ColAlignments[i] = "center"
            else:
                ColAlignments.append("inital")

    def __str__(self):
        return self.GetHtml()

    def GetHtml(self):
        copy = self.htmlDocument.copy()
        copy.append("</body>\n</html>")
        return "\n".join(copy)

    def WriteHtml(self, path):
        with open(path, "w+") as f:
            f.write(self.GetHtml())
