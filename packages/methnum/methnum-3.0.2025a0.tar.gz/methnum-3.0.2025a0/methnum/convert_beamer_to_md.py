import argparse
import sys


### OBSOLETE

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="Latex file name to transform into Markdown. Must end by .tex")
args = parser.parse_args()

filename = args.filename
if '.tex' not in filename:
    sys.exit('File name must end by .tex.')
outfile = filename.replace('.tex', '.md')
text_out = ""
title = ""
start_document = False
enum = 0
itemize = False
exo_num = 1
write_table_format_string = 0
ncols = 0
with open(filename, 'r') as f:
    for line in f:
        if line[0] == '%': continue
        if r'\begin{document' in line:
            start_document = True
            continue
        if 'frame' in line: continue
        if r'\textcolor{black}{\textbf{' in line:
            title = '# ' + (line.split('{')[-1]).replace('}', '').replace(r'\\', '\n')
        if r'\definetitle' in line:
            title = '# ' + (line.split('{')[-1]).replace('}', '').replace(r'\\', '\n')
        if start_document is False: continue
        if 'titlepage' in line or 'writetitle' in line:
            text_out += title
            continue
        # skip lines
        if 'vspace' in line: continue
        if 'column' in line: continue
        if r'\end{document}' in line: continue
        if '{center}' in line: continue
        if 'vfill' in line: continue
        if line == '}\n': continue
        if r'{minipage}' in line: continue
        # transform section headers
        if '\section' in line:
            line = '## ' + line.replace('{', '').replace('}', '').replace('\section', '')
        # transform iterations
        if 'itemize' in line:
            itemize = True
            continue
        if 'enumerate' in line:
            enum = 1
            continue
        if '\item' in line:
            if itemize: line = line.replace('\item', '*')
            if enum:
                line = line.replace('\item', f'{enum}.')
                enum += 1
        # transform font styles
        if '``' in line: line = line.replace('``', '"')
        words = line.split()
        for w in words:
            if r'\dots' in w:
                line = line.replace(r'\dots','...')
            if r'{\bf' in w:
                count = w.count(r'{\bf')
                line = line.replace(r'{\bf ', '**', count).replace('}', '**', count)
            if r'\textbf{' in w:
                count = w.count(r'\textbf{')
                line = line.replace(r'\textbf{', '**', count).replace('}', '**', count)
            if r'\emph{' in w:
                count = w.count(r'\emph{')
                line = line.replace(r'\emph{', '**', count).replace('}', '**', count)
            if r'{\it' in w:
                count = w.count(r'{\it')
                line = line.replace(r'{\it ', '*', count).replace('}', '*', count)
            if r'\textit{' in w:
                count = w.count(r'\textit{')
                line = line.replace(r'\textit{', '*', count).replace('}', '*', count)
        # french accents
        if r"\'e" in line:
            line = line.replace(r"\'e", 'é')
        if r'\`a' in line:
            line = line.replace(r"\`a", 'à')
        if r'\`e' in line:
            line = line.replace(r'\`e', 'è')
        # transform python
        if r'\begin{lstli' in line:
            line = line.replace(r'\begin{lstlisting}', r'```python')
        if r'\end{lstli' in line:
            line = line.replace(r'\end{lstlisting}', r'```')
        if r'\begin{verbati' in line:
            line = line.replace(r'\begin{verbatim}', r'```python')
        if r'\end{verbati' in line:
            line = line.replace(r'\end{verbatim}', r'```')
        if r'\texttt{' in line:
            for w in words:
                if r'\texttt{' in w:
                    count = w.count(r'\texttt{')
                    line = line.replace(r'\texttt{', '`', count).replace('}', '`', count)
        if r'$\sim$' in line:
            line = line.replace(r'$\sim$', '\~')
        if r'$\_$' in line:
            line = line.replace(r'$\_$', '_')
        if r'\_' in line:
            line = line.replace(r'\_', '_')
        if r'\verb!' in line:
            words = line.split(' ')
            for iw, w in enumerate(words):
                if r'\verb!' in w:
                    words[iw] = w.replace(r'\verb!', '```').replace('!', '```')
            line = ' '.join(words)
        if r'\verb?' in line:
            words = line.split(' ')
            for iw, w in enumerate(words):
                if r'\verb?' in w:
                    words[iw] = w.replace(r'\verb?', '```').replace('?', '```')
            line = ' '.join(words)
        # transform equations
        if 'displaymath' in line:
            line = line.replace('displaymath', 'equation')
        #if '$$' in line:
        #    line = line.replace('$$', '\\n\\begin{equation}\\n', 1)
        #    line = line.replace('$$', '\\n\end{equation}\\n')
        #if '$' in line:
        #    for w in words:
        #        if '$' in w:
        #            count = w.count('$')
        #            line = line.replace('$', '', count)
        # url
        if r'\url' in line:
            for w in words:
                if r'\url{' in w:
                    count = w.count(r'\url{')
                    line = line.replace(r'\url{', '', count).replace('}', '', count)
        # plots
        if 'includegraph' in line:
            plot_name = line.rstrip().split('{')[-1].replace('}', '').replace(r'\\', '')
            line = f'<img align="center" src="{plot_name}" width="10%" />\n'
        # exercices
        if r'\begin{Exercise}' in line:
            exo_title = (line.split('title=')[-1]).replace('[', '').replace(']', '').replace('{', '').replace('}', '')
            if "=" in exo_title:
                exo_title = (line.split('title =')[-1]).replace('[', '').replace(']', '').replace('{', '').replace('}', '')
            if r'title' not in line:
                exo_title = ""
            line = f'## Exercice {exo_num}: {exo_title}\n'
            exo_num += 1
        if r'\end{Exercise}' in line: continue
        if r'\ifPRINTANSWER\lstinputlisting' in line:
            sol = (line.split('{')[-1]).replace('}', '').replace(r'\fi', '')
            line = f'\n### BEGIN SOLUTION\n!cat {sol}### END SOLUTION\n'
        # tables
        if r'{table}' in line: continue
        if r'\begin{tabular}' in line:
            line = line.replace(r'\begin{tabular}', '')
            ncols = line.count('c') + line.count('l') + line.count('r')
            if ncols == 0:
                print('Warning undefined number of columns.')
            write_table_format_string = True
            continue
        if ncols:
            if line.rstrip('\n') == r'\hline': continue
            if r'\hline' in line:
                line = line.replace(r'\hline', '')
            if '&' in line:
                line = '|' + line.replace('&', '|').replace(r'\\', '')
                if write_table_format_string:
                    line += '\n' + ("|---" * ncols) + '|\n'
                    write_table_format_string = False
        if r'\end{tabular}' in line:
            write_table_format_string = False
            ncols = 0
            continue
        # new lines
        if r'\\' in line:
            line = line.replace(r'\\', '\n')
        # end of file...
        if 'vos TP' in line:
            line = '### A vos TPs !'
        # clean line
        line = line.replace('\hrulefill\quad', '')
        line = line.replace(r'\hfill', ' ')
        text_out += line

f = open(outfile, 'w')
f.write(text_out)
