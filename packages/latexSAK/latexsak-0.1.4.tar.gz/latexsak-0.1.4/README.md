[![PyPI Version](https://img.shields.io/pypi/v/latexSAK)](https://pypi.org/project/latexSAK/)
[![License](https://img.shields.io/github/license/casiez/latexSAK)](LICENSE)

# LatexSAK

LaTeX swiss army knife
## Install
```pip install latexSAK --upgrade```

You need the following commands available on your computer:
- latexpand
- delatex (brew install opendetex)
- awk
- zip 
## Features

Run ```latexSAK -h``` to show all the options available.

latexSAK first removes all commands listed in ```commandsToIgnore.json```. This file is generated in the current folder the first time the command is executed. You can then edits the commands to ignore by editing this file that will be loaded upon running the command again.

```commandsToIgnore.json``` defines 4 levels of command to ignore that can be set using the ```-level``` option. The default level is 1.
### Number of words --count
Count the number of words
### clean the tex file and figures --clean
Creates a clean version of the document, using image files actually used. Cleaned files can be found in articleclean/ folder.
### zip --zip
Creates the zip archive of the previously cleaned folder (articleclean/).
### Get text --text
Get text only and creates the file ```articleTextOnly.md```
### Captions --captions
Get captions from images and tables that use the \Description command from [acmart](https://www.ctan.org/pkg/acmart). 
