from __future__ import unicode_literals
from bs4 import BeautifulSoup
from urllib import request
import sys
import re
import os
import json
import time
import random
import requests
import datetime
import traceback

pwd = os.getcwd()
linkPath = pwd + '\\link\\'
dataPath = pwd + '\\data\\'
proxyPath = pwd + '\\proxy\\'
checkUrl = 'http://httpbin.org/get'
baseUrl = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2019/'
ipFileName = 'ip.json'
provinceFileName = 'province.json'
cityFileName = 'city.json'
countryFileName = 'country.json'
townFileName = 'town.json'
villageFileName = 'village.json'

totalNumber = 0
startTime = ''
endTime = ''

proxies = ''
proxyUrl = 'https://www.xicidaili.com/nn/'
proxyPageSize = 20
proxyPageStart = 1
proxyIpList = []
proxyStime = 0
proxyEtime = 0
proxyHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.107'}
openProxy = True
tries = 10
forceRefresh = False
level = 5

print('\n')


# 格式化显示时间
def getTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())



# 保存Json文件
def saveJsonInfo(data, handler):
    json.dump(data, handler, sort_keys = True, indent = 4, separators = (',', ':'), ensure_ascii = False)



# 创建Json文件
def createJsonFile(name, path):
    print(' ------------------ ( START ) 文件 ( ' + getTime() + ' ) ------------------\n')
    if not os.path.exists(path):
        os.makedirs(path)
        print(' 目录 ( ' + path + ' ) 创建成功\n')
    else:
        print(' 目录 ( ' + path + ' ) 已存在\n')
    if isinstance(name, str):
        file = path + name
        if not os.path.exists(file):
            with open(file, 'w+') as handler:
                saveJsonInfo([], handler)
            handler.close()
            print(' 文件 ( ' + file + ' ) 创建成功\n')
        else:
            print(' 文件 ( ' + file + ' ) 已经存在\n')
    else:
        for i in name:
            file = path + i
            if not os.path.exists(file):
                with open(file, 'w+') as handler:
                    saveJsonInfo([], handler)
                handler.close()
                print(' 文件 ( ' + file + ' ) 创建成功\n')
            else:
                print(' 文件 ( ' + file + ' ) 已经存在\n')
    print(' ------------------ ( END ) 文件 ( ' + getTime() + ' ) ------------------\n\n\n')



# 获取动态代理IP列表
def getIpList():
    print(' ------------------ ( START ) 动态代理IP ( ' + getTime() + ' ) ------------------\n')
    proxyStime = int(time.time())
    ipList = []
    for k in range(proxyPageSize):
        proxyPageNum = str(proxyPageStart + k)
        print(' 开始获取动态代理IP ( 第 ' + proxyPageNum + ' 页 )', end = '')
        soupIpPage = getPageInfo(proxyUrl + proxyPageNum)
        ips = soupIpPage.findAll(re.compile('tr'))
        for i in ips:
            tds = i.findAll(re.compile('td'))
            if(len(tds) > 0):
                for inx, k in enumerate(tds):
                    if inx == 1:
                        ip = k.text
                    if inx == 2:
                        port = k.text
                    if inx == 5:
                        protocol = k.text.lower()
                        break
                if protocol == 'https':
                    ipList.append({
                        'port': protocol,
                        'addr': protocol + '://' + ip + ':' + port
                    })
        print(' - 解析成功\n')
    return ipList



# 保存动态代理IP
def saveDynamicIp(ipList):
    print(' 开始检测动态代理IP的有效性并选取 ( 仅检测 HTTPS 协议 )\n')
    proxyList = []
    flag = False
    n = 0
    for ip in ipList:
        print(' 检测 ' + ip['addr'], end = '')
        proxy = {ip['port']: ip['addr']}
        try:
            response = requests.get(checkUrl, headers = proxyHeaders, proxies = proxy, timeout = 10)
            html = response.text
            if response.status_code == 200:
                proxyList.append(proxy)
                if not flag:
                    flag= True
                n = n + 1
                print(' ( \033[0;32;40m有效\033[0m )\n')
            else:
                print(' ( \033[0;31;40m无效\033[0m )\n')
        except:
            print(' ( \033[0;30;40m无效033[0m )\n')
    if not flag:
        print(' ( \033[0;33;40mNOTICE\033[0m ) 本次获取的动态代理IP都无效，后续将进行无代理访问\n')
    else:
        file = proxyPath + ipFileName
        with open(file, 'r+', encoding = 'utf-8') as handler:
            saveJsonInfo(proxyList, handler)
            print(' 共计 ' + str(n) + ' 条有效代理IP，已存储成功 ( ' + file + ' )\n')
        handler.close()
    proxyEtime = int(time.time())
    print(' ------------------ ( END ) 动态代理IP (' + getTime() + ') ------------------\n\n\n')
    return proxy



