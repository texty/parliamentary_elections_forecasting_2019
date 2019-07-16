#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import re, requests, time
from bs4 import BeautifulSoup
from tqdm import tqdm

PATH_TO_LOCATION_WITH_PROGRAMS = '/home/antek/Desktop/parse_cvk_2019/programs/'

def get_links_for_okrugs():
    request = requests.get('https://www.cvk.gov.ua/pls/vnd2019/wp032pt001f01=919.html')
    request.encoding = 'UTF-8'
    soup = BeautifulSoup(request.content, 'lxml')
    tds = soup.find_all('td', {'class':'td2'})
    okrugs = ['https://www.cvk.gov.ua/pls/vnd2019/' + td.a['href'] for td in tds if td.a is not None]
    return okrugs

def parse_candidates_info(url):
    request = requests.get(url)
    request.encoding = 'UTF-8'
    soup_okrug = BeautifulSoup(request.content, 'lxml')
    cands_table = soup_okrug.find_all('table', attrs = {'class':'t2'})[1]

    info_table = []

    for tr in cands_table.tbody.find_all('tr')[1:]:

        cands_info_dict = {
            'ПІБ':'',
            'Основні відомості':'',
            'Наявність(відсутність) заборгованості зі сплати аліментів':'',
            'Висування':'',
            'Передвиборна програма':'',
            'Дата реєстрації кандидатом':'',
            'Дата та підстава скасування реєстрації кандидата':'',
            'Округ':''
        }

        tds = [td for td in tr.findAll('td')]

        cands_info_dict['ПІБ'] = tds[0].text
        cands_info_dict['Основні відомості'] = tds[1].text
        cands_info_dict['Наявність(відсутність) заборгованості зі сплати аліментів'] = tds[2].text
        cands_info_dict['Висування'] = tds[3].text
        cands_info_dict['Дата реєстрації кандидатом'] = tds[5].text
        cands_info_dict['Дата та підстава скасування реєстрації кандидата'] = tds[6].text
        cands_info_dict['Округ'] = soup_okrug.find('p').text
        if tds[4].find('a') is not None:
            cands_info_dict['Передвиборна програма'] = 'https://www.cvk.gov.ua/pls/vnd2019/' + tds[4].find('a').get('href')

        info_table.append(cands_info_dict)
        time.sleep(1)

    return info_table

def get_csv_with_candidates(info_tables):
    cands_info = pd.concat(info_tables, ignore_index = True)
    cands_info = cands_info[cands_info.columns[::-1]]
    cands_info['Область'] = cands_info['Округ'].str.extract('\(([^)]+)')
    cands_info['Округ'] = cands_info['Округ'].str.extract('(\d+)')
    cands_info['ПІБ'] = [re.sub(r'([Є-ЯҐ]\w+)([Є-ЯҐ]\w+)', r'\1 \2', row) for row in cands_info['ПІБ']]
    return cands_info

def parse_candidates_programs(url):
    request = requests.get(url)
    request.encoding = 'UTF-8'
    soup_okrug = BeautifulSoup(request.content, 'lxml')
#     назва файлу з програмою - ПІБ депутата
    name = pd.read_html(str(soup_okrug),header=0)[5].iloc[:,0][0]
    tds = soup_okrug.find_all('td', {'class':'td3'})
    for td in tds:
        if td.a is not None:
            link = 'https://www.cvk.gov.ua/pls/vnd2019/' + td.a['href']
            response = requests.get(link)
            with open((PATH_TO_LOCATION_WITH_PROGRAMS + name), 'wb') as f:
                f.write(response.content)
            time.sleep(5)

info_tables = []
cands_info = []

okrugs = get_links_for_okrugs()
for okrug in tqdm(okrugs):
    info_tables.append(pd.DataFrame(parse_candidates_info(okrug)))
    # parse_candidates_programs(okrug)
cands_info = get_csv_with_candidates(info_tables)
cands_info.to_csv('output.csv', sep=',')