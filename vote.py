#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import time
import json
import threading
import datetime


class Vote(object):
    def __init__(self, person_id):
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
        self.proxy_server_url_1 = 'http api url'
        self.proxy_server_url_2 = self.proxy_server_url_1
        self.info_url = f"url1"
        self.vote_url = f"url2"
        self.all_info = 'info url'
        self.not_enough = True

    def send_req(self, vote_num_required=60000, rank_required: int = 4):
        if self.vote(self.proxy_server_url_1, vote_num_required, rank_required):
            return True
        elif self.vote(self.proxy_server_url_2, vote_num_required, rank_required):
            return True
        else:
            return False

    def vote(self, url_get_ip, vote_num_required, rank_required: int = 4):
        url = self.vote_url
        s = requests.Session()
        ip_ports = self.get_http_server(url_get_ip)
        if ip_ports:
            while True:
                try:
                    for ip_port in ip_ports:
                        time.sleep(0.3)
                        proxies = {
                            "http": "http://{}".format(ip_port), "https": "https://{}".format(ip_port)
                        }
                        res = s.get(url, headers=self.headers, proxies=proxies, timeout=10)
                        s.close()
                        res.encoding = 'gb2312'
                        rep_dict = json.loads(res.content.decode())
                        print(f"{threading.currentThread().getName()} | 票数:{rep_dict['data']['count']} ===> "
                              f"排名: {rep_dict['data']['rank']}")
                        if rep_dict['data']['rank'] <= rank_required and rep_dict['data']['count'] > vote_num_required:
                            self.not_enough = False
                            break
                        if rep_dict['data']['msg'] == 'need_captcha':
                            print('验证码校验，准备换IP')
                            return False
                    if not self.not_enough:
                        break

                except Exception as e:
                    print(e)
                    print('投票有点小问题，pass')
                    return False
        else:
            return False

    @staticmethod
    def get_http_server(url):
        res = requests.get(url, timeout=4)
        res.encoding = 'gb2312'
        try:
            rep_dict = json.loads(res.content.decode())
            ip_list = []
            if rep_dict['success'] and rep_dict['code'] == 200:
                for data in rep_dict['data']:
                    ip = data['ip']
                    port = data['port']
                    ip_list.append(f"{ip}:{port}")
            return ip_list
        except:
            print("换IP，休息5秒")
            time.sleep(5)

    def get_rank(self):
        res = requests.get(self.info_url, timeout=4)
        try:
            rep_dict = json.loads(res.content.decode())
            if rep_dict['code'] == 200:
                return rep_dict['data']['rank']
            return None
        except:
            print("无法获取当前排名")
        return -1

    def get_all_rank(self):
        res = requests.get(self.all_info, timeout=4)
        try:
            rep_dict = json.loads(res.content.decode())
            list = []
            for data in rep_dict['data']:
                list.append(data['count'])
            list.sort(reverse=True)
            return list
        except:
            print("无法获取所有人的排名")
        return None


class GetNameId(object):
    def __init__(self):
        self.all_info = 'Api URL'

    def get_name_id(self):
        res = requests.get(self.all_info, timeout=4)
        try:
            rep_dict = json.loads(res.content.decode())
            local_name_id_dict = {}

            for data in rep_dict['data']:
                local_name_id_dict[data['name']] = data['id']
            return local_name_id_dict
        except:
            print("无法获取名字和对应的ID")
        return None


class Execute(object):
    def __init__(self, name, rank_required):
        self.name = name
        self.rank_required = rank_required

    def to_vote(self):
        name_id_dict = GetNameId().get_name_id()
        person_id = int(name_id_dict[self.name])
        vote = Vote(person_id)
        rank_list = vote.get_all_rank()
        target_num = (rank_list[self.rank_required - 1] + rank_list[self.rank_required]) / 2
        while True:
            try:
                if vote.not_enough:
                    vote.send_req(rank_required=self.rank_required, vote_num_required=target_num)
                else:
                    if vote.get_rank() > self.rank_required and vote.get_rank() != 1:
                        vote.not_enough = True
                    print('======等待中，无需刷票======')
                    time.sleep(10)
            except:
                pass


class VoteThread(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        print('线程: ' + str(self.thread_id))
        Execute('人名', 1).to_vote()


def time_up(target_hour, target_min):
    now = datetime.datetime.now()
    return target_hour == now.hour and target_min == now.minute


if __name__ == '__main__':
    while not time_up(8, 45):
    	# 定时任务， 到点执行
        print(f"任务还未开始执行，请等待:{datetime.datetime.now()}")
        time.sleep(10)

    thread_num = 2
    for i in range(0, thread_num):
        thread = VoteThread(i, f"Thread-{i}", i)
        thread.start()