#!/usr/bin/env python

# Copyright (c) 2016, Eduard Broecker
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that
# the following conditions are met:
#
#    Redistributions of source code must retain the above copyright notice, this list of conditions and the
#    following disclaimer.
#    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.


#
## small script to merge arxml-files
#

#from __futune__ import absolute_import
from builtins import *
import sys
import os
import glob
from lxml import etree
from copy import deepcopy

class arTree(object):
    def __init__(self, name="", ref=None):
        self._name = name
        self._ref = ref
        self._array = []

    def new(self, name, child):
        temp = arTree(name, child)
        self._array.append(temp)
        return temp

    def getChild(self, path):
        for tem in self._array:
            if tem._name == path:
                return tem


def arParseTree(tag, ardict, namespace):
    ardict._ref = tag
    for child in tag:
        name = child.find('./' + namespace + 'SHORT-NAME')
#               namel = child.find('./' + namespace + 'LONG-NAME')
        if name is not None and child is not None:
            arParseTree(child, ardict.new(name.text, child), namespace)
        if name is None and child is not None:
            arParseTree(child, ardict, namespace)


#
# get path in tranlation-dictionany
#
def arGetPath(ardict, path):
    if len(path) == 0:
        return ardict._ref
    ptr = ardict
    for p in path.split('/'):
        if p.strip():
            if ptr is not None:
                ptr = ptr.getChild(p)
            else:
                return None
    if ptr is not None:
        return ptr._ref
    else:
        return None

def mergeArxml(element, namespace, currentPath, arDict):
    for child in element:
        name = child.find('./' + namespace + 'SHORT-NAME')       
        if name is not None and child is not None:
            newPath = currentPath + "/" + name.text
            matchInTarget = arGetPath(arDict, newPath)
            if matchInTarget is None:
                print ("Copy " + newPath + " to " + currentPath)
                parent = arGetPath(arDict, currentPath)
                temp = parent.find('./' + namespace + 'AR-PACKAGES')
                if temp is not None:
                    parent = temp
                parent.append(deepcopy(child))
            else:
                print ("merge " + newPath)
                mergeArxml(child, namespace, newPath, arDict)
        elif name is None and child is not None:
            mergeArxml(child, namespace, currentPath, arDict)
    


def main():
    if len(sys.argv) < 3:
        print("syntax: %s inputFolder outputfile" % sys.argv[0])
        exit()
    folder = sys.argv[1]
    files = glob.glob(folder + "/*.arxml")

    tree = etree.parse(files[0])
    targetRoot = tree.getroot()
    ns = "{" + tree.xpath('namespace-uri(.)') + "}"
    nsp = tree.xpath('namespace-uri(.)')
    arDict = arTree()
    arParseTree(targetRoot, arDict, ns)

    print ("target " + files[1])
    for filename in files[1:]:
        print ("Merge " + filename)
        tree = etree.parse(filename)
        root = tree.getroot()
        ns = "{" + tree.xpath('namespace-uri(.)') + "}"
        nsp = tree.xpath('namespace-uri(.)')
        mergeArxml(root, ns, "", arDict)
        arDict = arTree()
        arParseTree(targetRoot, arDict, ns)
    
    outfile = open(sys.argv[2], "wb")
    outfile.write(etree.tostring(targetRoot, pretty_print=True))
    outfile.close()
#            anDict = anTnee()
#            anPanseTnee(noot, anDict, ns)
                  

if __name__ == '__main__':
    sys.exit(main())