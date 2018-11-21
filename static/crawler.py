#!/usr/bin/python3.6
from urllib import request
import urllib
import requests
import re
import zlib
from bs4 import BeautifulSoup
import os
import random
import json
import time


class Spider(object):
    def __init__(self, url):
        self.base_url = url
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "pvp.qq.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,    like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        }
        self.hero_id = {}
        self.hero_list_url = {}
        self.hero_info = {}
        self.hero_types_list = ['战士', '法师', '坦克', '刺客', '射手', '辅助']

    def getHtml(self, url, now_headers, encode='gbk'):
        try:
            html = requests.get(url, headers=now_headers)
            html.encoding = encode
            return html.text
        except Exception as e:
            print(e)
            print("Get html failed. Url: %s" % url)
            return None

    def getCookies(self):
        self.getHtml("http://pvp.qq.com/web201605/herolist.shtml",
                     spider.headers)

    def getHeroList(self):
        now_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'pvp.qq.com',
            'Referer': 'http://pvp.qq.com/web201605/herolist.shtml',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        text = self.getHtml(
            "http://pvp.qq.com/web201605/js/herolist.json", now_headers, 'utf8')
        try:
            pattern = re.compile('"ename":.*?,')
            urls = pattern.findall(text)
            pattern = re.compile('"cname":.*?,')
            names = pattern.findall(text)
            pattern = re.compile('"hero_type":.*?,')
            hero_types = pattern.findall(text)

            for i in range(len(urls)):
                self.hero_list_url[names[i][8:-1]] = "http://pvp.qq.com/web201605/herodetail/" + \
                    urls[i][8:-1] + ".shtml"
                self.hero_id[names[i][8:-1]] = urls[i][8:-1]
                now_type_index = int(hero_types[i][12:-1]) - 1
                self.hero_info[names[i][8:-1]] = {
                    "type": self.hero_types_list[now_type_index]
                }
        except Exception as e:
            print(e)
            print("Get HeroList Failed")

    def getHeroInfo(self, hero_name):
        try:
            print("Get %s information" % hero_name)

            hero_url = self.hero_list_url[hero_name]
            text = self.getHtml(hero_url, self.headers)
            soup = BeautifulSoup(text, 'html5lib')

            # background
            background = soup.find_all(
                'div', class_='zk-con1')[0].attrs["style"].split("'")[1]
            self.hero_info[hero_name]['background'] = background[2:]

            # avator
            heroId = self.hero_id[hero_name]
            self.hero_info[hero_name]['avator'] = "game.gtimg.cn/images/yxzj/img201606/heroimg/" +\
                heroId + "/" + heroId + ".jpg"

            # title
            title = soup.find_all('h3', class_='cover-title')[0].next
            self.hero_info[hero_name]['title'] = title

            # abilities
            tag_list = ['surviveAbility', 'attackAbility',
                        'skillAbility', 'difficulty']
            tag_values = soup.find_all('i', class_='ibar')
            for i, tag in enumerate(tag_list):
                now_value = int(tag_values[i].attrs['style'][6:-1]) / 10
                self.hero_info[hero_name][tag] = now_value

            # story
            story = soup.find_all('div', class_='pop-bd')[0].get_text()
            self.hero_info[hero_name]['story'] = story.strip()

            # skills
            skills = soup.find_all('div', class_='show-list')
            self.hero_info[hero_name]['skills'] = []
            for index, skill in enumerate(skills):
                temp = skill.find_all(
                    'p', class_='skill-name')[0].get_text().split('：')
                name = temp[0].split('冷却值')[0]
                if len(name) > 0:
                    skillInfo = {}
                    skillInfo['name'] = name
                    consumption = temp[1].split('消耗')[0]
                    skillInfo['consumption'] = consumption
                    cdTime = temp[2]
                    skillInfo['cdTime'] = cdTime
                    detail = skill.find_all(
                        'p', class_='skill-desc')[0].get_text()
                    skillInfo['detail'] = detail
                    intro = skill.find_all(
                        'div', class_='skill-tips')[0].get_text()
                    skillInfo['intro'] = intro
                    if index == 4:
                        avator = soup.find_all('ul', class_='skill-u1')[0].find_all('li')[index].attrs['data-img']
                    else:
                        avator = soup.find_all(
                            'ul', class_='skill-u1')[0].find_all('img')[index].attrs['src']
                    skillInfo['avator'] = avator[2:]
                    self.hero_info[hero_name]['skills'].append(skillInfo)

        except Exception as e:
            print(e)
            print("Get %s infomation failed" % hero_name)

    def generateXML(self):
        try:
            print("Generate XML")
            with open("Heros.xml", 'w', encoding='utf-8') as f:
                f.writelines("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<heros>\n")
                for hero_name in self.hero_info:
                    now_line = '\t<hero>\n\t<name>%s</name>\n\t<background>%s</background>\n\t<avator>%s</avator>\n\t<title>%s</title>\n\t\t<position>%s</position>\n\t\t<surviveAbility>%d</surviveAbility>\n\t\t<attackAbility>%d</attackAbility>\n\t\t<skillAbility>%d</skillAbility>\n\t\t<difficulty>%d</difficulty>\n\t\t<story>\n\t\t\t%s\n\t\t</story>\n\t\t<skills>\n' \
                        % (hero_name, self.hero_info[hero_name]['background'], self.hero_info[hero_name]['avator'],
                            self.hero_info[hero_name]['title'], self.hero_info[hero_name]['type'],
                            self.hero_info[hero_name]['surviveAbility'], self.hero_info[hero_name]['attackAbility'],
                            self.hero_info[hero_name]['skillAbility'], self.hero_info[hero_name]['difficulty'],
                            self.hero_info[hero_name]['story'].replace('<', ''))

                    for skill in self.hero_info[hero_name]['skills']:
                        now_line += '\t\t\t<skill>\n\t\t\t\t<name>%s</name>\n\t\t\t\t<avator>%s</avator>\n\t\t\t\t<detail>%s</detail>\n\t\t\t\t<intro>%s</intro>\n\t\t\t\t<cdTime>%s</cdTime>\n\t\t\t\t<consumption>%s</consumption>\n\t\t\t</skill>\n' \
                            % (skill['name'], skill['avator'], skill['detail'],
                                skill['intro'], skill['cdTime'], skill['consumption'])

                    now_line += '\t\t</skills>\n\t</hero>\n'
                    f.writelines(now_line)
                f.writelines("</heros>\n")
            print("done")
        except Exception as e:
            print(e)
            print("Generate XML failed.")

    def getAllHeroInfo(self):
        self.getCookies()
        self.getHeroList()
        # print(spider.hero_list_url)
        try:
            for hero_name in self.hero_list_url:
                self.getHeroInfo(hero_name)
                print("done")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    while True:
        spider = Spider("http://pvp.qq.com/web201605/")
        spider.getAllHeroInfo()
        spider.generateXML()
        time.sleep(3600)
