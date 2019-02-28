"""
thanks to https://github.com/duanyifei/antispider.git
"""
import re
import string
from urllib import parse
import urllib
import requests
import traceback
from collections import defaultdict


def get_char(js, replace_count):
    all_var = {}

    if_else_no_args_return_constant_function_functions = []
    """ e.g.
    function zX_() {
            function _z() {
                return '09';
            };
            if (_z() == '09,') {
                return 'zX_';
            } else {
                return _z();
            }
        }
    """
    constant_function_regex4 = re.compile("""
        function\s+\w+\(\)\s*\{\s*
            function\s+\w+\(\)\s*\{\s*
                return\s+[\'\"][^\'\"]+[\'\"];\s*
            \};\s*
            if\s*\(\w+\(\)\s*==\s*[\'\"][^\'\"]+[\'\"]\)\s*\{\s*
                return\s*[\'\"][^\'\"]+[\'\"];\s*
            \}\s*else\s*\{\s*
                return\s*\w+\(\);\s*
            \}\s*
        \}
        """,
            re.X)
    l = constant_function_regex4.findall(js)    # find all functions in js
    for i in l:
        function_name = re.search("""
        function\s+(\w+)\(\)\s*\{\s*
            function\s+\w+\(\)\s*\{\s*
                return\s+[\'\"]([^\'\"]+)[\'\"];\s*
            \};\s*
            if\s*\(\w+\(\)\s*==\s*[\'\"]([^\'\"]+)[\'\"]\)\s*\{\s*
                return\s*[\'\"]([^\'\"]+)[\'\"];\s*
            \}\s*else\s*\{\s*
                return\s*\w+\(\);\s*
            \}\s*
        \}
        """, i,
            re.X)       # find a:the function name, b:string content of first return, 
                        # c: string content of the right value in 'if' condition, d: string content of second return stmt
        if_else_no_args_return_constant_function_functions.append(function_name.groups())
        js = js.replace(i, "")
        # 替换全文
        a,b,c,d = function_name.groups()
        all_var["%s()"%a] = d if b == c else b


    if_else_no_args_return_function_constant_functions = []
    """  e.g.
    function wu_() {
            function _w() {
                return 'wu_';
            };
            if (_w() == 'wu__') {
                return _w();
            } else {
                return '5%';
            }
        }
    """
    constant_function_regex5 = re.compile("""
        function\s+\w+\(\)\s*\{\s*
            function\s+\w+\(\)\s*\{\s*
                return\s+[\'\"][^\'\"]+[\'\"];\s*
            \};\s*
            if\s*\(\w+\(\)\s*==\s*[\'\"][^\'\"]+[\'\"]\)\s*\{\s*
                return\s*\w+\(\);\s*
            \}\s*else\s*\{\s*
                return\s*[\'\"][^\'\"]+[\'\"];\s*
            \}\s*
        \}
        """,
            re.X)
    l = constant_function_regex5.findall(js)
    for i in l:
        function_name = re.search("""
        function\s+(\w+)\(\)\s*\{\s*
            function\s+\w+\(\)\s*\{\s*
                return\s+[\'\"]([^\'\"]+)[\'\"];\s*
            \};\s*
            if\s*\(\w+\(\)\s*==\s*[\'\"]([^\'\"]+)[\'\"]\)\s*\{\s*
                return\s*\w+\(\);\s*
            \}\s*else\s*\{\s*
                return\s*[\'\"]([^\'\"]+)[\'\"];\s*
            \}\s*
        \}
        """, i,
            re.X)
        if_else_no_args_return_function_constant_functions.append(function_name.groups())
        js = js.replace(i, "")
        # replace
        a,b,c,d = function_name.groups()
        all_var["%s()"%a] = b if b == c else d

    #  add by sjj
    no_args_return_const_str_functions = []
    """
    var hR_=function(){
        'hR_';
        var _h=function(){
            return '最本机';
        };
        return _h();
    };
    """
    no_args_return_const_str_reg = re.compile("""
    var\s+[^=]+=\s*function\(\)\{
        \s*[\'\"]\w+[\'\"];\s*
        var\s+[^=]+=\s*function\(\)\{\s*return\s+[\'\"][^\'\"]+[\'\"];\s*\};
        \s*return\s+\w+\(\);\s*
    \};
    """, re.X)
    l = no_args_return_const_str_reg.findall(js)
    for i in l:
        function_name = re.search("""
        var\s+([^=]+)=\s*function\(\)\{
        \s*[\'\"]\w+[\'\"];\s*
        var\s+[^=]+=\s*function\(\)\{\s*return\s+[\'\"]([^\'\"]+)[\'\"];\s*\};
        \s*return\s+\w+\(\);\s*
        \};
        """, i, re.X)
        no_args_return_const_str_functions.append(function_name.groups())
        js = js.replace(i, "")
        a,b = function_name.groups()
        all_var["%s()"%a] = b

    var_args_equal_value_functions = []
    """
    var ZA_ = function(ZA__) {
            'return ZA_';
            return ZA__;
        };
    """
    constant_function_regex1 = re.compile("var\s+[^=]+=\s*function\(\w+\)\{\s*[\'\"]return\s*\w+\s*[\'\"];\s*return\s+\w+;\s*\};")
    l = constant_function_regex1.findall(js)
    for i in l:
        function_name = re.search("var\s+([^=]+)", i).group(1)
        var_args_equal_value_functions.append(function_name)
        js = js.replace(i, "")

        a = function_name
        js = re.sub("%s\(([^\)]+)\)"%a, r"\1", js)

    # 
    var_no_args_return_constant_functions = []
    """
    var Qh_ = function() {
            'return Qh_';
            return ';';
        };
    """
    constant_function_regex2 = re.compile("""
            var\s+[^=]+=\s*function\(\)\{\s*
                [\'\"]return\s*\w+\s*[\'\"];\s*
                return\s+[\'\"][^\'\"]+[\'\"];\s*
                \};
            """,
            re.X)
    l = constant_function_regex2.findall(js)
    for i in l:
        function_name = re.search("""
            var\s+([^=]+)=\s*function\(\)\{\s*
                [\'\"]return\s*\w+\s*[\'\"];\s*
                return\s+[\'\"]([^\'\"]+)[\'\"];\s*
                \};
            """,
            i,
            re.X)
        var_no_args_return_constant_functions.append(function_name.groups())
        js = js.replace(i, "")
        a,b = function_name.groups()
        all_var["%s()"%a] = b

    no_args_return_constant_functions = []
    """
    function ZP_() {
            'return ZP_';
            return 'E';
        }
    """
    constant_function_regex3 = re.compile("""
            function\s*\w+\(\)\s*\{\s*
                [\'\"]return\s*[^\'\"]+[\'\"];\s*
                return\s*[\'\"][^\'\"]+[\'\"];\s*
            \}\s*
        """,
        re.X)
    l = constant_function_regex3.findall(js)
    for i in l:
        function_name = re.search("""
            function\s*(\w+)\(\)\s*\{\s*
                [\'\"]return\s*[^\'\"]+[\'\"];\s*
                return\s*[\'\"]([^\'\"]+)[\'\"];\s*
            \}\s*
        """,
        i,
        re.X)
        no_args_return_constant_functions.append(function_name.groups())
        js = js.replace(i, "")
        a,b = function_name.groups()
        all_var["%s()"%a] = b


    # 
    no_args_return_constant_sample_functions = []
    """
    function do_() {
            return '';
        }
    """
    constant_function_regex3 = re.compile("""
            function\s*\w+\(\)\s*\{\s*
                return\s*[\'\"][^\'\"]*[\'\"];\s*
            \}\s*
        """,
        re.X)
    l = constant_function_regex3.findall(js)
    for i in l:
        function_name = re.search("""
            function\s*(\w+)\(\)\s*\{\s*
                return\s*[\'\"]([^\'\"]*)[\'\"];\s*
            \}\s*
        """,
        i,
        re.X)
        no_args_return_constant_sample_functions.append(function_name.groups())
        js = js.replace(i, "")
        a,b = function_name.groups()
        all_var["%s()"%a] = b

    # 
    """
    (function() {
                'return sZ_';
                return '1'
            })()
    """
    constant_function_regex6 = re.compile("""
            \(function\(\)\s*\{\s*
                [\'\"]return[^\'\"]+[\'\"];\s*
                return\s*[\'\"][^\'\"]*[\'\"];?
            \}\)\(\)
        """,
        re.X)
    l = constant_function_regex6.findall(js)
    for i in l:
        function_name = re.search("""
            \(function\(\)\s*\{\s*
                [\'\"]return[^\'\"]+[\'\"];\s*
                return\s*([\'\"][^\'\"]*[\'\"]);?
            \}\)\(\)
        """,
        i,
        re.X)
        js = js.replace(i, function_name.group(1))

    # 字符串拼接时使用返回参数的函数
    """
    (function(iU__) {
                'return iU_';
                return iU__;
            })('9F')
    """
    constant_function_regex6 = re.compile("""
            \(function\(\w+\)\s*\{\s*
                [\'\"]return[^\'\"]+[\'\"];\s*
                return\s*\w+;
            \}\)\([\'\"][^\'\"]*[\'\"]\)
        """,
        re.X)
    
    l = constant_function_regex6.findall(js)
    for i in l:
        function_name = re.search("""
            \(function\(\w+\)\s*\{\s*
                [\'\"]return[^\'\"]+[\'\"];\s*
                return\s*\w+;
            \}\)\(([\'\"][^\'\"]*[\'\"])\)
        """,
        i,
        re.X)
        js = js.replace(i, function_name.group(1))

    # 直接返回参数的函数            sjj
    var_args_return_args_functions = []
    """
    var Ky_=function(Ky__){
        return Ky__;
    };
    """
    constant_function_regex6 = re.compile("""
            var\s+[^=]+=\s*function\(\w+\)\{\s*
                return\s+\w+;\s*
                \};
        """,
        re.X)
    
    l = constant_function_regex6.findall(js)
    for i in l:
        function_name = re.search("var\s+([^=]+)",i).group(1)
        var_args_return_args_functions.append(function_name)
        js = js.replace(i, "")
        # 替换全文
        a = function_name
        js = re.sub("%s\(([^\)]+)\)"%a, r"\1", js)

        # js = js.replace(i, function_name.group(1))

    

    # 获取所有变量
    var_regex = "var\s+(\w+)\s*=\s*([\'\"].*?[\'\"]);\s"

    for var_name, var_value in re.findall(var_regex, js):
        var_value = re.sub("\s", "", var_value).strip("\'\" ")
        if "(" in var_value:
            var_value = ";"
        all_var[var_name] = var_value

    # 注释掉 此正则可能会把关键js语句删除掉
    #js = re.sub(var_regex, "", js)

    for var_name, var_value in all_var.items():
        js = js.replace(var_name, var_value)

    js = re.sub("[\s+']", "", js)

    # 寻找%E4%B8%AD%E5%80%92%E 密集区域
    #string_region = re.findall("((?:%\w\w)+)", js)

    # string is already utf-8 encoded
    # string_region = re.findall("((?:%\w\w|[A-Za-z\d])+)", js)         # update by sjj 2019-02-27
    # get the content in bracket following 'decodeURIComponent'
    string_region = re.findall("((?:[\u4E00-\u9FA5]|[A-Za-z\d·])+)", js)
    # deduplicate
    string_region = set(string_region)
    # 判断是否存在汉字
    chinese_flag = 0
    for string_ in string_region:
        # if re.search("%\w\w", string_):
        if re.search("[\u4E00-\u9FA5]", string_):       # update by sjj 2019-02-27
            chinese_flag = 1
    if not chinese_flag:
        # 可能混淆字符为纯英文 。。。尚未解决
        return []
    string_str = ""
    for string_ in string_region:
        # if not re.search("%\w\w", string_):
        if not re.search("[\u4E00-\u9FA5]", string_):       # update by sjj 2019-02-27
            continue
        # 过滤 
        # utf8_string = parse.unquote(string_)             # update by sjj 2019-02-27
        utf8_string = string_.rstrip(string.ascii_letters+string.digits+'_')

        # if not utf8_string.isalpha():
        #     # 去掉可能匹配到的多余字符 \w+  建立在混淆字符串是排好序的 字母在汉字前
        #     utf8_string = utf8_string.rstrip(string.ascii_letters + string.digits + "_")
        # try:                                              # update by sjj 2019-02-27
        #     # unicode_string = utf8_string.decode("utf8")   # update by sjj 2019-02-27
        #     unicode_string = utf8_string
        #     # print(unicode_string, flush=True)
        # except:                                           # update by sjj 2019-02-27
        #     continue                                      # update by sjj 2019-02-27
        # if len(unicode_string) < replace_count:           # update by sjj 2019-02-27
        #     continue
        # if len(string_) > len(string_str):
        #     string_str = string_


        if len(utf8_string) < replace_count:
            continue
        if len(utf8_string) > len(string_str):
            string_str = utf8_string

    # utf8_string = parse.unquote(string_str)
    # if not utf8_string.isalpha():
    #     # 去掉可能匹配到的多余字符 \w+  建立在混淆字符串是排好序的 字母在汉字前
    #     utf8_string = utf8_string.rstrip(string.ascii_letters + string.digits + "_")

    # unicode_string = utf8_string.decode("utf8")
    unicode_string = string_str

    # 当只有一个替换字符时 下面正则寻找失败 此时也不用寻找了
    if len(unicode_string) == 1:
        return [unicode_string]


    # 从 字符串密集区域后面开始寻找索引区域
    index_m = re.search("([\d,]+(;[\d,]+)+)", js[js.find(string_str) + len(string_str):])

    string_list = list(unicode_string)
    index_list = index_m.group(1).split(";")

    _word_list = []
    for word_index_list in index_list:
        _word = ""
        if "," in word_index_list:
            word_index_list = word_index_list.split(",")
            word_index_list = [int(x) for x in word_index_list]
        else:
            word_index_list = [int(word_index_list)]
        for word_index in word_index_list:
            if word_index < len(string_list):
                _word += string_list[word_index]
            else:
                break
                print('list index out of range')
        _word_list.append(_word)
    return _word_list

