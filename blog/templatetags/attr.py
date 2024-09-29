from django import template
from django.utils.safestring import SafeString 
from django.utils.safestring import mark_safe
import re
register=template.Library()

"""
attr 模板过滤器
在模板中修改或添加表单的属性(css 等)

"""


@register.filter
def attr(field,attr_value):
    attr=attr_match(attr_value)
    if attr != None:
        if type(field) == SafeString:
            return replace(attr,str(field))
        else:
            for kv in attr['kv']:
                field.field.widget.attrs[kv['attr']] = kv['value']
    return field        


# 覆盖 或 添加 html标签属性（有属性则覆盖，没有则添加）
def replace(attr,html):
    for it in attr['kv']:
        pattern = fr'''({it['attr']})="(.*?)"'''
        match = re.search(pattern,html)
        if match:
            html = re.sub(pattern,r'\1="\2"',html)  
        else:
            lb=re.search(r'<(\w+)',html).group(1)
            return mark_safe(html.replace(f"<{lb}",f"<{lb} {attr['rst']} "))
    return mark_safe(html)
    

    
def attr_match(attr):
    pattern = r'(.*?):([\w\-]+)(?:[,|\s]?)'
    matchs= re.finditer(pattern,attr)
    if matchs:
        result={
            'kv':[],
            'rst': re.sub(pattern,r'\1="\2"',attr)
        }
        for match in matchs:
            result['kv'].append({'attr':match.group(1),'value':match.group(2)})
        return result
    return None


