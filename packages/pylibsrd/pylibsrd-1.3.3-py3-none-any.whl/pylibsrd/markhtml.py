import os
import re
from pylibsrd import HtmlBuilder
import argparse


class Markdown:
    MultiLineTokens = ["checklist", "ul_item", "ol_item", "blockquote", "table", "paragraph"]

    def __init__(self, path, imageFolderPath=None, stylePath=None):
        self.imageFolderPath = imageFolderPath
        self.stylePath = stylePath
        self.path = path
        self.FileName_NoExt = os.path.splitext(os.path.basename(self.path))[0]

        self.createTableOfContents = False
        self.Headings = [] # (level, text, id)

        with open(path, "r") as f:
            self.mdlines = f.readlines()

    def GetHtml(self, createTableOfContents=False):
        self.createTableOfContents = createTableOfContents
        tokens = self.Tokenise()
        preprocessedHtml = self.HtmlFromTokens(tokens)
        regexHtml = self.convert_inline_formatting(preprocessedHtml)
        return regexHtml
    
    def Tokenise(self):
        tokens = []

        for line in self.mdlines:
            line = line.removesuffix("\n")

            if line.startswith("- [ ] ") or line.startswith("* [ ] "):  # Unchecked checklist
                tokens.append(("checklist", False, line[6:].strip()))

            elif line.startswith("- [x] ") or line.startswith("* [x] "):  # Checked checklist
                tokens.append(("checklist", True, line[6:].strip()))

            elif line.startswith("- ") or line.startswith("* "):  # Unordered List
                tokens.append(("ul_item", line[2:]))

            elif len(line) > 2 and line[0].isdigit() and line[1] == ".":  # Ordered List
                tokens.append(("ol_item", line[2:])) # Wont fail if string is only 2 long, due to slicing behaviour.

            elif line.startswith("> "):  # Blockquote
                tokens.append(("blockquote", line[2:]))

            elif line.startswith("|"): # Table row
                tokens.append(("table", line))

            elif line.startswith("#"):  # heading
                level = len(line.split(" ")[0])
                text = line[level:].strip()
                headingId = text.replace(" ", "_")
                
                # Make the heading id unique
                i = 0
                if headingId in [x[2] for x in self.Headings]:
                    i = 1
                    while headingId + str(i) in self.Headings:
                        i += 1

                if i != 0:
                    headingId += str(i)

                self.Headings.append((level, text, headingId))
                tokens.append(("heading", level, text, headingId))

            else:  # Everything else is a paragraph
                tokens.append(("paragraph", line))

            # Handle Linebreak
            if line.endswith("  "):
                tokens.append("linebreak")

        return tokens

    def HtmlFromTokens(self, tokens):
        html = HtmlBuilder(self.FileName_NoExt)
        html.initaliseHtml(self.stylePath)
        html.ImportMathJax()

        # Title bar
        html.startDiv(id="__container__")
        html.appendRawText(f"\n<h1>{self.FileName_NoExt}</h1>\n")
    
        if self.createTableOfContents:
            # Add a button to show and hide the TOC
            html.appendRawText('<div onclick="toc_click()" id="__toc_button__" class="w3-block w3-button" style="background-color: #444; color:white; font-weight: bold;">Table of Contents</div>')
            
            # Add the TOC
            html.appendRawText(self.GenerateTableOfContents())

            # Add the script to control the visibility
            html.appendRawText("""<script>
function toc_click() {
    var x = document.getElementById('__toc__');
    if (x.classList.contains("w3-hide")) {
        x.classList.remove("w3-hide");
    }
    else {
        x.classList.add("w3-hide");
    }
}
</script>\n""")
            
        tokens = self.JoinMultilineTokens(tokens)

        for token in tokens:
            if token[0] == "heading":
                html.Heading(token[2], token[1], id=token[3])

            elif token[0] == "paragraph":
                p = ""
                pTokens = token[1]
                for pToken in pTokens:
                    p += str(pToken[1]).strip() + " "

                html.p(p)
            
            elif token[0] == "linebreak":
                html.br()

            elif token[0] == "ul_item":
                items = []
                ulTokens = token[1]
                for ulToken in ulTokens:
                    items.append(ulToken[1])

                html.ul(items)

            elif token[0] == "checklist": # Im just going to convert a checklist to a ul
                items = []
                ulTokens = token[1]
                for ulToken in ulTokens:
                    items.append(ulToken[2])

                html.ul(items)

            elif token[0] == "ol_item":
                items = []
                olTokens = token[1]
                for olToken in olTokens:
                    items.append(olToken[1])

                html.ol(items)

            elif token[0] == "blockquote":
                quote = ""
                bqTokens = token[1]
                for bqToken in bqTokens:
                    quote += bqToken[1]

                html.blockquote(quote)

            elif token[0] == "table":
                table = []

                tabTokens = token[1]
                for tabToken in tabTokens:
                    table.append(tabToken[1])

                headers = [h.strip() for h in table[0].split("|")[1:-1]]
                alignments = ["l"] * len(headers)  # Default left-align

                data = []
                for row in table[2:]:  # Skip header and separator row
                    data.append([cell.strip() for cell in row.split("|")[1:-1]])

                html.table(headers, alignments, data, Class="centre")
        
        html.endDiv()
        return html.GetHtml()
    
    @staticmethod
    def JoinMultilineTokens(tokens):
        newTokenList = []
        buffer = []

        for token in tokens:
            # Case 1: empty buffer, single line token
            if len(buffer) == 0 and token[0] not in Markdown.MultiLineTokens:
                newTokenList.append(token)

            # Case 2: not empty buffer, single line token
            elif len(buffer) > 0 and token[0] not in Markdown.MultiLineTokens:
                newTokenList.append((buffer[0][0], buffer.copy()))
                buffer.clear()
                
                newTokenList.append(token)

            # Case 3: not empty buffer, new multiline token
            elif len(buffer) > 0 and token[0] != buffer[0][0] and token[0] in Markdown.MultiLineTokens:
                newTokenList.append((buffer[0][0], buffer.copy()))
                buffer.clear()

                buffer.append(token)

            # Case 4: empty buffer or same token
            else: 
                buffer.append(token)

        if len(buffer) > 0: # Make sure the buffer does not get forgotten if the last element is a multiline.
            newTokenList.append((buffer[0][0], buffer.copy()))

        return newTokenList

    def convert_inline_formatting(self, text):
        text = self.HandleLinksAndImages(text)

        # Handle Double-Dollar Maths FIRST
        text, MathsBlocks = self.HandleBlockMaths(text)
        text, InlineMaths = self.HandleInlineMaths(text)        
        text = self.HandleBoldAndItallic(text)

        text = self.restoreBlockMaths(text, MathsBlocks)
        text = self.restoreInlineMaths(text, InlineMaths)
        text = self.HandleCodeBlocks(text)

        return text
    def HandleCodeBlocks(self, text):
        return re.sub(r"```(.*?)```", r"<pre><code>\1</code></pre>", text, flags=re.DOTALL)
    def HandleBlockMaths(self, text):
        MathsBlocks = []

        def replacement_block(match:re.Match):
            MathsBlocks.append(match.group(0))
            return f"((==MATHS_BLOCK_{len(MathsBlocks)-1}==))"
        
        text = re.sub(r"\$\$(.*?)\$\$", replacement_block, text, flags=re.DOTALL)
        return text, MathsBlocks
    def HandleInlineMaths(self, text):
        InlineMaths = []

        def replacement_block(match:re.Match):
            InlineMaths.append(match.group(0))
            return f"((==INLINE_MATHS_{len(InlineMaths)-1}==))"
        
        text = re.sub(r"(?<!\$)\$(.*?)(?<!\\)\$", replacement_block, text)
        return text, InlineMaths
        # text = re.sub(r"(?<!\$)\$(.*?)(?<!\$)\$", r"\\(\1\\)", text)
    def HandleBoldAndItallic(self, text):
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)

        return text
    def HandleLinksAndImages(self, text):
        text = re.sub(r"!\[\[(.*?)\]\]", rf'<br><img src="{self.imageFolderPath}\1" alt="\1"/><br>', text)
        text = re.sub(r"(?<!\!)\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)

        return text
    def restoreBlockMaths(self, text:str, MathsBlocks):
        for i in range(len(MathsBlocks)):
            maths = fr"\[{MathsBlocks[i][2:-2].strip()}\]"
            text = text.replace(f"((==MATHS_BLOCK_{i}==))", maths)

        return text
    def restoreInlineMaths(self, text, InlineMaths):
        for i in range(len(InlineMaths)):
            maths = fr"\({InlineMaths[i][1:-1].strip()}\)"
            text = text.replace(f"((==INLINE_MATHS_{i}==))", maths)

        return text

    def GenerateTableOfContents(self):
        # Personally I really like this code - 14/05/2025
        html = []
        stack  = [0]

        for level, text, id in self.Headings:
            if level > 3:
                continue

            # Close lists if we're going up
            while stack[-1] != 0 and stack[-1] > level:
                html.append('</ol>') 
                stack.pop()

            # Open new <ul> if going deeper
            initalLevel = stack[-1]
            for i in range(level-stack[-1]):
                level = initalLevel + (i+1)

                html.append(f'<ol class="__toc_ol__ __lvl_{level}__">')
                stack.append(level)

            html.append(f'<li class="__toc_li__ __lvl_{level}__"><a class="__toc__a__ __lvl_{level}__" href="#{id}">{text}</a></li>')

        while stack[-1] != 0:
            html.append("</ol>")
            stack.pop()

        return f'<div id="__toc__" class="w3-hide w3-animate-top w3-container">\n{"\n".join(html)}\n</div>'


def _script():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="The filepath to the markdown file you would like to parse to HTML")
    parser.add_argument("-s", "--style_path", help="Specify a path to a css stylesheet to be included in the header. (If using -a, path should be from there)")
    parser.add_argument("-i", "--image_folder", help="Specify the path to a folder where images are stored")
    parser.add_argument("-t", "--table_of_contents", action="store_true", help="Create a table of contents above the begininning of the document.")
    args = parser.parse_args()

    md = None
    if args.style_path and args.image_folder:
        md = Markdown(args.file_path, args.image_folder, args.style_path)
    elif args.image_folder:
        md = Markdown(args.file_path, args.image_folder)
    elif args.style_path:
        md = Markdown(args.file_path, None, args.style_path)
    else:
        md = Markdown(args.file_path)

    if type(md) == Markdown:
        html = md.GetHtml(args.table_of_contents)
        with open(os.path.splitext(args.file_path)[0]+'.html', "w+") as f:
            f.write(html)
    else:
        print("An error has occured.")
