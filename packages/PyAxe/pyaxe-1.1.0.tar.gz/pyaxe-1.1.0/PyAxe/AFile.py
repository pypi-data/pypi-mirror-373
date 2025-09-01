import os
import re
from . import AError, AOS, AStr

class File_Error(AError.Error):
    pass


def read(filePath, encoding=None, newline=None):
    with open(filePath, encoding=encoding, newline=newline) as fp:
        return fp.read()


def write(filePath, content, encoding=None, newline=None):
    with open(filePath, 'w', encoding=encoding, newline=newline) as fp:
        fp.write(content)


def append(filePath, content, encoding=None, newline=None):
    with open(filePath, 'a', encoding=encoding, newline=newline) as fp:
        fp.write(content)


def appendUnique(filePath, content, encoding=None, newline=None):
    """仅当文件不存在此内容才追加"""
    if content in read(filePath, encoding, newline):
        return False
    append(filePath, content, encoding, newline)
    return True
        

def readStripedLines(filePath, *args, **kwargs):
    """
    每次返回一个非空行，并且去除了行首尾的空白.
    :param 和系统的open()函数一致
    """
    with open(filePath, 'r', *args, **kwargs) as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            yield line


class _replaceContent_StrReplaceError(AError.Error):
    pass

def _replaceContent(filePath, replaceMap, useRegex=False, regexFlags=0, encoding=None, newline=None):
    """
    使用replaceMap对文件内容进行替换
    useRegex: replaceMap是否使用正则表达式
    """
    with open(filePath, encoding=encoding, newline=newline) as fp:
        s = fp.read()
        try:
            newStr = AStr.replace(s, replaceMap, useRegex, regexFlags)
        except Exception as e:
            raise _replaceContent_StrReplaceError('%s' % e)

    if id(newStr) != id(s):  # changed
        with open(filePath, 'w', encoding=encoding, newline=newline) as fp:
            fp.write(newStr)


def replaceContent(filePath, replaceMap, useRegex=False, regexFlags=0, encoding=None, newline=None):
    """
    使用replaceMap对文件内容进行替换
    useRegex: replaceMap是否使用正则表达式
    encoding: 支持传递多个编码tuple/list（只要其中一个编码（可以为None）能打开即可）
    """
    if isinstance(encoding, (tuple, list)):
        lst = encoding
    else:
        lst = [encoding]

    for encode in lst:
        try:
            _replaceContent(filePath, replaceMap, useRegex=useRegex, regexFlags=regexFlags, encoding=encode, newline=newline)
            return
        except _replaceContent_StrReplaceError as e:
            raise File_Error('replaceFileContent(%s) failure: %s' % (filePath, e))
        except Exception as e:
            pass
    raise File_Error('replaceFileContent(%s) failure: can not open with encoding %s' % (filePath, encoding))


def replaceContentInDir(dir, replaceMap, fileMatchRule=None, useRegex=False, regexFlags=0, encoding=None, newline=None):
    """
    对目录dir下面所有满足条件的文件使用replaceMap进行内容替换
    fileMatchRule(fileName, filePath)是一个函数: 用于决定文件是否要参与替换
    useRegex: replaceMap是否使用正则表达式
    encoding: 支持传递多个编码tuple/list（只要其中一个编码（可以为None）能打开即可）
    """
    for _, filePath in AOS.walkFiles(dir, fileMatchRule=fileMatchRule):
        replaceContent(filePath, replaceMap, useRegex, regexFlags, encoding, newline)


def isNewer(aPath, bPath):
    """
    a是否比b新
    若a不存在，返回False
    若a存在但b不存在，返回True
    若a，b都存在则比较最后修改时间
    """
    try:
        aStat = os.stat(aPath)
    except:
        return False

    try:
        bStat = os.stat(bPath)
    except:
        return True

    return aStat.st_mtime > bStat.st_mtime


def tryWrite(filePath, content, encoding=None, newline=None):
    """如果文件内容发生变化则写入之（返回True），否则不做任何事情（返回False）"""
    if os.path.isfile(filePath):
        with open(filePath, encoding=encoding, newline=newline) as fp:
            if fp.read() == content:
                return False
    write(filePath, content, encoding=encoding, newline=newline)
    return True


