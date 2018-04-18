import requests
import base64
import re
import json

def start_session():
    return requests.Session()

def login(session, username, password):
    su = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    postData = {
        'entry': 'sso',
        'gateway': '1',
        'savestate': '30',
        'userticket': '0',
        'vsnf': '1',
        'su': su,
        'service': 'sso',
        'sp': password,
        'encoding': 'UTF-8',
        'cdult': '3',
        'returntype': 'TEXT',
    }
    loginURL = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
    res = session.post(loginURL, data = postData)
    info = res.json()
    #print(info)
    if info["retcode"] == "0":
        print("登录成功")
        ret = session.get(info['crossDomainUrlList'][0])
        return True
        #print(ret.text)
    else:
        print("登录失败，原因： {}".format(info["reason"]))
        return False



def profile(session, query_id):
    profile_url = 'https://m.weibo.cn/api/container/getIndex?uid={}&containerid=100505{}'
    addr_url = 'https://weibo.com/p/100505{}/info'
    user = {}
    try:
        res = session.get(profile_url.format(query_id, query_id)).json()
        #print(res)
        if 'userInfo'in res['data'].keys():
            resu = res['data']['userInfo']
            user['uid'] = resu['id']
            user['screen_name'] = resu['screen_name']
            user['gender'] = resu['gender']
            user['description'] = resu['description']
            user['profile_image_url'] = resu['profile_image_url']
            user['fans_count'] = resu['followers_count']
            user['follow_count'] = resu['follow_count']
    except Exception as e:
        print(e)
        return {}

    if 'uid' in user.keys():
        response = session.get(addr_url.format(query_id))
        if response.status_code is 200:
            reArr = re.findall(r'pt_detail\\\"\>(.+?)\<\\\/span', response.text)
            if len(reArr)>1 and reArr[1]:
                user['addr'] = reArr[1]

    return user


def crawl(session, query_id):
    fans_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{}&type=all&since_id={}'
    followers_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{}&page={}'

    followers_result = []
    result = []

    since_id = 1
    while True:
        res = session.get(followers_url.format(query_id, str(since_id)))
        print(res.text)
        res_json = res.json()
        if not len(res_json['data']['cards'])>0:
            break
        for card in res_json['data']['cards']:
            if 'card_group' in card.keys():
                for user in card['card_group']:
                    if 'user' in user.keys():
                        followers_result.append(user['user']['id'])
        since_id += 1
    page = 1
    while True:
        res = session.get(fans_url.format(query_id, str(page)))
        res_json = res.json()
        if not len(res_json['data']['cards'])>0:
            break
        for card in res_json['data']['cards']:
            if 'card_group' in card.keys():
                for user in card['card_group']:
                    if 'user' in user.keys() and user['user']['id'] in followers_result:
                        result.append({
                            'uid': user['user']['id'],
                            'screen_name': user['user']['screen_name'],
                            'gender': user['user']['gender'],
                            'description': user['user']['description'],
                            'profile_image_url': user['user']['profile_image_url'],
                            'fans_count': user['user']['followers_count'],
                            'follow_count': user['user']['follow_count']
                        })
                        print(user['user']['id'],user['user']['screen_name'])
        page += 1

    return result


def search_by_name(session, query_name):
    #containerid: 100103type=3&q=query_name&t=0
    query_url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D3%26q%3D{}%26t%3D0&&page={}'

    result = []
    page = 1
    while True:
        res = session.get(query_url.format(query_name, str(page)))
        res_json = res.json()
        if not len(res_json['data']['cards'])>0:
            break
        for card in res_json['data']['cards']:
            if 'card_group' in card.keys():
                for user in card['card_group']:
                    if 'user' in user.keys():
                        result.append({
                            'uid': user['user']['id'],
                            'screen_name': user['user']['screen_name'],
                            'gender': user['user']['gender'],
                            'description': user['user']['description'],
                            'profile_image_url': user['user']['profile_image_url'],
                            'fans_count': user['user']['followers_count'],
                            'follow_count': user['user']['follow_count']
                        })
                        print(user['user']['id'],user['user']['screen_name'])
        page += 1

    return result


def with_addr(session, result):
    addr_url = 'https://weibo.com/p/100505{}/info'
    for user in result:
        response = session.get(addr_url.format(user['uid']))
        if response.status_code is 200:
            reArr = re.findall(r'pt_detail\\\"\>(.+?)\<\\\/span', response.text)
            if len(reArr)>1 and reArr[1]:
                user['addr'] = reArr[1]
    return result

if __name__ == '__main__':
    man = """
Usage:
    session  start_session()
       bool  login(session, username, password),
  user_list  profile(session, query_id),
       user  search_by_name(session, query_name),
  user_list  with_addr(session, user_list)
        """
    print(man)


# foo = [{'id':1,'name':'a'},{'id':2,'name':'b'}]
# any(d['id'] == 3 for d in foo)