def get_page(page):
    _types_info = defaultdict(list)
    types = re.findall('hs_kw(\d+_[^\'\"]+)', page)
    for item in types:
        idx, type = item.split("_")         # item: 28_configcj
        _types_info[type].append(idx)
    # 获取混淆字符个数   type:num
    types = {type: len(set(value)) for type, value in _types_info.items()}

    js_list = re.findall("<script>(\(function[\s\S]+?)\(document\);</script>", page)    # text.encode("utf8")
    type_charlist = {}
    for js in js_list:
        for _type in types:
            if _type in js:
                break
        else:
            continue
        if not js:
            continue
        try:
            char_list = get_char(js, types[_type])
        except Exception as e:
            traceback.print_exc()
            continue
        type_charlist.update({_type: char_list})

    def char_replace(m):
        index = int(m.group(1))
        typ = m.group(2)
        char_list = type_charlist.get(typ, [])
        if not char_list:
            return m.group()
        char = char_list[index]
        return char
    page = re.sub("<span\s*class=[\'\"]hs_kw(\d+)_([^\'\"]+)[\'\"]></span>", char_replace, page)
    return page


if __name__ == '__main__':
    '''raw.html is the raw page crawling from autohome'''
    page = open('raw.html', 'r', encoding='utf-8').read()
    with open('decoded.html', 'w', encoding='utf-8') as f:
        page = get_page(page)
        f.write(page)
        print('fuck')