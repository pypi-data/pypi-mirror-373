import argparse
import sys, os
import subprocess


def figure_markdown_to_myst(line):
    caption = line.split('[')[1].split(']')[0]
    path = line.split('(')[1].split(')')[0]
    args = line.split('{')[1].split('}')[0]
    if r"\\%" in args:
        args = args.replace(r"\\%", "%")
    if r"\%" in args:
        args = args.replace(r"\%", "%")
    new_line = f'\n<img src="{path}" {args} />\n\n'
    if caption != "image":
        new_line = f'<figure>{new_line}<figcaption>{caption}</figcaption></figure>\n\n'
    return new_line


def make_title_frame(title):
    new_line = r'\section{'+title+'}\n'
    return new_line


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", help="Latex file name to transform into Markdown. Must end by .tex")
parser.add_argument("-t", "--title", help="Title", default="")
args = parser.parse_args()

filename = args.filename
if '.tex' not in filename:
    sys.exit('File name must end by .tex.')


environment_header = r"""  \newcommand{\frameignoreoption}[1][]{\framebegin}
 \newcommand{\framebegin}[]{}
 \newenvironment{frame}{\frameignoreoption}{+++}
 %\newenvironment{tabular}[2][]{}{}

% \newenvironment{blockgenerique}[1]{

%   \textbf{#1:}
% }{}
 \newenvironment{exemple}{\begin{blockgenerique}{Exemple}}{\end{blockgenerique}}
% \newenvironment{problem}{\begin{blockgenerique}{Problème}}{\end{blockgenerique}}
 \newenvironment{notes}{\begin{blockgenerique}{Notes aux enseignants}}{\end{blockgenerique}}
 \newenvironment{aretenir}{\begin{blockgenerique}{À retenir}}{\end{blockgenerique}}
 \newenvironment{syntaxe}{\begin{blockgenerique}{Syntaxe}}{\end{blockgenerique}}
 \newenvironment{sémantique}{\begin{blockgenerique}{Sémantique}}{\end{blockgenerique}}

% %\newenvironment{exercice}[1][]{\subsubsection{Exercice: #1}}{}
 %\newenvironment{exerciceavance}[1][]{\subsubsection{Exercice $\clubsuit$: #1}}{}
% \newenvironment{block}[1]{\begin{blockgenerique}{#1}}{\end{blockgenerique}}
% \newenvironment{definition}[1][]{\begin{blockgenerique}{Définition: #1}}{\end{blockgenerique}}

% \newcommand{\includenotebook}[1]{\href{#1}{#1}}
 \newcommand{\bigemph}[1]{\textbf{#1}}
% \newcommand{\scalebox}[2]{#2}
 %\newcommand{\input}[1]{#1}
 \newenvironment{bigcenter}{}{}

"""

outfile = filename.replace('.tex', '_tmp.tex')
text_out = ""
title = ""
start_document = False
enum = 0
itemize = False
exo_num = 1
write_table_format_string = 0
ncols = 0
brace_open = 0
brace_close = 0
start_frame = False
start_python = True
start_table = False
skip = False
start_equation = False
start_align = False
with open(filename, 'r') as f:
    for line in f:
        if line[0] == '%' and "<img" not in line:
            continue
        if r'\begin{document' in line:
            start_document = True
            text_out += environment_header
        if 'include_slides' in line:
            continue
        if "pyoutput" in line:
            continue
        if r'\begin{column' in line or r'\end{column' in line:
            continue
        if r'\animategr' in line:
            continue
        if r'\vspace' in line:
            continue
        if r'\frame' in line:
            brace_open = 1
            brace_close = 0
            start_frame = True
            line = line.replace(r'\frame{', r'\begin{frame}')
        if r"\\~\\" in line:
            line = line.replace(r"\\~\\", "")
        #if r"\\" in line:
        #    line = line.replace(r"\\", "")
        if r"section{" in line:
            line = line.replace(r"section{", r"subsection{")
        if "titlepage" in line:
            line = make_title_frame(args.title)
        if r'{centering}' in line or r'{center}' in line:
            continue
        if r'{frame}' not in line:
            brace_open += line.count(r'{')
            brace_close += line.count(r'}')
        if 'width' in line and 'cm' in line:
            size = float(line.split("=")[1].split('cm')[0])
            line = line.replace(f"{size:.0f}cm", f"{int(100*size/15):.0f}\%")
        if 'width=' in line and 'textwidth' in line:
            words = line.split("=")[1].split(r'\textwidth')
            if len(words) > 0 and words[0] != "":
                size = float(words[0])
            else:
                size = 1.0
            line = line.replace(f"{words[0]}"+r"\textwidth", f"{int(100*size):.0f}\%")
        if 'height' in line and 'cm' in line:
            size = float(line.split("=")[1].split('cm')[0])
            line = line.replace("height", "width")
            line = line.replace(f"{size:.0f}cm", f"{int(100*size/10):.0f}\%")
        if r'\begin{lstlisting}' in line:
            if "DOS" not in line:
                line = r'\begin{lstlisting}'+'\n```python'+'\n'
                start_python = True
            else:
                line = line.replace("[style=DOS]", "")
                start_python = False
        if r'\begin{pyin}' in line:
            line = r'\begin{lstlisting}'+'\n```python'+'\n'
            start_python = True
        if r'\end{lstlisting}' in line and start_python:
            line = line.replace(r'\end{lstlisting}', '```\n'+r'\end{lstlisting}')
            start_python = False
        if r'\end{pyin}' in line and start_python:
            line = line.replace(r'\end{pyin}', '```\n'+r'\end{lstlisting}')
            start_python = False
        if r'\begin{pyout}' in line:
            skip = True
            continue
        if r'\begin{pyprint}' in line:
            skip = True
            continue
        if r'\end{pyout}' in line:
            skip = False
            continue
        if r'\end{pyprint}' in line:
            skip = False
            continue
        if skip:
            continue
        if start_frame and brace_open == brace_close:
            brace_open = 0
            brace_close = 0
            start_frame = False
            last_brace_closed = line.rfind(r'}')
            line = line[:last_brace_closed] + r'\end{frame}' + line[last_brace_closed+1:]
        if "$$" in line:
            if start_equation:
                line = line.replace("$$", "\n$$\n")
                start_equation = False
            else:
                line = line.replace("$$", "\n$$\n")
                start_equation = True
        if "<img" in line and "<table>" not in line:
            line = r"\begin{lstlisting}"+"\n"+line[1:]+"\n"+r"\end{lstlisting}"
        if r'\begin{equation}' in line:
            line = line.replace(r'\begin{equation}', '\n$$')
        if r'\end{equation}' in line:
            line = line.replace(r'\end{equation}', '$$\n')
        # use $$\begin{aligned} ... \end{aligned}$$ in .tex instead of the following commands
        # if r'\begin{align*}' in line:
        #     line = line.replace(r'\begin{align*}', '\n$$')
        #     start_align = True
        # if start_align and r"&" in line and not start_table:
        #     line = line.replace(r"&", "")
        # if start_align and r"\\" in line and not start_table:
        #     line = line.replace(r"\\", "\n$$\n\n$$\n")
        # if r'\end{align*}' in line:
        #     line = line.replace(r'\end{align*}', '$$\n')
        #     start_align = False
        if r'\begin{tabular}' in line:
            start_table = True
        if r"& " in line and start_table:
            line = line.replace(r"& ", r"| &")
        if r'\end{tabular}' in line:
            start_table = False
        if ("<table>" in line or "<img" in line) and line[0] == r"%":
            line = line[1:]
        if r"\caption" in line and start_table:
            line = line.replace(r"\caption{", r"\textit{")
            #line = list(line)
            #line[-2] = r"</caption>"
            #line = "".join(line)
        text_out += line
