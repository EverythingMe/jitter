import os
import json
import itertools

from lxml import etree

from traverse import traverse, indent

BASE_XML = '<?xml version="1.0" encoding="utf-8"?><resources xmlns:tools="http://schemas.android.com/tools" xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2"></resources>'

def process_pack(root_dir,server_pack):
    server_pack = dict((x['name'],x) for x in server_pack)
    update_pack = {}

    def remove_unused(el,subel,kind,designator,locale,name,canonic_name,text,filename,priority,context):
        if locale is None:
            if canonic_name in server_pack:
                update_pack[canonic_name] = server_pack[canonic_name]
        return False

    def check_rec(el,subel,kind,designator,locale,name,canonic_name,text,filename,priority,context):
        modified = False
        if locale is not None:
            localized = update_pack.get(canonic_name,{}).get('locales',{})
            text = localized.get(locale)
            if text is not None:
                if subel.text != text:
                    subel.text = text
                    print canonic_name,"<--",text
                    modified = True
                del localized[locale]
                if len(localized)==0:
                    del update_pack[canonic_name]

        return modified

    traverse(root_dir,remove_unused)
    traverse(root_dir,check_rec)

    to_write = sorted(update_pack.values(),key=lambda x:(x['filename'],x['name']))
    to_write = itertools.groupby(to_write,lambda x:x['filename'])
    for filename,resources in to_write:
        filename = filename.lstrip(os.path.sep)
        filename = os.path.join(root_dir,filename)
        for res in resources:
            for locale, text in res.get('locales').iteritems():
                localized_filename = filename.replace(os.path.sep+'values'+os.path.sep,os.path.sep+'values-%s' % locale+os.path.sep)
                # Create the file if needed
                if not os.path.isfile(localized_filename):
                    if not os.path.exists(os.path.dirname(localized_filename)):
                        os.makedirs(os.path.dirname(localized_filename))
                    dummy = open(localized_filename,'w')
                    dummy.write(BASE_XML)
                    dummy.close()
                # Now, open (or re-open) the localized file and parse it
                parser = etree.XMLParser(remove_blank_text=True)
                tree = etree.parse(localized_filename,parser)
                root = tree.getroot()
                assert(root.tag=='resources')
                # Find out if this is a regular resource, string-array or plurals
                name_parts = res['name'].split('::')
                parent = None
                new_el = None
                if len(name_parts) == 1:
                    new_el = etree.fromstring('<string name="%s"></string>' % name_parts[0])
                    new_el.text = text
                    print name_parts[0],"<-",text
                    parent=root
                elif len(name_parts) == 3:
                    if name_parts[1] == 'A':
                        # Array
                        new_el = etree.fromstring('<item></item>')
                        new_el.text = text
                        # Find parent
                        array_name=name_parts[0]
                        parent = root.xpath("string-array[@name='%s']" % array_name)
                        if len(parent)==0:
                            # Not found - create a new array element
                            parent = etree.fromstring('<string-array name="%s"></string-array>' % array_name)
                            parent.append(new_el)
                            new_el = parent
                            parent = root
                        else:
                            parent = parent[0]
                    elif name_parts[1] == 'P':
                        # plurals
                        new_el = etree.fromstring('<item quantity="%s"></item>' % name_parts[2])
                        new_el.text = text
                        # Find parent
                        plural_name=name_parts[0]
                        parent = root.xpath("plurals[@name='%s']" % plural_name)
                        if len(parent)==0:
                            print "creating plurals el ",name_parts
                            parent = etree.fromstring('<plurals name="%s"></plurals>' % plural_name)
                            parent.append(new_el)
                            parent = root
                        else:
                            parent = parent[0]
                # make sure we have a known resource
                if parent is None or new_el is None:
                    raise RuntimeException("Bad string type: %s" % res['name'])
                # Make the necessary change
                parent.append(new_el)
                # Bail out
                indent(root)
                out = open(localized_filename, 'w')
                out.write(etree.tostring(root,encoding='UTF-8'))
                out.close()
