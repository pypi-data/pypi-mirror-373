import re

def format(template, prefix, suffix, **varDict):
    """
    由于标准的 `str.format` 需要对于 `{`, `}` 转义：`{` 要写成 `{{`，`}` 要写成 `}}`
    因此本函数仅适用于大量使用`{` `}`的字符串模板场合，其他场合皆应使用标准的 `str.format`
    example:
        format('123 $(name) def $(name)d', '$(', ')', name='x') == '123 x def xd'
    """
    s = template
    for k, v in varDict.items():
        s = s.replace(prefix+k+suffix, v)
    return s


# deprecated, replace with textwrap.indent(s, prefix)
def prefixM(prefix, s):
    """为字符串添加前缀，对于多行字符串，每行都添加前缀"""
    if '\n' not in s:
        return prefix+s

    ret = ''
    lines = s.split('\n')
    lineCount = len(lines)
    for index in range(lineCount):
        ret += prefix
        ret += lines[index]
        if index != lineCount-1:  # 最后一行不要添加换行符
            ret += '\n'
    return ret


def replace(s, replaceMap, useRegex=False, regexFlags=0):
    """将s用replaceMap进行替换，并返回替换后的字符串
    若id(返回值) == id(s)表示没有发生任何替换
    """
    for k, v in replaceMap.items():
        if useRegex:
            pattern = re.compile(k, regexFlags)
            s, replacedCount = pattern.subn(v , s)
        else:
            if k in s:
                s = s.replace(k, v)
    return s


def camelToUnderScore(s):
    """
    AbcDef -> Abc_Def
    AbcDEFGhi -> Abc_DEF_Ghi
    abcAbcDEF -> abc_Abc_DEF
    """ 
    prev = None
    ret = ''    
    
    for i, c in enumerate(s):
        if c.islower(): # 小写字母直接追加
            ret += c
        else:  # 当前为大写字母
            if prev is None:  # 前一个字母不存在或小写
                # 新单词开端
                ret += c
            elif prev.islower():  # 前一个字母小写
                # 新单词开端
                ret += '_' + c
            else:  # 前一个字母为大写
                if i == len(s)-1:  # 没有下一个字母
                    # 非新单词开端
                    ret += c
                else:  # 有下一个字母
                    if s[i+1].islower():  # 下一个字母为小写                    
                        # 当前字母为新单词开端
                        ret += '_' + c
                    else:  # 下一个字母为大写
                        # 当前字母非新单词开端
                        ret += c
        prev = c
       
    return ret


def insert(src, pos, s):
    """在src的pos处插入s"""
    before = src[:pos]
    after = src[pos:]
    return before + s + after


def getFuBaMap(FuBa, FuBaCN, charset='fuba'):
    """charset必须为4个小写字母"""
    s_FuBaCN = charset[0].upper()+charset[1]+charset[2].upper()+charset[3]+'CN'
    s_FuBa = charset[0].upper()+charset[1]+charset[2].upper()+charset[3]
    s_fuba = charset
    s_FUBA = charset.upper()
    s_Fuba = s_fuba.capitalize()
    s_fuBa = s_FuBa[0].lower()+s_FuBa[1:]
    s_Fu_Ba = charset[0].upper()+charset[1]+'_'+charset[2].upper()+charset[3]
    s_fu_ba = charset[0]+charset[1]+'_'+charset[2]+charset[3]
    s_FU_BA = charset[0].upper()+charset[1].upper()+'_'+charset[2].upper()+charset[3].upper()
    s_Fu_ba = s_fu_ba.capitalize()
    s_fu_Ba = s_Fu_Ba[0].lower()+s_Fu_Ba[1:]
    return {        
        s_FuBaCN: FuBaCN,
        s_FuBa: FuBa,
        s_fuba: FuBa.lower(),
        s_FUBA: FuBa.upper(),
        s_Fuba: FuBa.capitalize(),
        s_fuBa: FuBa[0].lower()+FuBa[1:],
        s_Fu_Ba: camelToUnderScore(FuBa),
        s_fu_ba: camelToUnderScore(FuBa).lower(),
        s_FU_BA: camelToUnderScore(FuBa).upper(),
        s_Fu_ba: camelToUnderScore(FuBa).capitalize(),
        s_fu_Ba: camelToUnderScore(FuBa)[0].lower() + camelToUnderScore(FuBa)[1:],
    }