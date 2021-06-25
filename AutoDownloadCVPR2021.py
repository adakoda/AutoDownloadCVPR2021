# -*- coding: utf-8 -*-
"""
@author: 51takahashi
"""

import os
import time
import urllib.robotparser

import requests

conf = 'CVPR2021'
header = 'http://openaccess.thecvf.com/'


def name_check(name):
    name = name.replace('?', '')
    name = name.replace(':', '')
    name = name.replace('*', '')
    name = name.replace('/', ' or ')
    return name


def get_crawl_delay_sec(url, fetch_url):
    crawl_delay_sec = -1
    rp = urllib.robotparser.RobotFileParser()
    robots_url = url + 'robots.txt'
    rp.set_url(robots_url)
    rp.read()
    can_fetch = rp.can_fetch('*', fetch_url)
    if can_fetch:
        crawl_delay = rp.crawl_delay("*")
        if crawl_delay is None:
            crawl_delay_sec = 15
        else:
            crawl_delay_sec = crawl_delay
    return crawl_delay_sec


def main():
    if not os.path.exists(conf):
        os.mkdir(conf)
    crawl_delay_sec = get_crawl_delay_sec(header, header + conf)
    if crawl_delay_sec == -1:
        exit()
    r = requests.get(header + conf,
                     headers={'User-Agent': 'AutoDownloadCVPR2021'},
                     params={'day': 'all'})
    txt = r.text
    lines = txt.split('\n')
    cnt = 0
    for line in lines:
        if line.find('<dt class="ptitle">') > -1:
            pdfname = conf + '/' + name_check(line.split('>')[3].split('<')[0]) + '.pdf'
            cnt += 1
        if len(line) > 0:
            if line[0] == '[':
                print(str(cnt) + ':' + pdfname)
                if not os.path.exists(pdfname):
                    url = header + line.split('"')[1]
                    r = requests.get(url)
                    f = open(pdfname, 'wb')
                    f.write(r.content)
                    f.close()
                    time.sleep(crawl_delay_sec)


if __name__ == '__main__':
    main()
