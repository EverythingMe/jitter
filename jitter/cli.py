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
@click.option('--rootdir', help='where to look for resource files ("." if omitted)')
def pack(variant,output,rootdir):
    "Prepare upload pack for JITT"
    pack = globals().get(variant).make_pack(rootdir)
    if output is None:
        output = sys.stdout
    else:
        output = file(output,'w')
    output.write(json.dumps(pack))

@entrypoint.command()
@click.argument('apikey')
@click.argument('secret')
@click.option('--packfile', help='upload pack (will take from stdin if omitted)')
@click.option('--server', help='JITT server to upload data to', default='http://jitt-v2.appspot.com')
def upload(apikey,secret,packfile,server):
    "upload pack to JITT Server"
    if packfile is None:
        packfile = sys.stdin
    else:
        packfile = file(packfile)
    token = get_token(secret.encode('utf8'))
    url = server + '/api/upload'
    resp = requests.post(url,params={'apikey':apikey,'token':token},data=packfile.read())
    print resp.text

@entrypoint.command()
@click.argument('apikey')
@click.argument('secret')
@click.argument('userid')
@click.argument('locale')
@click.option('--server', help='JITT server to upload data to', default='http://jitt-v2.appspot.com')
def link(apikey,secret,userid,locale,server):
    "Get translation link for a user"
    token = get_token(secret.encode('utf8'),userid)
    server = server.rstrip('/')
    url = '%s/#/start/%s/%s/%s/%s' % (server,apikey,locale,userid,token)
    print url
