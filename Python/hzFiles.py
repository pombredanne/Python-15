# -*- coding:utf8 -*-
#!/usr/bin/python
# Python:   3.5.1
# Platform: Windows
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  Files
# History:  2016/09/04
#           2016/10/07 PEP 8 Code Style

import sys
import re
import os
import os.path
import logging


from glob import glob


class hzFiles:

    def __init__(self, dirPath=sys.path[0], debug=False):
        super(hzFiles, self).__init__()
        self.dirPath = dirPath
        self.debug = debug
        self.count = 0
        self.braceCnt = 0
        self.lineAsterisk = 0

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='logging.log',
                            filemode='w')

    def findAllFilesInFolder(self):
        ''' Find all files in current folder.
        Argument(s):
                    None
        Return(s):
                    filesList
        Notes:
                    2016-10-08 V1.0[Heyn]
        '''
        filesList = []
        for root, dirs, files in os.walk(self.dirPath):
            for fileObj in files:
                filesList.append(os.path.join(root, fileObj))
        return filesList

    def findRuleFilesInFolder(self, pattern="*.*"):
        ''' Find all files in current folder by pattern.
        Argument(s):
                    pattern (* , ? , [ , ] )
                    e.g. Grep .c and .h files   pattern = "*.[c,h]"
                    e.g. Grep .jpg files        pattern = "*.jpg"
        Return(s):
                    filesList
        Notes:
                    (Used Module) from glob import glob
                    2016-10-08 V1.0[Heyn]
        '''
        filesList = []
        for root, dirs, files in os.walk(self.dirPath):
            for match in glob(os.path.join(root, pattern)):
                filesList.append(match)
        return filesList

    def findStringInFile(self, filePath, pattern="[\s\S]*"):
        ''' .
        Argument(s):
                    filePath : file path
                    pattern([\s\S]*) : Search any characters
        Return(s):
                    contentDict = {lineNumber：eachLine， key2：value2， …}
        Notes:
                    2016-10-08 V1.0[Heyn]
        '''
        contentDict = {}
        fileObj = open(filePath, 'r', encoding='SJIS', errors='ignore')
        try:
            for lineNumber, eachLine in enumerate(fileObj):
                if re.search(pattern, eachLine, re.I):
                    contentDict[lineNumber] = eachLine
            print((lambda dict: [item for item in dict.items()])(contentDict))
        finally:
            fileObj.close()
        return contentDict

    def findStringInDict(self, fileContentDict, pattern="[\s\S]*"):
        ''' .
        Argument(s):
                    fileContentDict  : File Content Dict
                    pattern([\s\S]*) : Search any characters
        Return(s):
                    contentDict = {index:[lineNumber, eachLine], key:[value], ...}
        Notes:
                    2016-10-08 V1.0[Heyn]
        '''
        contentDict = {}
        for index, value in fileContentDict.items():
            if re.search(pattern, value[1], re.I):
                contentDict[index] = value

        # print((lambda dict: [item for item in dict.items()])(contentDict))
        return contentDict

    def deleteAnotationInFile(self, filePath):
        ''' .
        Argument(s):
                    filePath : file path
        Return(s):
                    contentList = [(lineNumber,eachLine),(key,value),...]
        Notes:
                    2016-10-08 V1.0[Heyn]
        '''
        contentDict = {}
        multiLineNote = False
        indexDict = 0
        fileObj = open(filePath, 'r', encoding='SJIS', errors='ignore')
        try:
            for lineNumber, eachLine in enumerate(fileObj):
                eachLineRegex = re.sub(
                    '([^:]?//.*?$)|(/\*(.*?)\*/)', '', eachLine).strip()
                if (multiLineNote is False) and (
                        re.match('.*?/\*', eachLineRegex)):
                    multiLineNote = True
                    eachLineRegex = re.sub(
                        '/\*.*?$', '', eachLineRegex).strip()
                    # Methods for handling the following annotations
                    # for (i=0; i<100; i++)     /* loop 100 times
                    #                              It's test code */
                    # Add below code.
                    if eachLineRegex != '':
                        contentDict[lineNumber] = eachLineRegex
                if (multiLineNote is True) and (
                        re.match('.*?\*/$', eachLineRegex)):
                    multiLineNote = False
                    eachLineRegex = re.sub(
                        '^.*?\*/$', '', eachLineRegex).strip()
                if multiLineNote is True:
                    continue
                if eachLineRegex != '':
                    contentDict[indexDict] = [lineNumber + 1, eachLineRegex]
                    indexDict += 1
        finally:
            fileObj.close()

        for key, value in contentDict.items():
            logging.info(str(key) + "  " + str(value))

        # Sorted by key     key=lambda d: d[0]
        # Sorted by value   key=lambda d: d[1]
        # return sorted(contentDict.items(),
        #               key=lambda d: d[0],
        #               reverse = False)
        return contentDict

    def findFunctionNameInDict(self, fileContentDict):
        '''
        Argument(s):
                    fileContentDict = {key : [lineNumber, function]}
        Return(s):
                    None
        Notes:
                    2016-10-10 V1.0[Heyn]
        '''

        # Dict
        lineNumList1 = [x[0]
                        for x in fileContentDict.items() if '{' in x[1][1]]
        lineNumList2 = [x[0]
                        for x in fileContentDict.items() if '}' in x[1][1]]
        # print(lineNumList1)
        # print(lineNumList2)

        if len(lineNumList1) == 0 or len(lineNumList2) == 0:
            return []

        functionLineNum = []
        functionLineNum.append(lineNumList1[0] - 1)
        for x in lineNumList1:
            if x > lineNumList2[0]:
                lineNumList2 = [y for y in lineNumList2 if x < y]
                # The number of braces{} in the function is the same
                if len(lineNumList2) == (len(lineNumList1) -
                                         lineNumList1.index(x)):
                    functionLineNum.append(x - 1)
        # Function must be include '(' and ')'
        # fileContentDict = {key : [lineNumber, Values]}
        functionLineNum = [
            key for key in functionLineNum if '(' in fileContentDict.get(key)[1]]
        # Remove C language key words
        cKeyWords = ['#define', 'struct', '#if', '#endif']
        functionLineNum = [key for key in functionLineNum if all(
            t not in fileContentDict.get(key)[1] for t in cKeyWords)]
        # e.g. void UART_com_init ( void )
        functionSplit = list(
            map(lambda key: fileContentDict.get(key)[1].split('('), functionLineNum))
        # e.g. ['void UART_com_init ', 'void )']
        functionSplit = list(
            map(lambda x: x[0].strip().split(' ')[-1], functionSplit))
        # Update dict
        # [New] fileContentDict = {key : [lineNumber, function, functionName]}
        list(map(lambda val, key: fileContentDict[key].append(
            val), functionSplit, functionLineNum))

        # Debug information
        list(map(lambda key: print(key, fileContentDict.get(key)), functionLineNum))

        return functionLineNum

    def getInfomationFromFile(self, filePath, pattern="[\s\S]*"):
        '''<ESD> Get information from file.
        Argument(s):
                    None
        Return(s):
                    [functionName, lineNumber, keywords]
        Notes:
                    2016-10-10 V1.0[Heyn]
        '''
        infoList = []
        fileDicts = hz.deleteAnotationInFile(filePath)

        keyWordsList = sorted(hz.findStringInDict(
            fileDicts, pattern).items(), key=lambda d: d[0], reverse=False)

        fnIndexList = hz.findFunctionNameInDict(fileDicts)
        print(fnIndexList)
        print(keyWordsList)
        for keyIndex, values in keyWordsList:
            i = [x for x in fnIndexList if x > keyIndex]
            # infoList.clear()

            a = list(set(fnIndexList).difference(set(i)))
            a.sort()

            if len(i) == len(fnIndexList):
                infoList.append('None')
            elif len(i) == 0:
                infoList.append(fileDicts[fnIndexList[-1]][2])
            else:
                # print(i[0],'--->',fileDicts[i[0]][2])
                infoList.append(fileDicts[a[-1]][2])
            infoList.extend(values)

        print('*' * 40)
        print(infoList)

    def getFilesListInCurrentFolder(self):
        ''' Find files in current folder.
        Argument(s):
                    None
        Return(s):
                    FileList
        Notes:
                    2016-09-14 V1.0[Heyn]
        '''
        filesList = []
        for root, dirs, files in os.walk(self.dirPath):
            for fileObj in files:
                filesList.append(os.path.join(root, fileObj))
        return filesList

    def getFilterFilesEXT(self, filterStr):
        ''' Filter file's extension.
        Argument(s):
                    filterStr [filter key words]
                    e.g. (".c|.h")
        Return(s):
                    Grep result fileslist
        Notes:
                    2016-09-14 V1.0[Heyn]
                    2016-09-26 V1.1[Heyn]	Delete space(" ") in filterStr
        '''
        filesList = []
        # Delete space(" ") in filterStr
        filterStr = "".join([x for x in filterStr if x != " "])

        for root, dirs, files in os.walk(self.dirPath):
            for fileObj in files:
                if os.path.isfile(os.path.join(root, fileObj)):
                    ext = os.path.splitext(fileObj)[1].lower()
                    if ext in filterStr.split("|"):
                        filesList.append(os.path.join(root, fileObj))
        print("Search valid %s files = %d" % (filterStr, len(filesList)))
        return filesList

    def getFileName(self, filePath):
        fileName = os.path.basename(filePath)
        return fileName

    def getFileApproximateMatch(self, pattern):
        ''' Approximate Serach files.
        Argument(s):
                    pattern (* , ? , [ , ] )
                    e.g. Grep .c and .h files   pattern = "*.[c,h]"
                    e.g. Grep .jpg files 		pattern = "*.jpg"
        Return(s):

        Notes:  (Used Module) from glob import glob
                2016-09-15 V1.0[Heyn]
                2016-09-26 V1.0[Heyn] Add anotation.
        '''
        for root, dirs, files in os.walk(self.dirPath):
            for match in glob(os.path.join(root, pattern)):
                yield match

    def getFilePreciseMatch(self, pattern):
        ''' Precise Serach files.
        Argument(s):
                    None
        Return(s):

        Notes:  (Used Module) from glob import glob
                2016-09-17 V1.0[Heyn]
        '''
        for root, dirs, files in os.walk(self.dirPath):
            candidate = os.path.join(root, pattern)
            if os.path.isfile(candidate):
                yield os.path.abspath(candidate)

    def __getFunctionName__(self, eachLineList, eachLineStrip, functionName):
        '''
        Argument(s):
                    None
        Return(s):
                    None
        Notes:
                    2016-09-20 V1.0[Heyn]
        '''
        if re.match(".*?{.*?", eachLineStrip, re.I):
            strCache = ""
            loop = 2
            self.braceCnt += 1
            if (self.braceCnt == 1):
                # When the function name is divided into two or more rows defined
                # We need to loop processing
                try:
                    while True:
                        functionLine = str(
                            eachLineList[len(eachLineList) - loop]) + strCache
                        # Delete array
                        if re.match(".*?\[.*?\]", functionLine, re.I):
                            self.braceCnt -= 1
                            break
                        # Delete special keywords.
                        if re.match(".*?(struct|enum|union).*?", functionLine, re.I):
                            self.braceCnt -= 1
                            break

                        if re.match(".*?\(.*?\)", functionLine, re.I):
                            functionNameEnd = functionLine[
                                : functionLine.find("(")].strip()
                            functionNameStartIndex = functionNameEnd.rfind(" ")
                            functionName = functionNameEnd[
                                functionNameStartIndex + 1:].strip()
                            # print(functionName)
                            self.count += 1
                            break
                        else:
                            loop += 1
                            strCache = functionLine
                except Exception as e:
                    # print (str(e))
                    pass

        if re.match(".*?}.*?", eachLineStrip, re.I):
            if self.braceCnt > 0:
                self.braceCnt -= 1

        return functionName

    def __deleteAnotation__(self, eachLine):
        '''Find and remove the comment.
        Argument(s):
                    eachLine : file's each line.
        Return(s):
                    Remove the comment and striped.
        Notes:
                    2016-09-20 V1.0[Heyn]
        '''
        eachLineStrip = re.sub(
            '([^:]?//.*?$)|(/\*(.*?)\*/)', '', eachLine).strip()
        if re.match('.*?/\*', eachLineStrip) and self.lineAsterisk == 0:
            self.lineAsterisk = 1
            eachLineStrip = re.sub('/\*.*?$', '', eachLineStrip).strip()
        if re.match('.*?\*/$', eachLineStrip) and self.lineAsterisk == 1:
            self.lineAsterisk = 0
            eachLineStrip = re.sub('^.*?\*/$', '', eachLineStrip).strip()
        if self.lineAsterisk == 1:
            return ""
        #print (eachLineStrip)
        return eachLineStrip.strip()

    def findStringFromFile(self, filePath, regex):
        '''
        Argument(s):
                    None
        Return(s):
                    None
        Notes:
                    2016-09-17 V1.0.0[Heyn]
                    2016-09-17 V1.0.1[Heyn] Delete (space) in eachLineStrip
        '''
        functionName = ''
        infoLists = [[] for i in range(3)]  # [[], [], []]
        fileList = []
        lineNum = 0
        fileObj = open(filePath, 'r', encoding='SJIS', errors='ignore')
        try:

            for eachLine in fileObj.readlines():
                lineNum += 1
                eachLineStrip = self.__deleteAnotation__(eachLine.strip())
                fileList.append(eachLineStrip)
                functionName = self.__getFunctionName__(
                    fileList, eachLineStrip, functionName)

                if eachLineStrip:
                    if re.search(regex, eachLineStrip):
                        # <bug: 1609202120> self.braceCnt != 0
                        # When the function does not match the condition
                        # The next function name match the condition
                        # The output will cause an error.
                        if self.braceCnt != 0:
                            infoLists[0].append(functionName)
                            infoLists[1].append(lineNum)
                            # Delete space in eachLineStrip
                            infoLists[2].append(
                                "".join([x for x in eachLineStrip if x != " "]))

                        if self.debug == True:
                            print("%5d" % lineNum, end='')
                            print("%20s      " %
                                  self.getFileName(filePath), end='')
                            if self.braceCnt != 0:
                                print("%50s      " % functionName, end='')
                            else:
                                print("%50s      " % "<NONE>", end='')
                            print(eachLineStrip)

            return infoLists
        finally:
            fileObj.close()

    def grepStringFromFile(self, filePath, regex):
        '''Grep string from file.
        Argument(s):
                    filePath : file path
                    regex	 : matching rule
        Return(s):
                    fileList[[], [], []]
                    [0] filePath
                    [1] line number
                    [2] content
        Notes:
                    2016-09-25 V1.0[Heyn]
        '''

        infoLists = [[] for i in range(3)]  # [[], [], []]
        lineNum = 0
        fileObj = open(filePath, 'r', encoding='SJIS', errors='ignore')
        try:
            for eachLine in fileObj.readlines():
                lineNum += 1
                eachLineStrip = self.__deleteAnotation__(eachLine.strip())
                if eachLineStrip:
                    if re.search(regex, eachLineStrip, re.I):
                        infoLists[0].append(filePath)
                        infoLists[1].append(lineNum)
                        infoLists[2].append(eachLineStrip)
                        if self.debug == False:
                            print("%5d" % lineNum, end='')
                            print("%20s      " %
                                  self.getFileName(filePath), end='')
                            print(eachLineStrip)

            return infoLists
        finally:
            fileObj.close()

if __name__ == '__main__':
    # hz = hzFiles()
    # fileList = hz.findRuleFilesInFolder("DGT_*.[c,h]")
    # for x in fileList:
    #     dicts = hz.deleteAnotationInFile(x)
    #     functionNameDicts = hz.findFunctionNameInDict(dicts)
    #     if len(functionNameDicts) :
    #         print (x , len(functionNameDicts))
    # print(len(fileList))

    hz = hzFiles()
    hz.getInfomationFromFile("G:\@gitHub\Python\LD_LCM.c", 'LCD_BUFFER')
