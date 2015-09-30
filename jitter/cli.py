from __future__ import print_function
import sys
import click
import json
import requests
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
            print(resp.text)
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