# 随机获取动态代理IP
def getRandomIp():
    proxy = ''
    if len(proxyIpList) > 0:
        proxy = random.choice(proxyIpList)
    else:
        file = proxyPath + ipFileName
        with open(file, 'r') as handler:
            data = json.load(handler)
            if len(data) > 0:
                proxy = random.choice(data)
        handler.close()
    return proxy



files = [provinceFileName, cityFileName, countryFileName, townFileName, villageFileName]
createJsonFile(files, linkPath)
createJsonFile(files, dataPath)
createJsonFile(ipFileName, proxyPath)



# 省份
provinceDataList = []
provinceTotalNum = 0
# 城市
cityDataList = {}
cityTotalNum = 0
# 地区
countryDataList = {}
countryTotalNum = 0
# 乡镇
townDataList = {}
townTotalNum = 0
# 社区
villageDataList = {}
villageTotalNum = 0



# 根据URL获取网站信息
def getPageInfo(url, encoding = ''):
    page = ''
    tryNum = 0
    for i in range(tries):
        try:
            if proxies == '':
                response = requests.get(url, headers = proxyHeaders, timeout = 5)
            else:
                response = requests.get(url, headers = proxyHeaders, proxies = proxies, timeout = 10)
            if encoding != '':
                response.encoding = encoding
            if response.status_code == 200:
                page = BeautifulSoup(response.text, 'html.parser')
                break
        except:
            tryNum += 1
            print(' ( \033[0;31;40mERROR\033[0m ) 链接访问超时，再次尝试获取信息 ( ' + getTime() + ' )\n')
            if tryNum >= 5:
                proxies = getRandomIp()
                print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n')
    return page




# 获取省份链接信息并保存
def saveProvinceLink():
    print(' ------------------ ( START ) \033[0;31;40m省份链接\033[0m ( ' + getTime() + ' ) ------------------\n')
    province = []
    file = linkPath + provinceFileName
    global totalNumber
    global provinceTotalNum
    with open(file, 'r+', encoding = 'utf-8') as handler:
        try:
            data = json.load(handler)
            success = False
            if forceRefresh or len(data) <= 0:
                page = getPageInfo(baseUrl + 'index.html', 'gbk')
                if page == '':
                    success = True
                provinces = page.findAll(name = 'tr', attrs = {'class': re.compile('provincetr')})
                for i in provinces:
                    links = i.findAll(name = 'a')
                    for k in links:
                        provinceLink = baseUrl + k['href']
                        provinceName = k.text
                        print(' \033[0;31;40m' + provinceName + '\033[0m', end = ' ')
                        info = {
                            'name': provinceName,
                            'url': provinceLink
                        }
                        province.append(info)
                    provinceTotalNum += 1
                if len(province) > 0:
                    totalNumber += + len(province)
                    handler.seek(0)
                    saveJsonInfo(province, handler)
            else:
                totalNumber = totalNumber + len(data)
                print(' ( \033[0;33;40mNOTICE\033[0m ) 省份链接信息已存在，默认未设置强制更新 ( 可在代码内修改 forceRefresh 值 ) ', end = '')
        except:
            traceback.print_exc()
            if not success:
                print(' \n( \033[0;31;40mERROR\033[0m ) 省份链接信息已存在，但内容存在错误，请检查 ( ' + file + ' )', end = '')
            else:
                print(' \n( \033[0;31;40mERROR\033[0m ) 3次尝试获取省份链接信息失败，强制终止继续执行 ( ' + getTime() + ' )', end = '')
            os._exit(0)
    handler.close()
    print('\n\n ------------------ ( END ) \033[0;31;40m省份链接\033[0m ( ' + getTime() + ' ) ------------------\n\n\n')