def isEncodingWith(filePath, encoding):
    """
    已知问题
    1. 若文件编码为UTF8-BOM，isEncodingWith(GBK)返回True
    """
    def isUTF8(encoding):
        return encoding.lower() in ('utf8', 'utf-8', 'utf_8', 'u8')

    def isUTF8WithBOM(encoding):
        return encoding.lower() in ('utf_8_sig')

    """
    注意utf8和utf_8_sig都能打开带BOM和不带BOM的UTF8文件
    - utf8返回的文件内容不会去掉BOM标识
    - utf_8_sig返回的文件内容会自动去掉BOM标识
    """
    if isUTF8(encoding) or isUTF8WithBOM(encoding):
        try:
            with open(filePath, encoding='utf8') as fp:
                s = fp.read(1)
                if s == '\ufeff':
                    return isUTF8WithBOM(encoding)
                else:
                    return isUTF8(encoding)
        except UnicodeDecodeError:
            return False
        except Exception as e:
            raise

    try:
        with open(filePath, encoding=encoding) as fp:
            fp.read()
            return True
    except Exception:
        return False


def _convertEncoding(filePath, encodingFrom, encodingTo, newline=None):
    with open(filePath, encoding=encodingFrom, newline=newline) as fp:
        s = fp.read()

    with open(filePath, 'w', encoding=encodingTo, newline=newline) as fp:
        fp.write(s)


def convertEncoding(filePath, encodingFrom, encodingTo, newline=None):
    if not isinstance(encodingFrom, (tuple, list)):
        _convertEncoding(filePath, encodingFrom, encodingTo, newline)
        return

    errMsg = ''
    for enc in encodingFrom:
        try:
            _convertEncoding(filePath, enc, encodingTo, newline)
            return
        except Exception as e:
            errMsg += str(e) + '|'
            pass
    
    raise RuntimeError(errMsg)


def insertStrInFile(filePath, encoding, posCallback, s, newline=None):
    """
    在文件的某个位置（通过回调获得）插入s
    """
    with open(filePath, encoding=encoding, newline=newline) as fp:
        content = fp.read()
    
    # 找到插入位置
    pos = posCallback(content)
    if pos == -1:
        raise RuntimeError("向文件插入内容失败：" + filePath)

    afterContent = AStr.insert(content, pos, s)
    with open(filePath, mode='w', encoding=encoding) as fp:
        fp.write(afterContent)


def searchFirstMatchPos(s, pattern):
    """
    找到所匹配的第一个子串的位置范围[开始,结束)
    pattern: construct with re.compile
    """
    m = pattern.search(s)
    if not m:
        return (-1, -1)

    endPos = m.regs[0][1]
    length = endPos - m.regs[0][0]
    return (endPos-length, endPos)


def insertAtFirstMatchBeginPosOfFile(filePath, encoding, pattern, s, skipIfExist=False):
    """
    在文件匹配模式的第一个匹配处的开始位置插入s
    """
    if skipIfExist and s.strip() in read(filePath, encoding):
        return
            
    def posCallback(content):
        return searchFirstMatchPos(content, pattern)[0]
        
    insertStrInFile(filePath, encoding, posCallback, s)


def insertAtFirstMatchEndPosOfFile(filePath, encoding, pattern, s, skipIfExist=False):
    """
    在文件匹配模式的第一个匹配处的结束位置插入s
    """
    if skipIfExist and s.strip() in read(filePath, encoding):
        return
            
    def posCallback(content):
        return searchFirstMatchPos(content, pattern)[1]
    
    insertStrInFile(filePath, encoding, posCallback, s)


def searchLastMatchPos(s, pattern):
    """
    找到所匹配的最后一个子串的位置范围[开始,结束)
    pattern: construct with re.compile
    """
    pos = 0
    length = 0  # 匹配的子串长度
    ss = s[pos:]
    firstFlag = True
    while True:
        m = pattern.search(ss)
        if m:
            firstFlag = False
            endPos = m.regs[0][1]
            length = endPos - m.regs[0][0]
            pos += endPos
            ss = s[pos:]
        else:
            if firstFlag:
                return (-1, -1)
            return (pos-length, pos)


def insertAtLastMatchBeginPosOfFile(filePath, encoding, pattern, s, skipIfExist=False):
    """
    在文件匹配模式的最后一个匹配处的开始位置插入s
    """
    if skipIfExist and s.strip() in read(filePath, encoding):
        return
            
    def posCallback(content):
        return searchLastMatchPos(content, pattern)[0]
        
    insertStrInFile(filePath, encoding, posCallback, s)


def insertAtLastMatchEndPosOfFile(filePath, encoding, pattern, s, skipIfExist=False):
    """
    在文件匹配模式的最后一个匹配处的结束位置插入s
    """
    if skipIfExist and s.strip() in read(filePath, encoding):
        return
            
    def posCallback(content):
        return searchLastMatchPos(content, pattern)[1]
    
    insertStrInFile(filePath, encoding, posCallback, s)