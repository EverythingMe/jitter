import os
import json
from lxml import etree

LOCALES = json.load(file(os.path.join(os.path.dirname(__file__),'locales.json')))
PLURALS = json.load(file(os.path.join(os.path.dirname(__file__),'plurals.json')))

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def traverse(rootdir, visitor):

    for dirpath, dirnames, filenames in os.walk(rootdir):
        locale = None
        lastpart = os.path.split(dirpath)[1]
        if lastpart.startswith('values') and 'build' not in dirpath.split(os.path.sep):
            parts = lastpart.split('-')
            if len(parts)==1:
                locale=None
            else:
                locale = parts[1]
                if locale not in LOCALES:
                    continue
            for fn in filter(lambda x:x.endswith('.xml'),filenames):
                modified = False
                fn = os.path.join(dirpath,fn)
                original_filename = fn.replace(rootdir,'')
                parser = etree.XMLParser(remove_blank_text=True)
                root = etree.parse(fn,parser)
                res = root.xpath('/resources')
                globalcontext = None
                for el in res[0]:
                    if el.tag == 'string':
                        name = el.get('name')
                        priority = el.get('priority',4)
                        context = el.get('context',globalcontext)
                        translatable = el.get('translatable') != 'false'
                        text = el.text
                        if translatable:
                            modified = visitor(el,el,None,None,locale,name,name,text,original_filename,priority,context) or modified
                    elif el.tag == 'string-array':
                        array_name = el.get('name')
                        array_priority = el.get('priority',4)
                        array_context = el.get('context',globalcontext)
                        array_translatable = el.get('translatable')
                        items = el.xpath('item')
                        for index,item in enumerate(el):
                            priority = item.get('priority',array_priority)
                            context = item.get('context',array_context)
                            translatable = item.get('translatable',array_translatable) != 'false'
                            text = item.text
                            if translatable:
                                canonic_name = "%s::A::%03d" % (array_name,index)
                                modified = visitor(el,item,'array',index,locale,array_name,canonic_name,text,original_filename,priority,context) or modified
                    elif el.tag == 'plurals':
                        plural_name = el.get('name')
                        plural_priority = el.get('priority',4)
                        plural_context = el.get('context',globalcontext)
                        plural_translatable = el.get('translatable')
                        for item in el:
                            quantity = item.get('quantity')
                            priority = item.get('priority',array_priority)
                            context = item.get('context',array_context)
                            translatable = item.get('translatable',array_translatable) != 'false'
                            text = item.text
                            if translatable:
                                canonic_name = "%s::P::%s" % (plural_name,quantity)
                                modified = visitor(el,item,'quantity',quantity,locale,plural_name,canonic_name,text,original_filename,priority,context) or modified
                    elif el.tag == etree.Comment:
                        globalcontext = el.text
                    else:
                        pass

                if modified:
                    indent(root)
                    out = open(fn, 'w')
                    out.write(etree.tostring(root,encoding='UTF-8'))
                    out.close()