# 保存城市链接信息
def saveCityLink():
    print(' ------------------ (START) \033[0;32;40m城市链接\033[0m ( ' + getTime() + ' ) ------------------\n')
    try:
        provinceLinkFile = linkPath + provinceFileName
        cityLinkFile = linkPath + cityFileName
        global totalNumber
        global cityTotalNum
        with open(provinceLinkFile, 'r', encoding = 'utf-8') as provinceLinkFileHandler, open(cityLinkFile, 'r+', encoding = 'utf-8') as cityLinkFileHandler:
            data = json.load(cityLinkFileHandler)
            if forceRefresh or len(data) <= 0:
                proxies = getRandomIp()
                print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n')
                provinceLinkList = json.load(provinceLinkFileHandler)
                cityLinkList = []
                for index, i in enumerate(provinceLinkList):
                    print(' ------ 开始更新 [ \033[0;32;40m' + i['name'] + '\033[0m ] ( ' + getTime() + ' ) ------\n')
                    cityData = getCityLink(cityLinkFileHandler, i['url'], i['name'])
                    for k in cityData:
                        cityLinkList.append(k)
                    print(' ------ 完成更新 [ \033[0;32;40m' + i['name'] + '\033[0m ] ( ' + getTime() + ' ) ------\n\n')
                    if index < len(provinceLinkList):
                        proxies = getRandomIp()
                        print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n\n')
                cityNumber = len(cityLinkList)
                cityTotalNum += cityNumber
                totalNumber += cityNumber
                cityLinkFileHandler.seek(0)
                saveJsonInfo(cityLinkList, cityLinkFileHandler)
            else:
                totalNumber = totalNumber + len(data)
                print(' ( \033[0;33;40mNOTICE\033[0m ) 城市链接信息已存在，默认未设置强制更新 ( 可在代码内修改 forceRefresh 值 )\n')
        cityLinkFileHandler.close()
        provinceLinkFileHandler.close()
    except Exception as e:
        traceback.print_exc()
        print(' \n( \033[0;31;40mERROR\033[0m ) 城市链接信息获取失败，强制终止继续执行 ( ' + getTime() + ' )\n')
        os._exit(0)
    print(' ------------------ ( END ) \033[0;32;40m城市链接\033[0m ( ' + getTime() + ' ) ------------------\n\n\n')




# 获取城市链接信息
def getCityLink(cityFileHandler, link, province):
    page = getPageInfo(link, 'gbk')
    citys = page.findAll(name = 'tr', attrs = {'class': re.compile('citytr')})
    city = []
    provinceCode = ''
    for i in citys:
        links = i.findAll(re.compile('a'))
        for inx, k in enumerate(links):
            cityLink = k['href']
            if(inx == 0):
                cityCode = k.text
            else:
                cityName = k.text
        if(provinceCode == ''):
            provinceShortCode = cityCode[0:2]
            provinceCode = provinceShortCode.ljust(12, '0')
        city.append({
            'name': cityName,
            'code': cityCode,
            'url': baseUrl + cityLink,
            'pcode': provinceCode,
            'pname': province
        })
        if not cityDataList.__contains__(provinceCode):
            cityDataList[provinceCode] = []
        cityDataList[provinceCode].append({
            'code': cityCode,
            'name': cityName,
            'parent': provinceCode
        })
        print(' [ \033[0;32;40m' + province + ' - ' + cityName + '\033[0m ] 数据获取成功\n')
    provinceDataList.append({
        'code': provinceCode,
        'name': province
    })
    return city




