import os
import json
from traverse import traverse, PLURALS

def create_pack(root_dir="."):
    strings = {}

    def add_rec(el,subel,kind,designator,locale,name,canonic_name,text,filename,priority,context):
        if kind == 'quantity':
            allowed_quantities = ['zero','one','two','few','many','other']
            if locale is not None:
                allowed_quantities = PLURALS.get(locale,allowed_quantities)
                if designator not in allowed_quantities:
                    return
            for quantity in allowed_quantities:
                cn = '::'.join( canonic_name.split('::')[:-1] + [quantity] )
                if cn not in strings:
                    rec = {
                        'filename':filename,
                        'name':cn,
                        'priority':priority,
                        'context':context,
                        'original':u"%s (%s)" % (text,quantity),
                        'locales':{}
                    }
                    strings[cn] = rec

        if locale is None:
            rec = {
                'filename':filename,
                'name':canonic_name,
                'priority':priority,
                'context':context,
                'original':text,
                'locales':{}
            }
            if canonic_name not in strings or strings.get(canonic_name).get('original') is None:
                strings.setdefault(canonic_name,{}).update(rec)
        else:
            strings.setdefault(canonic_name,{}).setdefault('locales',{})[locale]=text
        return False

    traverse(root_dir,add_rec)

    strings = list(strings.values())
    strings = filter(lambda x:x.has_key('name'),strings)
    return strings
