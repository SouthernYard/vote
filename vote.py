import requests
import time
import json
import threading


class Vote(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
            'Connection': 'keep - alive',
            'Accept': 'application / json, text / plain, * / *',
            'Accept - Language': 'zh - CN, zh;q = 0.9, en;q = 0.8',
            'Accept - Encoding': 'gzip, deflate, br',
            'Host': 'www.xfz.cn',
            'Sec - Fetch - Mode': 'cors',
            'Sec - Fetch - Site': 'same - origin',
            'X - Requested - With': 'XMLHttpRequest'
        }
        self.url_1 = 'http://api.xiaoxiangdaili.com/app/shortProxy/getIp?appKey=509769175288664064&appSecret=OFcLPgFv&cnt=&wt=json'
        self.url_2 = 'http://api.xiaoxiangdaili.com/app/shortProxy/getIp?appKey=509769059530067968&appSecret=NP7vstsv&cnt=&wt=json'
        self.not_enough = True

    def sendReq(self):
        if self.vote(self.url_1):
            return True
        elif self.vote(self.url_2):
            return True
        else:
            return False

    def vote(self, url_get_ip):
        url = 'https://xxxx/api/vote'
        s = requests.Session()
        ip_port = self.getHttpServer(url_get_ip)
        if ip_port:
            while True:
                try:
                    time.sleep(2)
                    proxies = {
                        "http": "http://{}".format(ip_port), "https": "https://{}".format(ip_port)
                    }
                    res = s.get(url, headers=self.headers, proxies=proxies, timeout=10)
                    res.encoding = 'gb2312'
                    rep_dict = json.loads(res.content.decode())
                    print(f"票数:{rep_dict['data']['count']} ===> 排名: {rep_dict['data']['rank']}")
                    if rep_dict['data']['rank'] == 3:
                        self.not_enough = False
                        break
                    if rep_dict['data']['msg'] == 'need_captcha':
                        print('验证码校验，准备换IP')
                        return False
                except:
                    print('投票有点小问题，pass')
                    return False
        else:
            return False

    def getHttpServer(self, url):

        res = requests.get(url, timeout=4)
        res.encoding = 'gb2312'
        try:
            rep_dict = json.loads(res.content.decode())
            if rep_dict['success'] and rep_dict['code'] == 200:
                ip = rep_dict['data'][0]['ip']
                port = rep_dict['data'][0]['port']
                return f"{ip}:{port}"
            return None
        except:
            print("换IP，休息5秒")
            time.sleep(5)


if __name__ == '__main__':
    vote = Vote()

    while True:
        if vote.not_enough:
            vote.sendReq()
        else:
            break