# 保存地区链接信息
def saveCountryLink():
    print(' ------------------ ( START ) \033[0;33;40m地区链接\033[0m ( ' + getTime() + ' ) ------------------\n')
    try:
        cityLinkFile = linkPath + cityFileName
        countryLinkFile = linkPath + countryFileName
        global totalNumber
        global countryTotalNum
        with open(cityLinkFile, 'r', encoding = 'utf-8') as cityLinkFileHandler, open(countryLinkFile, 'r+', encoding = 'utf-8') as countryLinkFileHandler:
            data = json.load(countryLinkFileHandler)
            if forceRefresh or len(data) <= 0:
                proxies = getRandomIp()
                print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n')
                cityLinkList = json.load(cityLinkFileHandler)
                countrys = []
                for index, i in enumerate(cityLinkList):
                    print(' ------ 开始更新 [ \033[0;33;40m' + i['pname'] + ' - ' + i['name'] + '\033[0m ] ( ' + getTime() + ' ) ------\n')
                    countryLinkList = getCountryLink(i['url'], i['name'], i['code'], i['pname'])
                    for k in countryLinkList:
                        countrys.append(k)
                    print(' ------ 完成更新 [ \033[0;33;40m' + i['pname'] + ' - ' + i['name'] + '\033[0m ] ( ' + getTime() + ' ) ------\n\n')
                    if index < len(cityLinkList):
                        proxies = getRandomIp()
                        print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n\n')
                countryNumber = len(countrys)
                countryTotalNum += countryNumber
                totalNumber += countryNumber
                countryLinkFileHandler.seek(0)
                saveJsonInfo(countrys, countryLinkFileHandler)
            else:
                totalNumber = totalNumber + len(data)
                print(' ( \033[0;33;40mNOTICE\033[0m ) 地区链接信息已存在，默认未设置强制更新 ( 可在代码内修改 forceRefresh 值 )\n')
        cityLinkFileHandler.close()
        countryLinkFileHandler.close()
    except:
        traceback.print_exc()
        print(' \n( \033[0;31;40mERROR\033[0m ) 地区链接信息获取失败，强制终止继续执行 ( ' + getTime() + ' )\n')
        os._exit(0)
    print(' ------------------ ( END ) \033[0;33;40m地区链接\033[0m ( ' + getTime() + ' ) ------------------\n\n\n')



# 获取地区链接信息
def getCountryLink(url, city, pcode, pname):
    page = getPageInfo(url, 'gbk')
    countrys = page.findAll(name = 'tr', attrs = {'class': re.compile('countytr')})
    countryLink = []
    for i in countrys:
        country = i.findAll(re.compile('a'))
        if len(country) > 0:
            countryUrl = ''
            for inx, k in enumerate(country):
                if inx == 0:
                    countryCode = k.text
                    if(countryUrl == '' and k['href']):
                        countryUrl = re.sub(url.rsplit('/', 1)[-1], k['href'], url)
                else:
                    countryName = k.text
        else:
            country = i.findAll(re.compile('td'))
            countryUrl = None
            for index, n in enumerate(country):
                if index == 0:
                    countryCode = n.text
                else:
                    countryName = n.text
        countryLink.append({
            'code': countryCode,
            'name': countryName,
            'url': countryUrl,
            'pcode': pcode,
            'pname': pname + ' - ' + city
        })
        if not countryDataList.__contains__(pcode):
            countryDataList[pcode] = []
        countryDataList[pcode].append({
            'code': countryCode,
            'name': countryName,
            'parent': pcode
        })
        print(' [ \033[0;33;40m' + pname + ' - ' + city + ' - ' + countryName + '\033[0m ] 数据获取成功\n')
    return countryLink



# 保存城镇链接信息
def saveTownLink():
    print(' ------------------ ( START ) \033[0;35;40m乡镇链接\033[0m ( ' + getTime() + ' ) ------------------\n')
    try:
        countryLinkFile = linkPath + countryFileName
        townLinkFile = linkPath + townFileName
        global totalNumber
        global townTotalNum
        with open(countryLinkFile, 'r', encoding = 'utf-8') as countryLinkFileHandler, open(townLinkFile, 'r+', encoding = 'utf-8') as townLinkFileHandler:
            data = json.load(townLinkFileHandler)
            if forceRefresh or len(data) <= 0:
                proxies = getRandomIp()
                print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n')
                countryLinkList = json.load(countryLinkFileHandler)
                towns = []
                for index, i in enumerate(countryLinkList):
                    if i['url'] != None:
                        print(' ------ 开始更新 [ \033[0;35;40m' + i['pname'] + ' - ' + i['name'] + '\033[0m ] ( ' + getTime() + ' ) ------\n')
                        townLinkList = getTownLink(i['url'], i['name'], i['pcode'], i['pname'])
                        for k in townLinkList:
                            towns.append(k)    
                        print(' ------ 完成更新 [ \033[0;35;40m' + i['pname'] + ' - ' + i['name'] + '\033[0m ] ( ' + getTime() + ' ) ------\n\n')
                        if index < len(countryLinkList):
                            proxies = getRandomIp()
                            print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n\n')
                townNumber = len(towns)
                townTotalNum += townNumber
                totalNumber += townNumber
                townLinkFileHandler.seek(0)
                saveJsonInfo(towns, townLinkFileHandler)
            else:
                totalNumber = totalNumber + len(data)
                print(' ( \033[0;33;40mNOTICE\033[0m ) 乡镇链接信息已存在，默认未设置强制更新 ( 可在代码内修改 forceRefresh 值 )\n')
        countryLinkFileHandler.close()
        townLinkFileHandler.close()
    except:
        traceback.print_exc()
        print(' \n( \033[0;31;40mERROR\033[0m ) 乡镇链接信息获取失败，强制终止继续执行 ( ' + getTime() + ' )\n')
        os._exit(0)
    print(' ------------------ ( END ) \033[0;35;40m乡镇链接\033[0m ( ' + getTime() + ' ) ------------------\n\n\n')



