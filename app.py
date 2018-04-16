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
def user_profile(uid):
    uid = uid.strip()
    if not uid:
        return json.dumps({
            'msg': 'uid is required'
        }),400

    con = spider.login(username, password)
    user = spider.profile(con, uid)

    if 'uid' not in user.keys():
        return json.dumps({
            'msg': 'user uid {} not exist'.format(uid)
        }),404

    if int(user['fans_count']) > count_limit or int(user['follow_count']) > count_limit:
        return json.dumps({
            'msg': 'user fans({}) or follows({}) count limit exceed'.format(user['fans_count'], int(user['follow_count']))
        }),403

    res = spider.crawl(con, uid)
    with_addr = request.args.get('with_addr', '')

    if with_addr and int(with_addr) is 1:
        res = spider.with_addr(con, res)

    return json.dumps({
        'user': user,
        'circle': res
    }),200



@app.route('/api/name/<name>', methods=['GET'])
def search_user(name):
    name = name.strip()
    if not name:
        return json.dumps({
            'msg': 'name is required'
        }),400

    con = spider.login(username, password)
    res = spider.search_by_name(con, name)
    with_addr = request.args.get('with_addr', '')

    if with_addr and int(with_addr) is 1:
        res = spider.with_addr(con, res)

    if len(res) < 1:
        return json.dumps({
            'msg': 'empty result'
        }),404

    return json.dumps(res),200