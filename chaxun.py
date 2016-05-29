#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ 2016-05-25 21:06:32

import urllib, urllib2, cookielib
import re, os, string
from bs4 import BeautifulSoup
import sys
reload(sys)

baseUrl = 'http://10.23.5.5/'
codeUrl = 'CheckCode.aspx'
loginUrl = 'default2.aspx'
scoreUrl = 'xscj_gc.aspx'

def downImg(url):
    try:
        req = urllib2.Request(url)
        req = urllib2.urlopen(req)
        content = req.read()
        with open('yzm.gif','wb') as f:
            f.write(content)
    except Exception, e:
        print 'Error:', e

def setCookie():
    cookie = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    urllib2.install_opener(opener)
    opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1')]
    opener.open(baseUrl)
    return cookie

def login(username, password, cookie):
    """
    登录教务系统
    username:学号
    password:密码
    取得用户名和session_id
    """
    request = urllib2.Request(baseUrl)
    text = urllib2.urlopen(request).read()
    downImg(baseUrl + codeUrl)
    code = raw_input('请输入验证码:')
    soup = BeautifulSoup(text, 'html.parser')
    _VIEWSTATE = soup.find_all('input')[0].get('value')
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1',
        'Referer'    : baseUrl + loginUrl
    }
    postData = {
        '__VIEWSTATE' : _VIEWSTATE,
        'txtUserName' : username,
        'TextBox2' : password,
        'txtSecretCode' : code,
        'RadioButtonList1' : '学生',
        'Button1' : '',
        'lbLanguage' : '',
        'hidPdrs' : '',
        'hidsc' : '',
    }
    postData = urllib.urlencode(postData)
    request = urllib2.Request(baseUrl + loginUrl, postData, headers)
    response = urllib2.urlopen(request)
    text = response.read()
    # return text
    soup = BeautifulSoup(text, 'html.parser')
    if re.search(u'验证码不正确'.encode('gbk'), text):
        print '验证码错误'
        exit(1)
    elif re.search('<span id="xhxm">', text):
        result = {}
        name = soup.find(id = 'xhxm').string
        name = string.replace(name, u'同学', '')
        result['name'] = name
        session_id = cookie._cookies['10.23.5.5']['/']['ASP.NET_SessionId'].value
        result['session_id'] = session_id
        return result
    else:
        print '登录失败'
        exit(1)

def getScore(username, name, session_id, ddlXN, ddlXQ):
    """
    获取成绩
    username:学号
    ddlXN:2014-2015学年
    ddlXQ:1学期
    """
    url = baseUrl + scoreUrl + '?xh=' + str(username) + '&xm=' + name.encode('UTF-8') + '&gnmkdm=N121605'
    headers = {
        'Referer' : baseUrl + '/xs_main.aspx?xh=' + username,
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36',
        'Cookie' : 'ASP.NET_SessionId=' + session_id
    }
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    text = response.read().decode('gbk','ignore')
    soup = BeautifulSoup(text, 'html.parser')
    academy = soup.find(id = 'Label6').string
    academy = string.replace(academy, u'学院：', '')
    major = soup.find(id = 'Label7').string
    classes = soup.find(id = 'Label8').string
    classes = string.replace(classes, u'行政班：', '')
    _VIEWSTATE = soup.find_all('input')[0].get('value')
    print academy
    print major
    print classes
    headers = {
        'Referer'    : url,
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36',
        'Cookie' : 'ASP.NET_SessionId=' + session_id
    }
    postData = {
        'Button1' : '按学期查询',
        '__VIEWSTATE' : _VIEWSTATE,
        'ddlXN' : ddlXN,
        'ddlXQ' : ddlXQ,
    }
    postData = urllib.urlencode(postData)
    request = urllib2.Request(url, postData, headers)
    response = urllib2.urlopen(request)
    text = response.read()
    soup = BeautifulSoup(text.decode('gbk','ignore'), 'html.parser')
    datagrid = soup.find(id = 'Datagrid1')
    trs = datagrid.find_all('tr')
    length =  trs.__len__()
    for i in range(length):
        tds = trs[i].find_all('td')
        # print '课程名：%s 成绩：%s' % (tds[3].string.encode('gbk'), tds[8].string)
        print tds[3].string, tds[8].string


if __name__ == '__main__':
    cookie = setCookie()
    username = raw_input('请输入你的学号：')
    password = raw_input('请输入你的密码：')
    result = login(username, password, cookie)
    name = result['name']
    print name
    session_id = result['session_id']
    ddlXN = raw_input('请输入学年：')
    ddlXQ = raw_input('请输入学期：')
    getScore(username, name, session_id, ddlXN, ddlXQ)