# 获取城镇链接信息
def getTownLink(url, country, pcode, pname):
    page = getPageInfo(url, 'gbk')
    towns = page.findAll(name = 'tr', attrs = {'class': re.compile('towntr')})
    townLink = []
    for i in towns:
        town = i.findAll(re.compile('a'))
        townUrl = ''
        townCode = ''
        townName = ''
        if len(town) > 0:
            for inx, k in enumerate(town):
                if inx == 0:
                    townCode = k.text
                    if k['href'] and townUrl == '':
                        townUrl = re.sub(url.rsplit('/', 1)[-1], k['href'], url)
                else:
                    townName = k.text
        else:
            town = i.findAll(re.compile('td'))
            townUrl = None
            for index, n in enumerate(town):
                if index == 0:
                    townCode = n.text
                else:
                    townName = n.text
        townName = townName.replace('办事处', '')
        townLink.append({
            'code': townCode,
            'name': townName,
            'url': townUrl,
            'pcode': pcode,
            'pname': pname + ' - ' + country
        })
        if not townDataList.__contains__(pcode):
            townDataList[pcode] = []
        townDataList[pcode].append({
            'code': townCode,
            'name': townName,
            'parent': pcode
        })
        print(' [ \033[0;35;40m' + pname + ' - ' + country + ' - ' + townName + '\033[0m ] 数据获取成功\n')
    return townLink



# 保存社区链接信息
def saveVillageLink():
    print(' ------------------ ( START ) \033[0;36;40m社区链接\033[0m ( ' + getTime() + ' ) ------------------\n')
    try:
        townLinkFile = linkPath + townFileName
        villageLinkFile = linkPath + villageFileName
        global totalNumber
        global villageTotalNum
        with open(townLinkFile, 'r', encoding = 'utf-8') as townLinkFileHandler, open(villageLinkFile, 'r+', encoding = 'utf-8') as villageLinkFileHandler:
            data = json.load(villageLinkFileHandler)
            if forceRefresh or len(data) <= 0:
                proxies = getRandomIp()
                print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n')
                townLinkList = json.load(townLinkFileHandler)
                villages = []
                for index, i in enumerate(townLinkList):
                    if i['url'] != None:
                        print(' ------ 开始更新 [ \033[0;36;40m' + i['pname'] + ' - ' + i['name'] + '\033[0m ] ( ' + getTime() + ' ) ------\n')
                        villageLinkList = getVillageLink(i['url'], i['name'], i['pcode'], i['pname'])
                        for k in villageLinkList:
                            villages.append(k)
                        print(' ------ 完成更新 [ \033[0;36;40m' + i['pname'] + ' - ' + i['name'] + '\033[0m ] ( ' + getTime() + ' ) ------\n\n')
                        if index < len(townLinkList):
                            proxies = getRandomIp()
                            print(' ( \033[0;33;40mNOTICE\033[0m ) 随机选取动态代理IP：\033[0;35;40m' + proxies['https'] + '\033[0m\n\n')
                villageNumber = len(villages)
                villageTotalNum += villageNumber
                totalNumber += villageNumber
                villageLinkFileHandler.seek(0)
                saveJsonInfo(villages, villageLinkFileHandler)
            else:
                totalNumber = totalNumber + len(data)
                print(' ( \033[0;33;40mNOTICE\033[0m ) 社区链接信息已存在，默认未设置强制更新 ( 可在代码内修改 forceRefresh 值 )\n')
        villageLinkFileHandler.close()
        townLinkFileHandler.close()
    except:
        traceback.print_exc()
        print(' \n( \033[0;31;40mERROR\033[0m ) 社区链接信息获取失败，强制终止继续执行 ( ' + getTime() + ' )\n')
        os._exit(0)
    print(' ------------------ ( END ) \033[0;36;40m社区链接\033[0m ( ' + getTime() + ' ) ------------------\n\n\n')