f.close()

f = open(outfile, 'w')
f.write(text_out)
f.close()

print(f"pandoc {outfile} -o {outfile.replace('.tex', '.md')}")
subprocess.run(f"pandoc {outfile} -o {outfile.replace('.tex', '.md')}", shell=True, check=True)


jupyter_header = """---
celltoolbar: Diaporama
rise:
  scroll: true
  enable_chalkboard: true
  width: 90%
  height: 90%
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.7.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
metadata:
  execution:
    allow_errors: true
---
"""
outfile_md = outfile.replace('.tex', '.md')
text_out = ""
title = ""
start_document = False
enum = 0
itemize = False
exo_num = 1
write_table_format_string = 0
ncols = 0
brace_open = 0
brace_close = 0
start_python = False
with open(outfile_md, 'r') as f:
    for iline, line in enumerate(f):
        if iline == 0:
            line = jupyter_header + line
        if r"```python" in line:
            start_python = True
        if start_python:
            l_line = list(line)
            for k in range(4):
                try:
                    l_line.remove(" ")
                except ValueError:
                    pass
            line = ''.join(l_line)
            if r'```' in line and 'python' not in line:
                start_python = False
        if r'```' in line:
            line = line.replace(r'```python', '```{code-cell} ipython3\n---\nslideshow:\n  slide_type: "-"\n'
                                              'codeCellConfig:\n   lineNumbers: true\n'
                                              'tags: [raises-exception]\n'
                                              '---\n')
            #line = line.replace(r'```python', '+++ {"cell_type": "code",  "slideshow":  {"slide_type": "slide"} }\n')
            #if "slide_type" not in line:
            #    line = line.replace(r'```', '\n```\n +++ {"slideshow":  {"slide_type": "subslide"} }\n')
        if r'![image]' in line or (r"![" in line and "plots" in line):
            line = figure_markdown_to_myst(line)
        if r"\llbracket" in line:
            line = line.replace(r"\llbracket", r"[")
        if r"\rrbracket" in line:
            line = line.replace(r"\rrbracket", r"]")
        if line[-4:].rstrip() == "+++":
            line = line.replace("+++", "\n+++")
        if "+++" in line and "slide_type" not in line:
            line = line.replace('+++', r'+++ {"slideshow": {"slide_type": "slide"} }')
        if r"\|" in line:
            line = line.replace(r"\|", r"|")
        if r'\"' in line:
            line = line.replace(r'\"', r'"')
        if r'\<' in line:
            line = line.replace(r'\<', r'<')
        if "----" in line:
            line = line.replace("- ", r"-|")
        if r"<table\>" in line:
            start_table = True
        if '\\' in line and start_table:
            line = line.replace("\\", "")
        if "<img" in line and line[:4] == "    ":
            line = line[4:]
            line = line.replace("\\", "")
        if "</table>" in line:
            start_table = False
        text_out += line
f.close()

f = open(outfile_md, 'w')
f.write(text_out)
f.close()

print(f"jupytext  --to ipynb --execute {outfile_md}")
subprocess.run(f"jupytext  --to ipynb --execute {outfile_md}", shell=True, check=True)
os.rename(outfile_md.replace('.md', '.ipynb'), filename.replace('.tex', '.ipynb'))
subprocess.run(f"rm -rf {filename.split('.')[0]}_tmp*", shell=True, check=True)
#subprocess.run(f"jupytext --set-formats ipynb,md:myst --execute {filename.replace('.tex', '.ipynb')}", shell=True, check=True)
subprocess.run(r'''jupytext --from ipynb --to md:myst  --update-metadata '{"jupytext": {"notebook_metadata_filter":"all"}}' '''
               f'''--execute {filename.replace(".tex", ".ipynb")}''', shell=True, check=True)
