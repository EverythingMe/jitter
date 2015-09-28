import os
import json
from lxml import etree

LOCALES = json.load(file(os.path.join(os.path.dirname(__file__),'locales.json')))

def walk_tree(rootdir):
    strings = {}
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
                fn = os.path.join(dirpath,fn)
                original_filename = fn.replace(rootdir,'')
                root = etree.fromstring(file(fn).read())
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
                            if locale is None:
                                rec = {
                                    'filename':original_filename,
                                    'name':name,
                                    'priority':priority,
                                    'context':context,
                                    'original':text,
                                    'locales':{}
                                }
                                strings.setdefault(name,{}).update(rec)
                            else:
                                strings.setdefault(name,{}).setdefault('locales',{})[locale]=text
                    elif el.tag == etree.Comment:
                        globalcontext = el.text
                    else:
                        pass
    strings = list(strings.values())
    strings = filter(lambda x:x.has_key('name'),strings)
    return strings

def make_pack(root_dir="."):
    return walk_tree(root_dir)