# 获取社区链接信息
def getVillageLink(url, town, pcode, pname):
    page = getPageInfo(url, 'gbk')
    villages = page.findAll(name = 'tr', attrs = {'class': re.compile('villagetr')})
    villageLink = []
    for i in villages:
        village = i.findAll(re.compile('td'))
        villageCode = ''
        villageName = ''
        for inx, n in enumerate(village):
            if inx == 0:
                villageCode = n.text
            elif inx == 2:
                villageName = n.text
        villageName = villageName.replace('居民委员会', '')
        villageName = villageName.replace('居委会', '')
        villageName = villageName.replace('民委员会', '')
        villageName = villageName.replace('委会', '')
        villageName = villageName.replace('村村', '村')
        villageName = villageName.replace('虚拟社区', '')
        villageLink.append({
            'code': villageCode,
            'name': villageName,
            'pcode': pcode,
            'pname': pname + ' - ' + town
        })
        if not villageDataList.__contains__(pcode):
            villageDataList[pcode] = []
        villageDataList[pcode].append({
            'code': villageCode,
            'name': villageName,
            'parent': pcode
        })
        print(' [ \033[0;36;40m' + pname + ' - ' + town + ' - ' + villageName + '\033[0m ] 数据获取成功\n')
    return villageLink
    



# 保存省份数据信息
def saveProvinceData():
    print(' ------------------ ( START ) 省份数据 ( ' + getTime() + ' ) ------------------\n')
    provinceDataFile = dataPath + provinceFileName
    cityLinkFile = linkPath + cityFileName
    provinceExistData = []
    with open(provinceDataFile, 'r+', encoding = 'utf-8') as provinceDataFileHandler, open(cityLinkFile, 'r', encoding = 'utf-8') as cityLinkFileHandler:
        cityLinkData = json.load(cityLinkFileHandler)
        if len(provinceDataList) <= 0 and len(cityLinkData) > 0:
            for i in cityLinkData:
                if i['pcode'] not in provinceExistData:
                    provinceExistData.append(i['pcode'])
                    provinceDataList.append({
                        'code': i['pcode'],
                        'name': i['pname']
                    })
            saveJsonInfo(provinceDataList, provinceDataFileHandler)
            print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(len(provinceDataList)) + ' 条省份数据保存成功 ( ' + provinceDataFile + ' )\n')
        elif len(provinceDataList) > 0:
            saveJsonInfo(provinceDataList, provinceDataFileHandler)
            print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(provinceTotalNum) + ' 条省份数据保存成功 ( ' + provinceDataFile + ' )\n')
        else:
            print(' ( \033[0;31;40mERROR\033[0m ) 省份数据缺失，请检查 ( ' + cityLinkFile + ' )\n')
    cityLinkFileHandler.close()
    provinceDataFileHandler.close()
    print(' ------------------ ( END ) 省份数据 ( ' + getTime() + ' ) ------------------\n\n\n')
    


# 保存城市数据信息
def saveCityData():
    print(' ------------------ ( START ) 城市数据 ( ' + getTime() + ' ) ------------------\n')
    cityDataNum = 0
    cityDataFile = dataPath + cityFileName
    cityLinkFile = linkPath + cityFileName
    try:
        with open(cityDataFile, 'r+', encoding = 'utf-8') as cityDataFileHandler, open(cityLinkFile, 'r', encoding = 'utf-8') as cityLinkFileHandler:
            cityLinkData = json.load(cityLinkFileHandler)
            if len(cityDataList) <= 0 and len(cityLinkData) > 0:
                for i in cityLinkData:
                    if not cityDataList.__contains__(i['pcode']):
                        cityDataList[i['pcode']] = []
                    cityDataList[i['pcode']].append({
                        'code': i['code'],
                        'name': i['name'],
                        'parent': i['pcode']
                    })
                    cityDataNum += 1
                saveJsonInfo(cityDataList, cityDataFileHandler)
                print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(cityDataNum) + ' 条城市数据保存成功 ( ' + cityDataFile + ' )\n')
            elif len(cityDataList) > 0:
                saveJsonInfo(cityDataList, cityDataFileHandler)
                print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(cityTotalNum) + ' 条城市数据保存成功 ( ' + cityDataFile + ' )\n')
            else:
                print(' ( \033[0;31;40mERROR\033[0m ) 城市数据缺失，请检查 ( ' + cityLinkFile + ' )\n')
        cityLinkFileHandler.close()
        cityDataFileHandler.close()
    except Exception as e:
        traceback.print_exc()
        print(' \n( \033[0;31;40mERROR\033[0m ) 城市数据保存失败，强制终止继续执行 ( ' + getTime() + ' )\n')
        os._exit(0)
    print(' ------------------ ( END ) 城市数据 ( ' + getTime() + ' ) ------------------\n\n')



