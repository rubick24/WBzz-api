import spider
import json
from configparser import ConfigParser
from flask import Flask,request
app = Flask(__name__)


cfg = ConfigParser()
cfg.read('.env')
username = cfg.get('account','username')
password = cfg.get('account','password')
count_limit = int(cfg.get('other','count-limit'))

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/uid/<uid>', methods=['GET'])
def wbzzapi(uid):
    uid = uid.strip()
    if not uid:
        return json.dumps({
            'error': 1,
            'msg': 'uid is required'
        })

    con = spider.login(username, password)
    user = spider.profile(con, uid)

    if 'uid' not in user.keys():
        return json.dumps({
            'error': 2,
            'msg': 'user uid {} not exist'.format(uid)
        })

    if int(user['fans_count']) > count_limit or int(user['follow_count']) > count_limit:
        return json.dumps({
            'error': 3,
            'msg': 'user fans({}) or follows({}) count limit exceed'.format(user['fans_count'], int(user['follow_count']))
        })

    res = spider.crawl(con, uid)
    with_addr = request.args.get('with_addr', '')

    if with_addr and int(with_addr) is 1:
        res = spider.with_addr(con, res)

    return json.dumps({
        'error': 0,
        'data': {
            'user': user,
            'circle': res
        }
    })



@app.route('/api/name/<name>', methods=['GET'])
def search_user(name):
    name = name.strip()
    if not name:
        return json.dumps({
            'error': 2,
            'msg': 'name is required'
        })

    con = spider.login(username, password)
    res = spider.search_by_name(con, name)
    with_addr = request.args.get('with_addr', '')

    if with_addr and int(with_addr) is 1:
        res = spider.with_addr(con, res)

    if len(res) < 1:
        return json.dumps({
            'error': 1,
            'msg': 'empty result'
        })

    return json.dumps({
        'error': 0,
        'data': res
    })