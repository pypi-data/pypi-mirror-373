#!/usr/bin/env python3
#
# Gery Casiez
# 2020 - 2022
#

import argparse
import os
import json
import sys
from os.path import exists
from pathlib import Path
from TexSoup import TexSoup
from TexSoup import TexNode
from TexSoup import data

class myList(list):
    def __new__(cls, data=None):
        obj = super(myList, cls).__new__(cls, data)
        return obj

    def __str__(self):
        return ''. join(list(self))

def createDir(path):
    if (not(os.path.exists(path))):
        os.makedirs(path)   

def msg(text, display=True):
    if display:
        print(text)

def removeCommands(soup, cmds):
    # for cmd in cmds:
    #     for c in soup.find_all(cmd):
    #         c.name = ' '

    for cmd in cmds:
        for c in soup.find_all(cmd):
            desc = myList()
            for d in c.descendants:
                desc.append(d)
            c.replace_with(desc)    

# Replace command cmd with txt
def replaceCommand(cmd, txt):
    for c in soup.find_all(cmd):
        try:
            c.replace_with(TexNode(data.TexText(txt)))
        except Exception as e:
            print("pb with %s: %s"%(c, e))

def cleanCode(soup):
    mainDir = 'articleclean'
    createDir(mainDir)

    # Copy bib files
    os.system("cp *.bib articleclean/")

    # Copy sty files
    os.system("cp *.sty articleclean/")

    # Check if graphicspath command exists
    graphicsMainDir = ''

    for c in soup.find_all('graphicspath'):
        graphicsMainDir = str(c.contents[0]).replace("{","").replace("}","")

    # Get images
    listImg = []
    dirs = []
    for c in soup.find_all('includegraphics'):
        img = str(c.args[-1]).replace("{","").replace("}","")
        directory = img.split("/")
        actualDir = "/".join(directory[:-1])
        if actualDir not in dirs:
            dirs.append("%s%s"%(graphicsMainDir, actualDir))
        listImg.append(img)

    # Create folders and clean up images
    createDir(mainDir)
    for d in dirs:
        createDir("%s/%s"%(mainDir, d))
        os.system("rm -rf %s/%s/*"%(mainDir, d))

    for img in listImg:
        directory = img.split("/")
        actualDir = "/".join(directory[:-1])
        cmd = 'cp %s%s* %s/%s%s'%(graphicsMainDir, img, mainDir, graphicsMainDir, actualDir)
        os.system(cmd)

    f = open("%s/article.tex"%mainDir, "w")
    f.write(str(soup))

    f.close()

def getCaptions(soup):
    # Get images descriptions
    imgDescriptions = []
    tabDescriptions = []
    for c in soup.find_all('Description'):
        if len(c.contents) == 1:
            desc = c.contents[0]
        elif len(c.contents) == 2:
            desc = c.contents[1]
        elif len(c.contents) > 2:
            desc = "".join(c.contents[1:])
        else:
            desc = "NO DESCRIPTION"

        if c.parent.count('includegraphics') > 0:
            imgDescriptions.append(desc)
        else:
            tabDescriptions.append(desc)

    for i in range(0, len(imgDescriptions)):
        print("Figure %s:"%(i+1))
        print(imgDescriptions[i])
        print()

    for i in range(0, len(tabDescriptions)):
        print("Table %s:"%(i+1))
        print(tabDescriptions[i])
        print()

def createZip(debug=True):
    msg("Deleting articleclean.zip", debug)
    os.system("rm -rf articleclean.zip")
    msg("Creating zip from files in articleclean/", debug)
    os.system("find articleclean -path '*/.*' -prune -o -type f -print | zip articleclean.zip -@")

def countWords(soup):
    # # Only delete tables with no minipage embedded
    # for c in soup.find_all('table'):
    #     if c.find('minipage') == None:
    #         c.delete()

    f2 = open("new2.tex", "w")
    for c in soup.contents:
        f2.write(str(c))
    f2.close()

    # Remove all latex commands
    # brew install opendetex
    os.system("delatex new2.tex > new3.tex")
    os.system("awk 'NF > 0 {blank=0} NF == 0 {blank++} blank < 2' new3.tex > new4.tex")
    os.system("wc new4.tex")   
    os.system("rm new2.tex new3.tex new4.tex")  

def textOnly(soup):
    # Add # in front of sections
    for c in soup.find_all('section'):
        c.string = "# %s"%c.string

    # Add ## in front of subsections
    for c in soup.find_all('subsection'):
        c.string = "## %s"%c.string        

    # Add ### in front of subsubsections
    for c in soup.find_all('subsubsection'):
        c.string = "### %s"%c.string  

    # replace \cite with [1]
    replaceCommand('cite', "[1]")

    # replace \ref with 1
    replaceCommand('ref', "1")

    # replace \etal with et al.
    replaceCommand('etal', "et al.")

    f2 = open("new2.tex", "w")
    for c in soup.contents:
        f2.write(str(c))
    f2.close()

    # Remove all latex commands
    # brew install opendetex
    os.system("delatex new2.tex > new3.tex")
    os.system("awk 'NF > 0 {blank=0} NF == 0 {blank++} blank < 2' new3.tex > articleTextOnly.md") 
    os.system("rm new2.tex new3.tex")  

def loadJSON(file):
  try:
    with open(file) as json_file:
        data = json.load(json_file)
    return data
  except:
    print("Cound not load %s"%file)
    return []

def saveJSON(data, file):
  with open(file, 'w') as fp:
      json.dump(data, fp, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description='LaTeX swiss army knife')
    parser.add_argument('file', help = 'main tex file')
    parser.add_argument('--count', help = 'Count the number of words', action="store_true")
    parser.add_argument('--clean', help = 'clean the tex file and figures', action="store_true")
    parser.add_argument('--zip', help = 'Creates the zip archive of the previously cleaned folder', action="store_true")
    parser.add_argument('--text', help = 'Get text', action="store_true")
    parser.add_argument('--captions', help = 'Get img and tab captions', action="store_true")
    parser.add_argument('-level', nargs=1, help='Level of cleaning', type=int, default=1)
    args = parser.parse_args() 

    if exists('commandsToIgnore.json'):
        commandsToIgnoreLevels = loadJSON('commandsToIgnore.json')
    else:
        commandsToIgnoreLevels = {
            '1': ['author', 'affiliation', 'email', 'CCSXML', 'ccsdesc'],
            '2': ['streetaddress', 'city', 'orcid', 'additionalaffiliation'],
            '3': [ 'state', 'country', 'postcode'],
            '4': ['orcid', 'additionalaffiliation']
        }
        saveJSON(commandsToIgnoreLevels, 'commandsToIgnore.json')

    # List of all commands to clean
    cmdsToClean = []
    if isinstance(args.level, list):
        level = int(args.level[0])
    else:
        level = 1

    for i in range(1, level+1):
        cmdsToClean.extend(commandsToIgnoreLevels[str(i)])


    if args.zip:
        createZip()
    else:
        # Combines all tex files into one
        os.system("latexpand %s > new.tex"%(args.file))

        with open('new.tex', 'r') as f:
          s = "\n".join([x.strip() for x in f]) 

        soup = TexSoup(s)
        f.close()
        os.system("rm new.tex") 

        for c0 in cmdsToClean:
            for c in soup.find_all(c0):
                c.delete()

        if args.count:
            countWords(soup)

        if args.clean:
            cleanCode(soup)

        if args.text:
            textOnly(soup)

        if args.captions:
            getCaptions(soup)


if __name__ == "__main__":
    main()
