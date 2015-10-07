from __future__ import print_function
import sys
import click
import json
import csv
import requests
import urllib
from hashlib import sha1
import hmac
import time

import android

def get_token(secret,userid=None):

    if userid is None:
        msg = tohash = "%08x" % time.time()
    else:
        msg = ""
        tohash = userid
    hashed = hmac.new(secret,tohash,sha1)
    hashed = hashed.digest().encode('hex')
    return msg + hashed

@click.group()
def entrypoint():
    pass

@entrypoint.command()
@click.option('--variant', default='android', help='resource collection method')
@click.option('--output', help='filename to write output to (stdout if omitted)')
@click.option('--rootdir', help='where to look for resource files ("." if omitted)',default=".")
def pack(variant,output,rootdir):
    "Prepare upload pack for JITT"
    pack = globals().get(variant).create_pack(rootdir)
    if output is None:
        output = sys.stdout
    else:
        output = file(output,'w')
    json.dump(pack,output)

@entrypoint.command()
@click.argument('apikey')
@click.argument('secret')
@click.option('--packfile', help='upload pack file name (will read from stdin if omitted)')
@click.option('--server', help='JITT server to upload data to', default='http://jitt.io')
def upload(apikey,secret,packfile,server):
    "upload pack to JITT Server"
    if packfile is None:
        packfile = sys.stdin
    else:
        packfile = file(packfile)
    token = get_token(secret.encode('utf8'))
    url = server.rstrip('/') + '/api/upload'
    try:
        resp = requests.post(url,params={'apikey':apikey,'token':token},data=packfile.read())
        if resp.status_code == 200:
            resp = resp.json()
            if resp['success']:
                print("Successfully uploaded %d strings to JITT server." % resp['processed'])
                print("Once JITT process your upload, you should be able to see them at %s/#/resources/%s" % (server,apikey))
                print("(Be patient - it might take a few minutes to update on the server)")
            else:
                print("Some error occurred... got response %r" % resp)
        else:
            print('Error %d: %s' % (resp.status_code,resp.reason),file=sys.stderr)
    except Exception,e:
        print(e,file=sys.stderr)

@entrypoint.command()
@click.argument('apikey')
@click.argument('secret')
@click.option('--packfile', help='download pack file name (will write to stdout if omitted)')
@click.option('--server', help='JITT server to download data from', default='http://jitt.io')
def download(apikey,secret,packfile,server):
    "download pack from JITT Server"
    if packfile is None:
        packfile = sys.stdin
    else:
        packfile = file(packfile)
    token = get_token(secret.encode('utf8'))
    url = server.rstrip('/') + '/api/download'
    try:
        resp = requests.get(url,params={'apikey':apikey,'token':token})
        if resp.status_code == 200:
            print(resp.text)
        else:
            print('Error %d: %s' % (resp.status_code,resp.reason),file=sys.stderr)
    except Exception,e:
        print(e,file=sys.stderr)

@entrypoint.command()
@click.option('--variant', default='android', help='resource collection method')
@click.option('--input', help='filename to read input from (stdin if omitted)')
@click.option('--rootdir', help='where to look for resource files to update ("." if omitted)',default=".")
def unpack(variant,input,rootdir):
    "Merge translated pack from JITT into existing resource files"
    if input is None:
        input = sys.stdin
    else:
        input = file(input)
    pack = json.load(input)
    globals().get(variant).process_pack(rootdir,pack)

@entrypoint.command()
@click.argument('apikey')
@click.argument('secret')
@click.argument('userid')
@click.argument('locale')
@click.option('--server', help='JITT server to upload data to', default='http://jitt.io')
def link(apikey,secret,userid,locale,server):
    "Get translation link for a user"
    token = get_token(secret.encode('utf8'),userid)
    server = server.rstrip('/')
    url = '%s/#/start/%s/%s/%s/%s' % (server,apikey,locale,token,userid)
    print(url)

@entrypoint.group()
def status():
    "Get status on resources and users"
    pass

def flatten(recs,path):

    def copy_dict(rec):
        out = {}
        for k,v in rec.items():
            if type(v) is dict:
                for k1,v1 in copy_dict(v).items():
                    out["%s.%s" % (k,k1)] = v1
            elif type(v) is list:
                pass
            else:
                if type(v) is unicode:
                    v = v.encode('utf8')
                out[k] = v
        return out

    for rec in recs:
        if len(path) > 0:
            first = path[0]
            rest = path[1:]
            divein = rec.get(first,[])
            if first in rec:
                del rec[first]
            for inner in flatten(divein,rest):
                out = copy_dict(rec)
                for k,v in inner.items():
                    out["%s.%s" % (first,k)] = v
                yield out
        else:
            out = copy_dict(rec)
            yield out

@status.command()
@click.argument('apikey')
@click.argument('secret')
@click.option('--server', help='JITT server to fetch data from', default='http://jitt.io')
@click.option('--format', help='Output format (csv/json), default is json', default='json')
@click.option('--output', help='Output filename, default is stdout')
def resources(apikey,secret,server,format,output=None):
    "Get app's resource status"
    token = get_token(secret.encode('utf8'))
    fileinfo = requests.get('%s/api/admin/files/%s' % (server,apikey), {'token':token}).json()
    files = fileinfo['files'].keys()
    locales = fileinfo['locales']
    res = []
    for fn in files:
        for locale in locales:
            resources = requests.get('%s/api/admin/resources/%s/%s/%s' % (server,apikey,locale,urllib.quote_plus(fn)), {'token':token}).json()
            for resource in resources:
                res.append({u'filename':fn,'resources':resources})
    if output is None:
        output = sys.stdout
    else:
        output = open(output,"w")
    if format == 'json':
        json.dump(res,output)
    elif format == "csv":
        records = flatten(res,['resources','suggestions'])
        writer=csv.DictWriter(output,[
                     u'filename',
                     u'resources.resource_id',
                     u'resources.text',
                     u'resources.context',
                     u'resources.priority',
                     u'resources.created_at',
                     u'resources.stats.last_suggestion_added',
                     u'resources.stats.skipped',
                     u'resources.stats.unclear',
                     u'resources.stats.weight',
                     u'resources.suggestions.created_at',
                     u'resources.suggestions.locale',
                     u'resources.suggestions.text',
                     u'resources.suggestions.score',
                     ],extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)

@status.command()
@click.argument('apikey')
@click.argument('secret')
@click.option('--server', help='JITT server to fetch data from', default='http://jitt.io')
@click.option('--format', help='Output format (csv/json), default is json', default='json')
@click.option('--output', help='Output filename, default is stdout')
def users(apikey,secret,server,format,output):
    "Get app's user status"
    token = get_token(secret.encode('utf8'))
    users = requests.get('%s/api/admin/users/%s' % (server,apikey), {'token':token}).json()
    if output is None:
        output = sys.stdout
    else:
        output = open(output,"w")
    if format == 'json':
        json.dump(users,output)
    elif format == 'csv':
        records = flatten(users,['localeStats'])
        writer=csv.DictWriter(output,[u'userid',
                     u'created_at',
                     u'last_activity',
                     u'stats.approved',
                     u'stats.received',
                     u'stats.served',
                     u'stats.translated',
                     u'localeStats.locale',
                     u'localeStats.approved',
                     u'localeStats.received',
                     u'localeStats.served',
                     u'localeStats.translated',
                     ],extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)