# 保存地区数据信息
def saveCountryData():
    print(' ------------------ ( START ) 地区数据 ( ' + getTime() + ' ) ------------------\n')
    countryDataNum = 0
    countryDataFile = dataPath + countryFileName
    countryLinkFile = linkPath + countryFileName
    try:
        with open(countryDataFile, 'r+', encoding = 'utf-8') as countryDataFileHandler, open(countryLinkFile, 'r', encoding = 'utf-8') as countryLinkFileHandler:
            countryLinkData = json.load(countryLinkFileHandler)
            if len(countryDataList) <= 0 and len(countryLinkData) > 0:
                for i in countryLinkData:
                    if not countryDataList.__contains__(i['pcode']):
                        countryDataList[i['pcode']] = []
                    countryDataList[i['pcode']].append({
                        'code': i['code'],
                        'name': i['name'],
                        'parent': i['pcode']
                    })
                    countryDataNum += 1
                saveJsonInfo(countryDataList, countryDataFileHandler)
                print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(countryDataNum) + ' 条地区数据保存成功 ( ' + countryDataFile + ' )\n')
            elif len(countryDataList) > 0:
                saveJsonInfo(countryDataList, countryDataFileHandler)
                print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(countryTotalNum) + ' 条地区数据保存成功 ( ' + countryDataFile + ' )\n')
            else:
                print(' ( \033[0;31;40mERROR\033[0m ) 地区数据缺失，请检查 ( ' + countryLinkFile + ' )\n')
        countryLinkFileHandler.close()
        countryDataFileHandler.close()
    except Exception as e:
        traceback.print_exc()
        print(' \n( \033[0;31;40m\tERROR\033[0m ) 地区数据保存失败，强制终止继续执行 ( ' + getTime() + ' )\n')
        os._exit(0)
    print(' ------------------ ( END ) 地区数据 ( ' + getTime() + ' ) ------------------\n\n')


# 保存乡镇数据信息
def saveTownData():
    print(' ------------------ ( START ) 乡镇数据 ( ' + getTime() + ' ) ------------------\n')
    townDataNum = 0
    townDataFile = dataPath + townFileName
    townLinkFile = linkPath + townFileName
    try:
        with open(townDataFile, 'r+', encoding = 'utf-8') as townDataFileHandler, open(townLinkFile, 'r', encoding = 'utf-8') as townLinkFileHandler:
            townLinkData = json.load(townLinkFileHandler)
            if len(townDataList) <= 0 and len(townLinkData) > 0:
                for i in townLinkData:
                    if not townDataList.__contains__(i['pcode']):
                        townDataList[i['pcode']] = []
                    townDataList[i['pcode']].append({
                        'code': i['code'],
                        'name': i['name'],
                        'parent': i['pcode']
                    })
                    townDataNum += 1
                saveJsonInfo(townDataList, townDataFileHandler)
                print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(townDataNum) + ' 条乡镇数据保存成功 ( ' + townDataFile + ' )\n')
            elif len(townDataList) > 0:
                saveJsonInfo(townDataList, townDataFileHandler)
                print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(townTotalNum) + ' 条乡镇数据保存成功 ( ' + townDataFile + ' )\n')
            else:
                print(' ( \033[0;31;40mERROR\033[0m ) 乡镇数据缺失，请检查 ( ' + countryLinkFile + ' )\n')
        townLinkFileHandler.close()
        townDataFileHandler.close()
    except Exception as e:
        traceback.print_exc()
        print(' \n( \033[0;31;40m\tERROR\033[0m ) 乡镇数据保存失败，强制终止继续执行 ( ' + getTime() + ' )\n')
        os._exit(0)
    print(' ------------------ ( END ) 乡镇数据 ( ' + getTime() + ' ) ------------------\n\n')



