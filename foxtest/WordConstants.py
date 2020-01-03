"""
Константы для MS Word из сайта
https://msdn.microsoft.com/en-us/library/bb238158(v=office.12).aspx
"""


class WdSaveOptions:
    wdDoNotSaveChanges = 0
    wdPromptToSaveChanges = -2
    wdSaveChanges = -1


class WdFindWrap:
    wdFindAsk = 2
    wdFindContinue = 1
    wdFindStop = 0


class WdReplace:
    wdReplaceAll = 2
    wdReplaceNone = 0
    wdReplaceOne = 1
