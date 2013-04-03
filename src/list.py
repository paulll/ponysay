#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies
Copyright (C) 2012, 2013  Erkin Batu Altunbaş et al.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
'''
from common import *
from ucs import *



'''
File listing functions
'''
class List():
    '''
    Columnise a list and prints it
    
    @param  ponies:list<(str, str)>  All items to list, each item should have to elements: unformated name, formated name
    '''
    @staticmethod
    def __columnise(ponies):
        ## Get terminal width, and a 2 which is the space between columns
        termwidth = gettermsize()[1] + 2
        ## Sort the ponies, and get the cells' widths, and the largest width + 2
        ponies.sort(key = lambda pony : pony[0])
        widths = [UCS.dispLen(pony[0]) for pony in ponies]
        width = max(widths) + 2 # longest pony file name + space between columns
        
        ## Calculate the number of rows and columns, can create a list of empty columns
        cols = termwidth // width # do not believe electricians, this means ⌊termwidth / width⌋
        rows = (len(ponies) + cols - 1) // cols
        columns = []
        for c in range(0, cols):  columns.append([])
        
        ## Fill the columns with cells of ponies
        (y, x) = (0, 0)
        for j in range(0, len(ponies)):
            cell = ponies[j][1] + ' ' * (width - widths[j]);
            columns[x].append(cell)
            y += 1
            if y == rows:
                x += 1
                y = 0
        
        ## Make the columnisation nicer by letting the last row be partially empty rather than the last column
        diff = rows * cols - len(ponies)
        if (diff > 2) and (rows > 1):
            c = cols - 1
            diff -= 1
            while diff > 0:
                columns[c] = columns[c - 1][-diff:] + columns[c]
                c -= 1
                columns[c] = columns[c][:-diff]
                diff -= 1
        
        ## Create rows from columns
        lines = []
        for r in range(0, rows):
             lines.append([])
             for c in range(0, cols):
                 if r < len(columns[c]):
                     line = lines[r].append(columns[c][r])
        
        ## Print the matrix, with one extra blank row
        print('\n'.join([''.join(line)[:-2] for line in lines]))
        print()


    '''
    Lists the available ponies
    
    @param  ponydirs:itr<str>          The pony directories to use
    @param  quoters:__in__(str)→bool   Set of ponies that of quotes
    @param  ucsiser:(list<str>)?→void  Function used to UCS:ise names
    '''
    @staticmethod
    def simplelist(ponydirs, quoters = [], ucsiser = None):
        for ponydir in ponydirs: # Loop ponydirs
            ## Get all ponies in the directory
            _ponies = os.listdir(ponydir)
            
            ## Remove .pony from all files and skip those that does not have .pony
            ponies = []
            for pony in _ponies:
                if endswith(pony, '.pony'):
                    ponies.append(pony[:-5])
            
            ## UCS:ise pony names, they are already sorted
            if ucsiser is not None:
                ucsiser(ponies)
            
            ## If ther directory is not empty print its name and all ponies, columnised
            if len(ponies) == 0:
                continue
            print('\033[1mponies located in ' + ponydir + '\033[21m')
            List.__columnise([(pony, '\033[1m' + pony + '\033[21m' if pony in quoters else pony) for pony in ponies])
    
    
    '''
    Lists the available ponies with alternatives inside brackets
    
    @param  ponydirs:itr<str>                        The pony directories to use
    @param  quoters:__in__(str)→bool                  Set of ponies that of quotes
    @param  ucsiser:(list<str>, map<str, str>)?→void  Function used to UCS:ise names
    '''
    @staticmethod
    def linklist(ponydirs = None, quoters = [], ucsiser = None):
        ## Get the size of the terminal
        termsize = gettermsize()
        
        for ponydir in ponydirs: # Loop ponydirs
            ## Get all pony files in the directory
            _ponies = os.listdir(ponydir)
            
            ## Remove .pony from all files and skip those that does not have .pony
            ponies = []
            for pony in _ponies:
                if endswith(pony, '.pony'):
                    ponies.append(pony[:-5])
            
            ## If there are no ponies in the directory skip to next directory, otherwise, print the directories name
            if len(ponies) == 0:
                continue
            print('\033[1mponies located in ' + ponydir + '\033[21m')
            
            ## UCS:ise pony names
            pseudolinkmap = {}
            if ucsiser is not None:
                ucsiser(ponies, pseudolinkmap)
            
            ## Create target–link-pair, with `None` as link if the file is not a symlink or in `pseudolinkmap`
            pairs = []
            for pony in ponies:
                if pony in pseudolinkmap:
                    pairs.append((pony, pseudolinkmap[pony] + '.pony'));
                else:
                    pairs.append((pony, os.path.realpath(ponydir + pony + '.pony') if os.path.islink(ponydir + pony + '.pony') else None))
            
            ## Create map from source pony to alias ponies for each pony
            ponymap = {}
            for pair in pairs:
                if (pair[1] is None) or (pair[1] == ''):
                    if pair[0] not in ponymap:
                        ponymap[pair[0]] = []
                else:
                    target = pair[1][:-5]
                    if '/' in target:
                        target = target[target.rindex('/') + 1:]
                    if target in ponymap:
                        ponymap[target].append(pair[0])
                    else:
                        ponymap[target] = [pair[0]]
            
            ## Create list of source ponies concatenated with alias ponies in brackets
            ponies = {}
            for pony in ponymap:
                w = UCS.dispLen(pony)
                item = '\033[1m' + pony + '\033[21m' if (pony in quoters) else pony
                syms = ponymap[pony]
                syms.sort()
                if len(syms) > 0:
                    w += 2 + len(syms)
                    item += ' ('
                    first = True
                    for sym in syms:
                        w += UCS.dispLen(sym)
                        if first:  first = False
                        else:      item += ' '
                        item += '\033[1m' + sym + '\033[21m' if (sym in quoters) else sym
                    item += ')'
                ponies[(item.replace('\033[1m', '').replace('\033[21m', ''), item)] = w
            
            ## Print the ponies, columnised
            List.__columnise(list(ponies))
    
    
    '''
    Lists the available ponies on one column without anything bold or otherwise formated
    
    @param  standard:itr<str>?         Include standard ponies
    @param  extra:itr<str>?            Include extra ponies
    @param  ucsiser:(list<str>)?→void  Function used to UCS:ise names
    '''
    @staticmethod
    def onelist(standarddirs, extradirs = None, ucsiser = None):
        ## Get all pony files
        _ponies = []
        if standarddirs is not None:
            for ponydir in standarddirs:
                _ponies += os.listdir(ponydir)
        if extradirs is not None:
            for ponydir in extradirs:
                _ponies += os.listdir(ponydir)
            
        ## Remove .pony from all files and skip those that does not have .pony
        ponies = []
        for pony in _ponies:
            if endswith(pony, '.pony'):
                ponies.append(pony[:-5])
        
        ## UCS:ise and sort
        if ucsiser is not None:
            ucsiser(ponies)
        ponies.sort()
        
        ## Print each one on a seperate line, but skip duplicates
        last = ''
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    '''
    Prints a list of all balloons
    
    @param  balloondirs:itr<str>  The balloon directories to use
    @param  isthink:bool          Whether the ponythink command is used
    '''
    @staticmethod
    def balloonlist(balloondirs, isthink):
        ## Get the size of the terminal
        termsize = gettermsize()
        
        ## Get all balloons
        balloonset = set()
        for balloondir in self.balloondirs:
            for balloon in os.listdir(balloondir):
                ## Use .think if running ponythink, otherwise .say
                if isthink and endswith(balloon, '.think'):
                    balloon = balloon[:-6]
                elif (not isthink) and endswith(balloon, '.say'):
                    balloon = balloon[:-4]
                else:
                    continue
                
                ## Add the balloon if there is none with the same name
                if balloon not in balloonset:
                    balloonset.add(balloon)
        
        ## Print all balloos, columnised
        List.__columnise([(balloon, balloon) for balloon in list(balloonset)])