# 保存街道数据信息
def saveVillageData():
    print(' ------------------ ( START ) 街道数据 ( ' + getTime() + ' ) ------------------\n')
    villageDataNum = 0
    villageDataFile = dataPath + villageFileName
    villageLinkFile = linkPath + villageFileName
    try:
        with open(villageDataFile, 'r+', encoding = 'utf-8') as villageDataFileHandler, open(villageLinkFile, 'r', encoding = 'utf-8') as villageLinkFileHandler:
            villageLinkData = json.load(villageLinkFileHandler)
            if len(villageDataList) <= 0 and len(villageLinkData) > 0:
                for i in villageLinkData:
                    if not villageDataList.__contains__(i['pcode']):
                        villageDataList[i['pcode']] = []
                    villageDataList[i['pcode']].append({
                        'code': i['code'],
                        'name': i['name'],
                        'parent': i['pcode']
                    })
                    villageDataNum += 1
                saveJsonInfo(villageDataList, villageDataFileHandler)
                print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(villageDataNum) + ' 条街道数据保存成功 ( ' + villageDataFile + ' )\n')
            elif len(villageDataList) > 0:
                saveJsonInfo(villageDataList, villageDataFileHandler)
                print(' ( \033[0;32;40mWONDERFUL\033[0m ) ' + str(villageTotalNum) + ' 条街道数据保存成功 ( ' + villageDataFile + ' )\n')
            else:
                print(' ( \033[0;31;40mERROR\033[0m ) 街道数据缺失，请检查 ( ' + countryLinkFile + ' )\n')
        villageLinkFileHandler.close()
        villageDataFileHandler.close()
    except Exception as e:
        traceback.print_exc()
        print(' \n( \033[0;31;40mERROR\033[0m ) 街道数据保存失败，强制终止继续执行 ( ' + getTime() + ' )\n')
        os._exit(0)
    print(' ------------------ ( END ) 街道数据 ( ' + getTime() + ' ) ------------------\n\n')



try:
    startTime = int(time.time())
    if openProxy:
        # 根据文件的修改时间来更新免费代理IP ( 大于5小时则更新 )
        ipFile = proxyPath + ipFileName
        with open(ipFile, 'r', encoding = 'utf-8') as ipFileHandler:
            ipData = json.load(ipFileHandler)
            ipFileMTime = int(os.path.getmtime(proxyPath + ipFileName))
            timeNow = int(time.time())
            if len(ipData) <= 0 or timeNow - ipFileMTime > 60 * 60 * 10:
                ipList = getIpList()
                saveDynamicIp(ipList)
        ipFileHandler.close()
        proxies = getRandomIp()
        if proxies != '':
            print(' ------------------ (START) 随机选取动态代理IP：' + proxies['https'] + ' (END) ------------------\n\n\n')
    else:
        print(' ------ 未开启代理 ( 需开启可在代码内修改 openProxy 值 ) ' + getTime() + ' ------\n\n\n')
    saveProvinceLink()
    saveCityLink()
    saveCountryLink()
    if level > 3:
        saveTownLink()
    if level > 4:
        saveVillageLink()
    saveProvinceData()
    saveCityData()
    saveCountryData()
    if level > 3:
        saveTownData()
    if level > 4:
        saveVillageData()
    endTime = int(time.time())
    totalSeconds = endTime - startTime
    proxySeconds = proxyEtime - proxyStime
    grabSeconds = totalSeconds - proxySeconds
    totalTime = str(datetime.timedelta(seconds = totalSeconds))
    grabTime = str(datetime.timedelta(seconds = grabSeconds))
    proxyTime = str(datetime.timedelta(seconds = proxySeconds))
    print(' ------------------ ( START ) 小结 ------------------\n')
    print(' 开始时间：' + time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime(startTime)) + '\n')
    print(' 结束时间：' + time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime(endTime)) + '\n')
    print(' 耗时总计：' + totalTime + '\n')
    print(' 更新代理：' + proxyTime + '\n')
    print(' 抓取时长：' + grabTime + '\n')
    print(' 数据总量：' + str(totalNumber) + '\n')
    print(' ------------------ ( END ) 小结 ------------------')
    os._exit(0)
except:
    print(' ------------------ 数据解析错误，脚本被迫终止，请稍候再试 ( ' + getTime() + ' ) ------------------\n')
    os._exit(0)
