import inspect
import re

import textom.textom

def generate_latex_doc(module, output_file="library_functions.tex", filter_keyword=""):
    """
    Generates a LaTeX document listing all functions of a library with their docstrings.

    Parameters:
    module (module): The library module to inspect.
    output_file (str): The name of the output LaTeX file.
    filter_keyword (str): Include only functions with names containing this keyword.
    """
    # Extract the source code of the module
    source_code = inspect.getsource(module)

    # Use regex to match function definitions in the source code
    functions = re.findall(r"def (\w+)\(", source_code)

    with open(output_file, "w") as f:
        # Write the LaTeX preamble
        f.write(r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor} % For custom colors
\usepackage{sectsty} % For customizing section fonts
% \subsectionfont{\raggedright} % Allow line breaks and ragged right alignment             
\usepackage{geometry}
% \geometry{margin=1in}
\usepackage{graphicx}
                
\title{TexTOM - Manual}
\author{Moritz Frewein, Moritz Stammer, Marc Allain, Tilman Grünewald}
\begin{document}
\maketitle
\label{toc}
\tableofcontents

% Define a custom style for docstrings
\lstdefinelanguage{docstring}{
    basicstyle=\ttfamily\small, % Monospaced font
    backgroundcolor=\color[HTML]{F5F5F5}, % Light gray background
    frame=single, % Border around the docstring
    rulecolor=\color[HTML]{D6D6D6}, % Border color
    keywordstyle=\color{blue}, % Optional: color for keywords
    breaklines=true, % Wrap long lines
}
                
\subsectionfont{\large\ttfamily\raggedright}

\include{introduction}
\section{Functions}\label{sec:functions}
""")
        
        # f.write("\\section*{Module: " + module.__name__.replace("_", r"\_") + "}\n\n")

        # Loop through functions in the order they appear in the source code
        for name in functions:
            if hasattr(module, name):
                obj = getattr(module, name)
                if inspect.isfunction(obj) and name[0] != "_" and filter_keyword in name:
                    # Escape underscores in the function name
                    escaped_name = name.replace("_", r"\_")
                    escaped_name_2 = name.replace("_", r"")

                    # Get the function signature
                    try:
                        signature = inspect.signature(obj)
                        # Replace underscores in the signature for LaTeX compatibility
                        escaped_signature = str(signature).replace("_", r"\_")
                    except ValueError:
                        escaped_signature = "()"

                    # Get the docstring and escape LaTeX special characters
                    docstring = inspect.getdoc(obj) or "No docstring available."
                    escaped_docstring = docstring#.replace("_", r"\_")

                    # Write the function name, signature, and docstring
                    f.write("\\subsection*{\\texttt{" + escaped_name + escaped_signature + "}}\n")
                    f.write("\\label{fun:" +escaped_name_2+ "}\n")
                    f.write("\\addcontentsline{toc}{subsection}{"+escaped_name+"}\n\n")
                    # f.write("\\label{"+escaped_name+"}\n") # crashes
                    f.write(r"\begin{lstlisting}[language=docstring]" + "\n")
                    f.write(escaped_docstring + "\n")
                    f.write(r"\end{lstlisting}" + "\n\n")
                    f.write(r"\begin{flushright}" + "\n\n")
                    f.write(r"\hyperref[toc]{ToC}" + "\n\n")
                    f.write(r"\end{flushright}" + "\n\n")
                    f.write(r"\input{functions/" + name + "}\n\n")
                    f.write(r"\vspace{5mm}" + "\n\n")
                    f.write(r"\hrule" + "\n\n")
                    # f.write(r"\newpage" + "\n")

                    # create files to be included if necessary
                    with open(f'textom/documentation/functions/{name}.tex','a') as fid:
                        pass        
                    
        # Write the LaTeX end
        f.write(r"\end{document}")
        
        # Write the LaTeX end
        f.write(r"\end{document}")

    print(f"LaTeX document saved to {output_file}")

import textom
generate_latex_doc(textom.textom, 'textom/documentation/textom_documentation.tex')
# run with python textom/documentation/create_documentation.py