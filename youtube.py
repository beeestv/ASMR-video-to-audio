#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/15 下午10:05
# @Author  : bestv
# @Site    : 
# @File    : youtube.py
# @Software: PyCharm Community Edition

from __future__ import unicode_literals
import sys, os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import youtube_dl
from concurrent.futures import ThreadPoolExecutor


def load_all_more_button(browser):
    while True:
        try:
            element = browser.find_element_by_class_name('load-more-button')
            element.click()
        except NoSuchElementException:
            print("已点击所有\'加载更多\'")
            break
        except Exception:
            load_all_more_button(browser)


def check_user_exist(browser):
    try:
        browser.find_element_by_class_name('channel-empty-message')
    except NoSuchElementException:
        pass
    else:
        print("用户不存在")
        sys.exit()


def get_page(channal):
    chrome_options = webdriver.ChromeOptions()
    browser = webdriver.Chrome('/Users/koshitakashi/Code/Python/chromedriver', chrome_options=chrome_options)
    browser.get("https://www.youtube.com/user/" + channal + "/videos")
    check_user_exist(browser)
    load_all_more_button(browser)
    print("end load, start analyze")
    return browser.page_source


def extract_links(page):
    bs = BeautifulSoup(page, 'html.parser')
    url = 'https://www.youtube.com'
    link_tags = bs.find_all('a', class_='yt-ui-ellipsis-2')
    links = []
    for link_tag in link_tags:
        link = url + link_tag['href']
        links.append(link)
    return links


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        global count
        count += 1
        print('%d : %d   %s\nDone downloading, now converting ...\n' % (count, total, d['filename']))


def download_and_convert(links, output_template=None, hook=None, logger=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'nocheckcertificate': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': None if logger is None else logger,
        'progress_hooks': [] if hook is None else hook,
        'outtmpl': './video/%(title)s.%(ext)s' if output_template is None else output_template,
    }
    for link in links:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if not was_downloaded(link):
                pool.submit(ydl.download, ([link]))
                record_download(link)


def was_downloaded(link):
    if not os.path.isfile(storage_filename):
        return False
    f = open(storage_filename)
    data = f.read()
    if data.find(link) != -1:
        return True
    return False


def record_download(link):
    f = open(storage_filename, 'a')
    f.write(link + '\n')


count = 0
total = 0
storage_filename = './data.txt'
channals = ['aruru0815', 'jellybeanasmr']
pool = ThreadPoolExecutor(5)
for channal in channals:
    channal_page = get_page(channal)
    video_links = extract_links(channal_page)
    total += len(video_links)
    download_and_convert(video_links, hook=[my_hook], logger=MyLogger(),
                         output_template='/Users/koshitakashi/Documents/ASMR/' + channal + '/%(title)s.%(ext)s')
