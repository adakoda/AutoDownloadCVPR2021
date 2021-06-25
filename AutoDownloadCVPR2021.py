# -*- coding: utf-8 -*-
"""
contributors:
    [51takahashi/AutoDownloadICCV2015](https://github.com/51takahashi/AutoDownloadICCV2015)
    [S\-aiueo32/AutoDownloadCVPR2019](https://github.com/S-aiueo32/AutoDownloadCVPR2019)
    [contaconta/AutoDownloadCVPR2020](https://github.com/contaconta/AutoDownloadCVPR2020)
    [adakoda/AutoDownloadCVPR2021](https://github.com/adakoda/AutoDownloadCVPR2021/)
"""

import os
import re
import time
import urllib.robotparser
from typing import List

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

YEAR = '2021'

CONF_NAME = 'CVPR' + YEAR
APP_NAME = 'AutoDownload' + CONF_NAME
BASE_URL = 'http://openaccess.thecvf.com/'
CRAWL_DELAY_SEC = 15


def get_crawl_delay_sec(url: str, fetch_url: str) -> int:
    crawl_delay_sec = -1
    rp = urllib.robotparser.RobotFileParser()
    robots_url = url + 'robots.txt'
    rp.set_url(robots_url)
    rp.read()
    can_fetch = rp.can_fetch('*', fetch_url)
    if can_fetch:
        crawl_delay = rp.crawl_delay("*")
        if crawl_delay is None:
            crawl_delay_sec = CRAWL_DELAY_SEC
        else:
            crawl_delay_sec = crawl_delay
    return crawl_delay_sec


def validate_filename(name: str) -> str:
    return re.sub(r'[\\:*?"<>|]+', '', name).replace('/', ' or ')


def get_pdf_filename_list_from(soup):
    pdf_filename_list = []
    dt_items = soup.find_all('dt', {'class': 'ptitle'})
    for dt_item in dt_items:
        paper_title = dt_item.find('a').text
        pdf_filename = CONF_NAME + '/' + validate_filename(paper_title) + '.pdf'
        pdf_filename_list.append(pdf_filename)
    return pdf_filename_list


def get_pdf_url_list_from(soup: BeautifulSoup) -> List:
    a_pdf_items = soup.find_all('a', text='pdf')
    return [BASE_URL.strip('/') + a_pdf_item.get('href') for a_pdf_item in a_pdf_items]


def get_pdf_list() -> List:
    r = requests.get(
        BASE_URL + CONF_NAME,
        headers={'User-Agent': APP_NAME},
        params={'day': 'all'})
    soup = BeautifulSoup(r.text, 'html.parser')
    pdf_filename_list = get_pdf_filename_list_from(soup)
    pdf_url_list = get_pdf_url_list_from(soup)
    return list(zip(pdf_filename_list, pdf_url_list))


def print_pdf_list(pdf_list: List) -> None:
    for i, (pdf_filename, pdf_url) in enumerate(pdf_list, start=1):
        print(f'[{i}] {pdf_filename} | {pdf_url}')


def download_pdf(pdf_list: List) -> None:
    for (pdf_filename, pdf_url) in tqdm(pdf_list, ncols=60):
        if not os.path.exists(pdf_filename):
            r = requests.get(pdf_url)
            with open(pdf_filename, 'wb') as f:
                f.write(r.content)
            time.sleep(CRAWL_DELAY_SEC)


def main():
    crawl_delay_sec = get_crawl_delay_sec(BASE_URL, BASE_URL + CONF_NAME)
    if crawl_delay_sec == -1:
        exit()

    os.makedirs(CONF_NAME, exist_ok=True)
    pdf_list = get_pdf_list()
    print_pdf_list(pdf_list)
    download_pdf(pdf_list)


if __name__ == '__main__':
    main()
