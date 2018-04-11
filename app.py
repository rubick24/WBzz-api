import spider
import json
from configparser import ConfigParser
from flask import Flask,request
app = Flask(__name__)


cfg = ConfigParser()
cfg.read('.env')
username = cfg.get('account','username')
password = cfg.get('account','password')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/uid/<uid>', methods=['GET'])
def wbzzapi(uid):
    uid = uid.strip()
    if uid:
        con = spider.login(username, password)
        user = spider.profile(con, uid)
        if 'uid' in user.keys():
            res = spider.crawl(con, uid)
            with_addr = request.args.get('with_addr', '')
            if with_addr and int(with_addr) is 1:
                res = spider.with_addr(con, res)
            response = {
                'error': 0,
                'data': {
                    'user': user,
                    'circle': res
                }
            }
        else:
            response = {
                'error': 2,
                'msg': 'user uid {} not exist'.format(uid)
            }
    else:
        response = {
            'error': 1,
            'msg': 'uid is required'
        }

    return json.dumps(response)


@app.route('/api/name/<name>', methods=['GET'])
def search_user(name):
    name = name.strip()
    if name:
        con = spider.login(username, password)
        res = spider.search_by_name(con, name)
        with_addr = request.args.get('with_addr', '')
        if with_addr and int(with_addr) is 1:
            res = spider.with_addr(con, res)

        if len(res) > 0:
            response = {
                'error': 0,
                'data': res
            }
        else:
            response = {
                'error': 1,
                'msg': 'empty result'
            }
    else:
        response = {
            'error': 2,
            'msg': 'name is required'
        }

    return json.dumps(response)